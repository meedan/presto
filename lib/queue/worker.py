import pdb
import os
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import json
import boto3
from typing import List, Tuple
from lib import schemas
from lib.logger import logger
from lib.queue.queue import Queue, MAX_RETRIES
from lib.model.model import Model
from lib.sentry import capture_custom_message
from lib.helpers import get_environment_setting

TIMEOUT_SECONDS = int(os.getenv("WORK_TIMEOUT_SECONDS", "60"))

# Initialize CloudWatch client
cloudwatch = boto3.client('cloudwatch', region_name='us-west-2')

class QueueWorker(Queue):
    @classmethod
    def create(cls, model_name: str = None):
        """
        Instantiate a queue worker. Must pass input_queue_name.
        Pulls settings and then inits instance.
        """
        input_queue_name = Queue.get_input_queue_name(model_name)
        output_queue_name = Queue.get_output_queue_name(model_name)
        logger.info(f"Starting queue with: ('{input_queue_name}', '{output_queue_name}')")
        return QueueWorker(input_queue_name, output_queue_name)

    def __init__(self, input_queue_name: str, output_queue_name: str = None, dlq_queue_name: str = None):
        """
        Start a specific queue - must pass input_queue_name, optionally pass output_queue_name, dlq_queue_name.
        """
        super().__init__()
        self.input_queue_name = input_queue_name
        self.output_queue_name = output_queue_name or Queue.get_output_queue_name()
        self.dlq_queue_name = dlq_queue_name or Queue.get_dead_letter_queue_name()
        q_suffix = f"_output" + Queue.get_queue_suffix()
        dlq_suffix = f"_dlq" + Queue.get_queue_suffix()
        self.input_queues = self.restrict_queues_by_suffix(self.get_or_create_queues(input_queue_name), q_suffix)
        self.output_queues = self.get_or_create_queues(self.output_queue_name)
        self.dead_letter_queues = self.get_or_create_queues(self.dlq_queue_name)
        self.all_queues = self.store_queue_map([item for row in [self.input_queues, self.output_queues, self.dead_letter_queues] for item in row])
        logger.info(f"Worker listening to queues of {self.all_queues}")

    def process(self, model: Model):
        """
        Main routine. Given a model, in a loop, read tasks from input_queue_name,
        pass messages to model to respond (i.e. fingerprint) them, then pass responses to output queue.
        If failures happen at any point, resend failed messages to input queue.
        """
        responses = self.safely_respond(model)
        if responses:
            for response in responses:
                logger.info(f"Processing message of: ({response})")
                self.push_message(self.output_queue_name, response)

    def safely_respond(self, model: Model) -> List[schemas.Message]:
        """
        Rescue against failures when attempting to respond (i.e. fingerprint) from models.
        Return responses if no failure.
        """
        messages_with_queues = self.receive_messages(model.BATCH_SIZE)
        if not messages_with_queues:
            return []
        messages = self.extract_messages(messages_with_queues, model)
        responses, success = self.execute_with_timeout(model.respond, messages, timeout_seconds=TIMEOUT_SECONDS)
        if success:
            self.delete_processed_messages(messages_with_queues)
        else:
            self.increment_message_error_counts(messages_with_queues)
        return responses

    @staticmethod
    def extract_messages(messages_with_queues: List[Tuple], model: Model) -> List[schemas.Message]:
        """
        Extracts and transforms messages from a list of (message, queue) tuples into a list of Message schema objects.

        Parameters:
        - messages_with_queues (List[Tuple]): A list of tuples, each containing a message and its corresponding queue.

        Returns:
        - List[schemas.Message]: A list of Message objects ready for processing.
        """
        return [schemas.parse_message({**json.loads(message.body), **{"model_name": model.model_name}})
                for message, queue in messages_with_queues]

    @staticmethod
    def execute_with_timeout(func, args, timeout_seconds: int) -> List[schemas.Message]:
        """
        Executes a given hasher/fingerprinter with a specified timeout. If the hasher/fingerprinter execution time exceeds the timeout,
        logs an error and returns an empty list.

        Parameters:
        - func (callable): The function to execute.
        - args (any): The arguments to pass to the function.
        - timeout_seconds (int): The maximum number of seconds to wait for the function to complete.

        Returns:
        - List[schemas.Message]: The result of the function if it completes within the timeout, otherwise an empty list.
        """
        start_time = time.time()
        try:
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(func, args)
                result = future.result(timeout=timeout_seconds)
                execution_time = time.time() - start_time
                QueueWorker.log_execution_time(func.__name__, execution_time)
                return result, True
        except TimeoutError:
            error_message = "Model respond timeout exceeded."
            QueueWorker.log_and_handle_error(error_message)
            return [], False
        except Exception as e:
            QueueWorker.log_and_handle_error(str(e))
            return [], False

    @staticmethod
    def log_execution_time(func_name: str, execution_time: float):
        """
        Logs the execution time of a function to CloudWatch.

        Parameters:
        - func_name (str): The name of the function that was executed.
        - execution_time (float): The time taken to execute the function.
        """
        env_name = get_environment_setting("DEPLOY_ENV")
        logger.info(f"Function {func_name} executed in {execution_time:.2f} seconds.")
        cloudwatch.put_metric_data(
            Namespace='QueueWorkerMetrics',
            MetricData=[
                {
                    'MetricName': f'{env_name}_presto_{func_name}_ExecutionTime',
                    'Dimensions': [
                        {
                            'Name': 'FunctionName',
                            'Value': func_name
                        },
                    ],
                    'Unit': 'Seconds',
                    'Value': execution_time
                },
            ]
        )

    @staticmethod
    def log_and_handle_error(error):
        """
        Logs an error message to the system logger.

        Parameters:
        - error (Exception or str): The error to log, can be an Exception object or a string message.
        """
        logger.error(error)

    def delete_processed_messages(self, messages_with_queues: List[Tuple]):
        """
        Deletes messages from the queue after they have been processed.

        Parameters:
        - messages_with_queues (List[Tuple]): A list of tuples, each containing a message and its corresponding queue, to be deleted.
        """
        self.delete_messages(messages_with_queues)

    def increment_message_error_counts(self, messages_with_queues: List[Tuple]):
        """
        Increment the error count for messages and push them back to the queue or to the dead letter queue if retries exceed the limit.

        Parameters:
        - messages_with_queues (List[Tuple]): A list of tuples, each containing a message and its corresponding queue.
        """
        for message, queue in messages_with_queues:
            message_body = json.loads(message.body)
            retry_count = message_body.get('retry_count', 0) + 1

            if retry_count > MAX_RETRIES:
                logger.info(f"Message {message_body} exceeded max retries. Moving to DLQ.")
                capture_custom_message("Message exceeded max retries. Moving to DLQ.", 'info', {"message_body": message_body})
                self.push_to_dead_letter_queue(schemas.parse_message(message_body))
            else:
                updated_message = schemas.parse_message(message_body)
                updated_message.retry_count = retry_count
                queue.delete_messages(Entries=[self.delete_message_entry(message)])
                self.push_message(self.input_queue_name, updated_message)
