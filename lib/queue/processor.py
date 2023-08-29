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
        input_queue_name = get_setting(input_queue_name, "MODEL_NAME").replace(".", "__")
        logger.info(f"Starting queue with: ('{input_queue_name}', {batch_size})")
        return QueueProcessor(input_queue_name, batch_size)

    def __init__(self, input_queue_name: str, output_queue_name: str = None, batch_size: int = 1):
        """
        Start a specific queue - must pass input_queue_name - optionally pass output_queue_name, batch_size.
        """
        super().__init__()
        self.input_queue_name = input_queue_name
        self.input_queues = self.restrict_queues_by_suffix(self.get_or_create_queues(input_queue_name), "_output")
        self.all_queues = self.store_queue_map(self.input_queues)
        self.batch_size = batch_size

    def send_callbacks(self) -> List[schemas.Message]:
        """
        Main routine. Given a model, in a loop, read tasks from input_queue_name at batch_size depth,
        pass messages to model to respond (i.e. fingerprint) them, then pass responses to output queue.
        If failures happen at any point, resend failed messages to input queue.
        """
        messages_with_queues = self.receive_messages(self.batch_size)
        if messages_with_queues:
            logger.debug(f"About to respond to: ({messages_with_queues})")
            bodies = [schemas.Message(**json.loads(message.body)) for message, queue in messages_with_queues]
            for body in bodies:
                self.send_callback(body)
            self.delete_messages(messages_with_queues)


    def send_callback(self, body):
        """
        Rescue against failures when attempting to respond (i.e. fingerprint) from models.
        Return responses if no failure.
        """
        try:
            callback_url = body.get("callback_url")
            requests.post(callback_url, json=body)
        except Exception as e:
            logger.error(f"Callback fail! Failed with {e} on {callback_url} with body of {body}")