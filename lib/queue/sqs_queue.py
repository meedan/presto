import json
from typing import Any, Dict, List
import boto3

from lib.queue.queue import Queue
from lib.helpers import get_environment_setting

class SQSQueue(Queue):
    def __init__(self, input_queue_name: str, output_queue_name: str, batch_size: int):
        """
        Initialize SQS queue - requires string names for intput / output queues,
        and batch_size to determine number of messages to pull off queue at each pull.
        """
        super().__init__(input_queue_name, output_queue_name, batch_size)

