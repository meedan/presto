import json
from typing import Any, List, Dict, Tuple, Union
import os

import boto3
import botocore

from lib.helpers import get_class, get_setting, get_environment_setting
from lib.model.model import Model
from lib.logger import logger
from lib import schemas
class Queue:
    @classmethod
    def create(cls, input_queue_name: str = None, output_queue_name: str = None, batch_size: int = 10):
        """
        Instantiate a queue. Must pass input_queue_name, output_queue_name, and batch_size.
        Pulls settings and then inits instance.
        """
        input_queue_name = get_setting(input_queue_name, "MODEL_NAME").replace(".", "__")
        output_queue_name = output_queue_name or f"{input_queue_name}_output"
        logger.info(f"Starting queue with: ('{input_queue_name}', '{output_queue_name}', {batch_size})")
        return Queue(input_queue_name, output_queue_name, batch_size)

    def __init__(self, input_queue_name: str, output_queue_name: str = None, batch_size: int = 1):
        """
        Start a specific queue - must pass input_queue_name - optionally pass output_queue_name, batch_size.
        """
        self.sqs = self.get_sqs()
        self.input_queue_name = input_queue_name
        self.output_queue_name = self.get_output_queue_name(input_queue_name, output_queue_name)
        self.input_queues = self.restrict_queues_by_suffix(self.get_or_create_queues(input_queue_name), "_output")
        self.output_queues = self.get_or_create_queues(output_queue_name)
        self.batch_size = batch_size

    def restrict_queues_by_suffix(self, queues, suffix):
        """
        When plucking input queues, we want to omit any queues that are our paired suffix queues..
        """
        return [queue for queue in queues if not queue.url.split('/')[-1].endswith(suffix)]

    def get_or_create_queues(self, queue_name):
        try:
            return self.sqs.queues.filter(QueueNamePrefix=queue_name)
        except botocore.exceptions.ClientError as e:
            logger.info(f"Queue {queue_name} doesn't exist - creating")
            if e.response['Error']['Code'] == "AWS.SimpleQueueService.NonExistentQueue":
                return [self.sqs.create_queue(QueueName=queue_name)]
            else:
                raise

    def get_sqs(self):
        deploy_env = get_environment_setting("DEPLOY_ENV")
        if deploy_env == "local":
            logger.info(f"Using ElasticMQ Interface")
            return boto3.resource('sqs',
                                  region_name=(get_environment_setting("AWS_DEFAULT_REGION") or 'eu-central-1'),
                                  endpoint_url=(get_environment_setting("ELASTICMQ_URI") or 'http://presto-elasticmq:9324'),
                                  aws_access_key_id=(get_environment_setting("AWS_ACCESS_KEY_ID") or 'x'),
                                  aws_secret_access_key=(get_environment_setting("AWS_SECRET_ACCESS_KEY") or 'x'))
        else:
            logger.info(f"Using SQS Interface")
            return boto3.resource('sqs', region_name=get_environment_setting("AWS_DEFAULT_REGION"))

    def get_output_queue_name(self, input_queue_name: str, output_queue_name: str = None) -> str:
        """
        If output_queue_name was empty or None, set name for queue.
        """
        if not output_queue_name:
            output_queue_name = f'{input_queue_name}-output'
        return output_queue_name

    def group_deletions(self, messages_with_queues: List[Tuple[Dict[str, Any], boto3.resources.base.ServiceResource]]) -> Dict[boto3.resources.base.ServiceResource, List[Dict[str, Any]]]:
        """
        Group deletions so that we can run through a simplified set of batches rather than delete each item independently
        """
        queue_to_messages = {}
        for message, queue in messages_with_queues:
            if queue not in queue_to_messages:
                queue_to_messages[queue] = []
            queue_to_messages[queue].append(message)
        return queue_to_messages
    
    def delete_messages(self, messages_with_queues: List[Tuple[Dict[str, Any], boto3.resources.base.ServiceResource]]) -> None:
        """
        Delete messages as we process them so other processes don't pick them up.
        SQS deals in max batches of 10, so break up messages into groups of 10
        when deleting them.
        """
        for queue, messages in self.group_deletions(messages_with_queues).items():
            self.delete_messages_from_queue(queue, messages)


    def delete_messages_from_queue(self, queue: boto3.resources.base.ServiceResource, messages: List[Dict[str, Any]]) -> None:
        """
        Helper function to delete a group of messages from a specific queue.
        """
        for i in range(0, len(messages), 10):
            batch = messages[i:i + 10]
            entries = []
            for idx, message in enumerate(batch):
                logger.debug(f"Deleting message: {message}")
                entry = {
                    'Id': str(idx),
                    'ReceiptHandle': message.receipt_handle
                }
                entries.append(entry)
            queue.delete_messages(Entries=entries)

    def safely_respond(self, model: Model) -> Tuple[List[Dict[str, str]], List[Dict[str, Any]]]:
        """
        Rescue against failures when attempting to respond (i.e. fingerprint) from models.
        Return responses if no failure.
        """
        messages_with_queues = self.receive_messages(model.BATCH_SIZE)
        responses = []
        if messages_with_queues:
            logger.debug(f"About to respond to: ({messages_with_queues})")
            responses = model.respond([schemas.Message(**json.loads(message.body)) for message, queue in messages_with_queues])
            self.delete_messages(messages_with_queues)
        return responses

    def fingerprint(self, model: Model):
        """
        Main routine. Given a model, in a loop, read tasks from input_queue_name at batch_size depth,
        pass messages to model to respond (i.e. fingerprint) them, then pass responses to output queue.
        If failures happen at any point, resend failed messages to input queue.
        """
        responses = self.safely_respond(model)
        if responses:
            for response in responses:
                logger.info(f"Processing message of: ({response})")
                self.return_response(response)

    def receive_messages(self, batch_size: int = 1) -> List[Tuple[Dict[str, Any], boto3.resources.base.ServiceResource]]:
        """
        Pull batch_size messages from input queue.
        Actual SQS logic for pulling batch_size messages from matched queues
        """
        messages_with_queues = []
        for queue in self.input_queues:
            if batch_size <= 0:
                break
            this_batch_size = min(batch_size, self.batch_size)
            batch_messages = queue.receive_messages(MaxNumberOfMessages=this_batch_size)
            for message in batch_messages:
                if batch_size > 0:
                    messages_with_queues.append((message, queue))
                    batch_size -= 1
        return messages_with_queues

    def return_response(self, message: Dict[str, Any]):
        """
        Send message to output queue
        """
        return self.push_message(self.output_queue, message)
        
    def push_message(self, queue: boto3.resources.base.ServiceResource, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Actual SQS logic for pushing a message to a queue
        """
        queue.send_message(MessageBody=json.dumps(message.dict()))
        return message
