from typing import Any, Dict, List
import boto3

from lib.queue.queue import Queue

class SQSQueue(Queue):
    def __init__(self, input_queue_name: str, output_queue_name: str, batch_size: int):
        """
        Initialize SQS queue - requires string names for intput / output queues,
        and batch_size to determine number of messages to pull off queue at each pull.
        """
        self.sqs = boto3.resource('sqs')
        self.input_queue = self.sqs.get_queue_by_name(QueueName=input_queue_name)
        self.output_queue = self.sqs.get_queue_by_name(QueueName=output_queue_name)
        super().__init__(input_queue_name, output_queue_name, batch_size)

    def receive_messages(self, batch_size: int = 1) -> List[Dict[str, Any]]:
        """
        Pull batch_size messages from input queue
        """
        messages = self.pop_message(self.input_queue, batch_size)
        return messages

    def pop_message(self, queue: boto3.resources.base.ServiceResource, batch_size: int = 1) -> List[Dict[str, Any]]:
        """
        Actual SQS logic for pulling batch_size messages from a queue
        """
        return queue.receive_messages(MaxNumberOfMessages=batch_size)
        
    def push_message(self, queue: boto3.resources.base.ServiceResource, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Actual SQS logic for pushing a message to a queue
        """
        queue.send_message(MessageBody=message)
        return message
    
