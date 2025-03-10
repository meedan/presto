from typing import List
import json
from datetime import datetime
import requests

from lib import schemas
from lib.logger import logger
from lib.queue.queue import Queue
from lib.sentry import capture_custom_message

class QueueProcessor(Queue):
    @classmethod
    def create(cls, model_name: str = None, batch_size: int = 10):
        """
        Instantiate a queue. Must pass input_queue_name, output_queue_name, and batch_size.
        Pulls settings and then inits instance.
        """
        input_queue_name = Queue.get_output_queue_name(model_name)
        logger.info(f"Starting queue with: ('{input_queue_name}', {batch_size})")
        return QueueProcessor(input_queue_name, batch_size)

    def __init__(
        self, input_queue_name: str, output_queue_name: str = None, batch_size: int = 1
    ):
        """
        Start a specific queue - must pass input_queue_name - optionally pass output_queue_name, batch_size.
        """
        super().__init__()
        self.input_queue_name = input_queue_name
        self.input_queues = self.restrict_queues_to_suffix(
            self.get_or_create_queue(input_queue_name), Queue.get_queue_suffix()
        )
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
            bodies = [
                json.loads(message.body)
                for message, queue in messages_with_queues
            ]
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
            schemas.parse_output_message(message)  # will raise exceptions if not valid, e.g. too large of a message
            callback_url = message.get("body", {}).get("callback_url")
            start_time = datetime.now()
            response = requests.post(
                callback_url,
                timeout=30,
                json=message,
                # headers={"Content-Type": "application/json"},
            )
            if response.ok != True:
                capture_custom_message(f"Callback response not ok: error code {response.status_code}", 'error', {"status_code": response.status_code, "response": response, "callback_url": callback_url})
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            capture_custom_message("Presto callback failure", 'error', {"error": e, "callback_url": callback_url, "message": message, "duration": duration})
