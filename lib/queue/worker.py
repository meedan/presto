import os
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import json
from typing import List, Tuple
from lib import schemas
from lib.logger import logger
from lib.queue.queue import Queue
from lib.model.model import Model
from lib.helpers import get_setting
TIMEOUT_SECONDS = int(os.getenv("WORK_TIMEOUT_SECONDS", "60"))
class QueueWorker(Queue):
    @classmethod
    def create(cls, input_queue_name: str = None):
        """
        Instantiate a queue worker. Must pass input_queue_name.
        Pulls settings and then inits instance.
        """
        input_queue_name = Queue.get_queue_name(input_queue_name)
        output_queue_name = Queue.get_output_queue_name(input_queue_name, None)
        logger.info(f"Starting queue with: ('{input_queue_name}', '{output_queue_name}')")
        return QueueWorker(input_queue_name, output_queue_name)

    def __init__(self, input_queue_name: str, output_queue_name: str = None):
        """
        Start a specific queue - must pass input_queue_name - optionally pass output_queue_name.
        """
        super().__init__()
        self.input_queue_name = input_queue_name
        q_suffix = f"_output" + Queue.get_queue_suffix()
        self.input_queues = self.restrict_queues_by_suffix(self.get_or_create_queues(input_queue_name), q_suffix) 
        if output_queue_name:
            self.output_queue_name = self.get_output_queue_name(input_queue_name, output_queue_name)
            self.output_queues = self.get_or_create_queues(output_queue_name)
        self.all_queues = self.store_queue_map([item for row in [self.input_queues, self.output_queues] for item in row])
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
        return [schemas.parse_message(**{**json.loads(message.body), **{"model_name": model.model_name}})
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
        try:
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(func, args)
                return future.result(timeout=timeout_seconds), True
        except TimeoutError:
            error_message = "Model respond timeout exceeded."
            QueueWorker.log_and_handle_error(error_message)
            return [], False
        except Exception as e:
            QueueWorker.log_and_handle_error(str(e))
            return [], False

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
