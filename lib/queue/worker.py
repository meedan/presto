import json
from typing import List
from lib import schemas
from lib.logger import logger
from lib.queue.queue import Queue
from lib.model.model import Model
from lib.helpers import get_setting
class QueueWorker(Queue):
    @classmethod
    def create(cls, input_queue_name: str = None):
        """
        Instantiate a queue worker. Must pass input_queue_name.
        Pulls settings and then inits instance.
        """
        queue_prefix = get_setting("", "QUEUE_PREFIX").replace(".", "__")
        input_queue_name = queue_prefix+get_setting(input_queue_name, "MODEL_NAME").replace(".", "__")
        output_queue_name = f"{input_queue_name}_output"
        logger.info(f"Starting queue with: ('{input_queue_name}', '{output_queue_name}')")
        return QueueWorker(input_queue_name, output_queue_name)

    def __init__(self, input_queue_name: str, output_queue_name: str = None):
        """
        Start a specific queue - must pass input_queue_name - optionally pass output_queue_name.
        """
        super().__init__()
        self.input_queue_name = input_queue_name
        self.input_queues = self.restrict_queues_by_suffix(self.get_or_create_queues(input_queue_name), "_output")
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
        responses = []
        if messages_with_queues:
            logger.debug(f"About to respond to: ({messages_with_queues})")
            try:
                responses = model.respond([schemas.Message(**json.loads(message.body)) for message, queue in messages_with_queues])
            except Exception as e:
                logger.error(e)
            self.delete_messages(messages_with_queues)
        return responses

