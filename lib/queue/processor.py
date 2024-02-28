from typing import List
import json

import requests

from lib import schemas
from lib.logger import logger
from lib.helpers import get_setting
from lib.queue.queue import Queue
class QueueProcessor(Queue):
    @classmethod
    def create(cls, input_queue_name: str = None, batch_size: int = 10):
        """
        Instantiate a queue. Must pass input_queue_name, output_queue_name, and batch_size.
        Pulls settings and then inits instance.
        """
        input_queue_name = Queue.get_queue_name()
        logger.info(f"Starting queue with: ('{input_queue_name}', {batch_size})")
        return QueueProcessor(input_queue_name, batch_size)
    
    def __init__(self, input_queue_name: str, output_queue_name: str = None, batch_size: int = 1):
        """
        Start a specific queue - must pass input_queue_name - optionally pass output_queue_name, batch_size.
        """
        super().__init__()
        self.input_queue_name = input_queue_name
        q_suffix = f"_output" + Queue.get_queue_suffix()
        self.input_queues = self.restrict_queues_to_suffix(self.get_or_create_queues(input_queue_name+q_suffix), q_suffix)
        self.all_queues = self.store_queue_map(self.input_queues)
        logger.info(f"Processor listening to queues of {self.all_queues}")
        self.batch_size = batch_size
    
    def send_callbacks(self) -> List[schemas.Message]:
        """
        Main routine. Given a model, in a loop, read tasks from input_queue_name at batch_size depth,
        pass messages to model to respond (i.e. fingerprint) them, then pass responses to output queue.
        If failures happen at any point, resend failed messages to input queue.
        """
        messages_with_queues = self.receive_messages(self.batch_size)
        if messages_with_queues:
            logger.info(f"About to respond to: ({messages_with_queues})")
            bodies = [schemas.Message(**json.loads(message.body)) for message, queue in messages_with_queues]
            for body in bodies:
                self.send_callback(body)
            self.delete_messages(messages_with_queues)
    
    def send_callback(self, message):
        """
        Rescue against failures when attempting to respond (i.e. fingerprint) from models.
        Return responses if no failure.
        """
        logger.info(f"Message for callback is: {message}")
        try:
            callback_url = message.body.callback_url
            requests.post(callback_url, json=message.dict())
        except Exception as e:
            logger.error(f"Callback fail! Failed with {e} on {callback_url} with message of {message}")
