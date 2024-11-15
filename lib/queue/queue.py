import json
from typing import List, Dict, Tuple
import os
import threading

import boto3
import botocore

from lib.helpers import get_environment_setting
from lib.logger import logger
from lib import schemas

SQS_MAX_BATCH_SIZE = int(os.getenv("SQS_MAX_BATCH_SIZE", "10"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "5"))

class Queue:
    _thread_local = threading.local()

    @staticmethod
    def get_sqs():
        """
        Thread-safe, lazy-initialized boto3 SQS resource per thread.
        """
        if not hasattr(Queue._thread_local, "sqs_resource"):
            deploy_env = get_environment_setting("DEPLOY_ENV")
            if deploy_env == "local":
                logger.info("Using ElasticMQ Interface")
                Queue._thread_local.sqs_resource = boto3.resource(
                    'sqs',
                    region_name=get_environment_setting("AWS_DEFAULT_REGION") or 'eu-central-1',
                    endpoint_url=get_environment_setting("ELASTICMQ_URI") or 'http://presto-elasticmq:9324',
                    aws_access_key_id=get_environment_setting("AWS_ACCESS_KEY_ID") or 'x',
                    aws_secret_access_key=get_environment_setting("AWS_SECRET_ACCESS_KEY") or 'x'
                )
            else:
                logger.info("Using SQS Interface")
                Queue._thread_local.sqs_resource = boto3.resource(
                    'sqs',
                    region_name=get_environment_setting("AWS_DEFAULT_REGION")
                )
        return Queue._thread_local.sqs_resource

    @staticmethod
    def get_queue_prefix():
        return (get_environment_setting("QUEUE_PREFIX") or "").replace(".", "__")

    @staticmethod
    def get_queue_suffix():
        return (get_environment_setting("QUEUE_SUFFIX") or "")

    @staticmethod
    def get_input_queue_name(model_name=None):
        name = model_name or get_environment_setting("MODEL_NAME").replace(".", "__")
        return Queue.get_queue_prefix()+name+Queue.get_queue_suffix()

    @staticmethod
    def get_output_queue_name(model_name=None):
        name = model_name or get_environment_setting("MODEL_NAME").replace(".", "__")
        return Queue.get_queue_prefix()+name+"_output"+Queue.get_queue_suffix()

    @staticmethod
    def get_dead_letter_queue_name(model_name=None):
        name = model_name or get_environment_setting("MODEL_NAME").replace(".", "__")
        return Queue.get_queue_prefix()+name+"_dlq"+Queue.get_queue_suffix()

    def store_queue_map(self, all_queues: List[boto3.resources.base.ServiceResource]) -> Dict[str, boto3.resources.base.ServiceResource]:
        """
        Store a quick lookup so that we dont loop through this over and over in other places.
        """
        queue_map = {}
        for queue in all_queues:
            queue_map[self.queue_name(queue)] = queue
        return queue_map

    def queue_name(self, queue: boto3.resources.base.ServiceResource) -> str:
        """
        Pull queue name from a given queue
        """
        return queue.url.split('/')[-1]

    def restrict_queues_to_suffix(self, queues: List[boto3.resources.base.ServiceResource], suffix: str) -> List[boto3.resources.base.ServiceResource]:
        """
        When plucking input queues, we want to omit any queues that are our paired suffix queues..
        """
        return [queue for queue in queues if not suffix or suffix and self.queue_name(queue).endswith(suffix)]

    def restrict_queues_by_suffix(self, queues: List[boto3.resources.base.ServiceResource], suffix: str) -> List[boto3.resources.base.ServiceResource]:
        """
        When plucking input queues, we want to omit any queues that are our paired suffix queues..
        """
        return [queue for queue in queues if not self.queue_name(queue).endswith(suffix)]

    def create_queue(self, queue_name: str) -> boto3.resources.base.ServiceResource:
        """
        Create queue by name - may not work in production owing to permissions - mostly a local convenience function
        """
        logger.info(f"Queue {queue_name} doesn't exist - creating")
        attributes = {}
        if queue_name.endswith('.fifo'):
            attributes['FifoQueue'] = 'true'
            # Optionally enable content-based deduplication for FIFO queues
            attributes['ContentBasedDeduplication'] = 'true'
            # Include other FIFO-specific attributes as needed
        return self.get_sqs().create_queue(
            QueueName=queue_name,
            Attributes=attributes
        )

    def get_or_create_queue(self, queue_name: str):
        """
        Retrieve or create a queue with the specified name.
        """
        try:
            return [self.get_sqs().get_queue_by_name(QueueName=queue_name)]
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "AWS.SimpleQueueService.NonExistentQueue":
                return [self.create_queue(queue_name)]
            else:
                raise

    def send_message(self, queue_name: str, message: schemas.Message):
        """
        Send a message to a specific queue.
        """
        queue = self.get_or_create_queue(queue_name)[0]
        message_data = {"MessageBody": json.dumps(message.dict())}
        if queue_name.endswith('.fifo'):
            message_data["MessageGroupId"] = message.body.id
        queue.send_message(**message_data)

    def group_deletions(self, messages_with_queues: List[Tuple[schemas.Message, boto3.resources.base.ServiceResource]]) -> Dict[boto3.resources.base.ServiceResource, List[schemas.Message]]:
        """
        Group deletions by queue.
        """
        queue_to_messages = {}
        for message, queue in messages_with_queues:
            if queue not in queue_to_messages:
                queue_to_messages[queue] = []
            queue_to_messages[queue].append(message)
        return queue_to_messages

    def delete_messages(self, messages_with_queues: List[Tuple[schemas.Message, boto3.resources.base.ServiceResource]]):
        """
        Delete messages in batch mode.
        """
        for queue, messages in self.group_deletions(messages_with_queues).items():
            logger.info(f"Deleting messages {messages}")
            self.delete_messages_from_queue(queue, messages)

    def delete_messages_from_queue(self, queue, messages: List[schemas.Message]):
        """
        Helper to delete a batch of messages from a specific queue.
        """
        for i in range(0, len(messages), 10):
            batch = messages[i:i + 10]
            entries = [{"Id": str(idx), "ReceiptHandle": message.receipt_handle} for idx, message in enumerate(batch)]
            queue.delete_messages(Entries=entries)

    def delete_message_entry(self, message: schemas.Message, idx: int = 0) -> Dict[str, str]:
        """
        Helper function to generate correct format of entry
        """
        return {
            'Id': str(idx),
            'ReceiptHandle': message.receipt_handle
        }

    def receive_messages(self, batch_size: int = 1):
        """
        Receive messages from a queue.
        """
        queue = self.get_or_create_queue(self.input_queue_name)[0]
        return [(m, self.input_queue_name) for m in queue.receive_messages(MaxNumberOfMessages=min(batch_size, SQS_MAX_BATCH_SIZE))]

    def find_queue_by_name(self, queue_name: str) -> boto3.resources.base.ServiceResource:
        """
        Search through queues to find the right one
        """
        return self.all_queues.get(queue_name)

    def push_message(self, queue_name: str, message: schemas.Message) -> schemas.Message:
        """
        Actual SQS logic for pushing a message to a queue
        """
        message_data = {"MessageBody": json.dumps(message.dict())}
        if queue_name.endswith('.fifo'):
            message_data["MessageGroupId"] = message.body.id
        self.find_queue_by_name(queue_name).send_message(**message_data)
        return message

    def push_to_dead_letter_queue(self, message: schemas.Message):
        """
        Push a message to the dead letter queue.
        """
        dlq_name = Queue.get_dead_letter_queue_name()
        self.push_message(dlq_name, message)