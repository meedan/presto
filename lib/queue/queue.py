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
        Instantiate a queue. Must pass queue_driver_name (i.e. sqs_queue.SQSQueue vs redis_queue.RedisQueue), 
        input_queue_name, output_queue_name, and batch_size. Pulls settings and then inits instance.
        """
        input_queue_name = get_setting(input_queue_name, "INPUT_QUEUE_NAME")
        output_queue_name = get_setting(output_queue_name, "OUTPUT_QUEUE_NAME")
        logger.info(f"Starting queue with: ('{input_queue_name}', '{output_queue_name}', {batch_size})")
        return Queue(input_queue_name, output_queue_name, batch_size)

    def get_or_create_queue(self, queue_name):
        try:
            return self.sqs.get_queue_by_name(QueueName=queue_name)
        except botocore.exceptions.ClientError as e:
            logger.info(f"Queue {queue_name} doesn't exist - creating")
            if e.response['Error']['Code'] == "AWS.SimpleQueueService.NonExistentQueue":
                return self.sqs.create_queue(QueueName=queue_name)
            else:
                raise

    def get_sqs(self):
        presto_env = get_environment_setting("PRESTO_ENV")
        if presto_env == "local":
            logger.info(f"Using ElasticMQ Interface")
            return boto3.resource('sqs',
                                  region_name=(get_environment_setting("AWS_DEFAULT_REGION") or 'eu-central-1'),
                                  endpoint_url=(get_environment_setting("ELASTICMQ_URI") or 'http://presto-elasticmq:9324'),
                                  aws_access_key_id=(get_environment_setting("AWS_ACCESS_KEY_ID") or 'x'),
                                  aws_secret_access_key=(get_environment_setting("AWS_SECRET_ACCESS_KEY") or 'x'))
        else:
            logger.info(f"Using SQS Interface")
            return boto3.resource('sqs', region_name=get_environment_setting("AWS_DEFAULT_REGION"))

    def __init__(self, input_queue_name: str, output_queue_name: str = None, batch_size: int = 1):
        """
        Start a specific queue - must pass input_queue_name - optionally pass output_queue_name, batch_size.
        """
        self.sqs = self.get_sqs()
        self.input_queue = self.get_or_create_queue(input_queue_name)
        self.output_queue = self.get_or_create_queue(output_queue_name)
        self.input_queue_name = input_queue_name
        self.batch_size = batch_size
        self.output_queue_name = self.get_output_queue_name(input_queue_name, output_queue_name)

    def get_output_queue_name(self, input_queue_name: str, output_queue_name: str = None):
        """
        If output_queue_name was empty or None, set name for queue.
        """
        if not output_queue_name:
            output_queue_name = f'{input_queue_name}-output'
        return output_queue_name

    def delete_messages(self, queue, messages):
        for message in messages:
            logger.info(f"Deleting message of {message}")
            queue.delete_messages(Entries=[
                {
                    'Id': message.receipt_handle,
                    'ReceiptHandle': message.receipt_handle
                }
            ])
            
    def safely_respond(self, model: Model) -> Tuple[List[Dict[str, str]], List[Dict[str, Any]]]:
        """
        Rescue against failures when attempting to respond (i.e. fingerprint) from models.
        Return responses if no failure.
        """
        messages = self.receive_messages(model.BATCH_SIZE)
        responses = []
        if messages:
            logger.info(f"About to respond to: ({messages})")
            responses = model.respond([schemas.Message(**json.loads(message.body)) for message in messages])
            self.delete_messages(self.input_queue, messages)
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

    def receive_messages(self, batch_size: int = 1) -> List[Dict[str, Any]]:
        """
        Pull batch_size messages from input queue
        """
        messages = self.pop_message(self.input_queue, batch_size)
        return messages

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
    
    def pop_message(self, queue: boto3.resources.base.ServiceResource, batch_size: int = 1) -> List[Dict[str, Any]]:
        """
        Actual SQS logic for pulling batch_size messages from a queue
        """
        messages = []
        logger.info("Grabbing message...")
        while batch_size > 0:
            this_batch_size = min(batch_size, self.batch_size)
            batch_messages = queue.receive_messages(MaxNumberOfMessages=this_batch_size)
            for message in batch_messages:
                messages.append(message)
            batch_size -= this_batch_size
        return messages
        
