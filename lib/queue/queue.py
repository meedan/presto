import json
from typing import List, Dict, Tuple
import os

import boto3
import botocore

from lib.helpers import get_environment_setting
from lib.logger import logger
from lib import schemas
SQS_MAX_BATCH_SIZE = 10
class Queue:
    def __init__(self):
        """
        Start a specific queue - must pass input_queue_name.
        """
        self.sqs = self.get_sqs()

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
        return [queue for queue in queues if suffix and self.queue_name(queue).endswith(suffix)]

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
        return self.sqs.create_queue(
            QueueName=queue_name,
            Attributes=attributes
        )

    def get_or_create_queues(self, queue_name: str) -> List[boto3.resources.base.ServiceResource]:
        """
        Initialize all queues for the given worker - try to create them if they are not found by name for whatever reason
        """
        try:
            found_queues = [q for q in self.sqs.queues.filter(QueueNamePrefix=queue_name)]
            exact_match_queues = [queue for queue in found_queues if queue.attributes['QueueArn'].split(':')[-1] == queue_name]
            logger.info(f"found queues are {found_queues}")
            logger.info(f"exact queues are {exact_match_queues}")
            if exact_match_queues:
                return exact_match_queues
            else:
                return [self.create_queue(queue_name)]
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "AWS.SimpleQueueService.NonExistentQueue":
                return [self.create_queue(queue_name)]
            else:
                raise

    def get_sqs(self) -> boto3.resources.base.ServiceResource:
        """
        Get an instantiated SQS - if local, use local alternative via elasticmq
        """
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

    def group_deletions(self, messages_with_queues: List[Tuple[schemas.Message, boto3.resources.base.ServiceResource]]) -> Dict[boto3.resources.base.ServiceResource, List[schemas.Message]]:
        """
        Group deletions so that we can run through a simplified set of batches rather than delete each item independently
        """
        queue_to_messages = {}
        for message, queue in messages_with_queues:
            if queue not in queue_to_messages:
                queue_to_messages[queue] = []
            queue_to_messages[queue].append(message)
        return queue_to_messages
    
    def delete_messages(self, messages_with_queues: List[Tuple[schemas.Message, boto3.resources.base.ServiceResource]]) -> None:
        """
        Delete messages as we process them so other processes don't pick them up.
        SQS deals in max batches of 10, so break up messages into groups of 10
        when deleting them.
        """
        for queue, messages in self.group_deletions(messages_with_queues).items():
            self.delete_messages_from_queue(queue, messages)


    def delete_messages_from_queue(self, queue: boto3.resources.base.ServiceResource, messages: List[schemas.Message]) -> None:
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

    def receive_messages(self, batch_size: int = 1) -> List[Tuple[schemas.Message, boto3.resources.base.ServiceResource]]:
        """
        Pull batch_size messages from input queue.
        Actual SQS logic for pulling batch_size messages from matched queues
        """
        messages_with_queues = []
        for queue in self.input_queues:
            if batch_size <= 0:
                break
            batch_messages = queue.receive_messages(MaxNumberOfMessages=min(batch_size, SQS_MAX_BATCH_SIZE))
            for message in batch_messages:
                if batch_size > 0:
                    messages_with_queues.append((message, queue))
                    batch_size -= 1
        return messages_with_queues

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
