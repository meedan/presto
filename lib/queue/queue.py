from typing import Any, List, Dict, Tuple, Union
import copy
import os
from abc import ABC

from lib.helpers import get_class, get_setting
from lib.model.model import Model

class Queue(ABC):
    @classmethod
    def create(cls, input_queue_name: str = None, output_queue_name: str = None, queue_driver_name: str = None, batch_size: int = None):
        """
        Instantiate a queue. Must pass queue_driver_name (i.e. sqs_queue.SQSQueue vs redis_queue.RedisQueue), 
        input_queue_name, output_queue_name, and batch_size. Pulls settings and then inits instance.
        """
        input_queue_name = get_setting(input_queue_name, "INPUT_QUEUE_NAME")
        output_queue_name = get_setting(output_queue_name, "OUTPUT_QUEUE_NAME")
        return get_class('lib.queue.', get_setting(queue_driver_name, "QUEUE_TYPE"))(input_queue_name, output_queue_name, batch_size)

    def __init__(self, input_queue_name: str, output_queue_name: str = None, batch_size: int = 1):
        """
        Start a specific queue - must pass input_queue_name - optionally pass output_queue_name, batch_size.
        """
        self.input_queue_name = input_queue_name
        self.output_queue_name = self.get_output_queue_name(input_queue_name, output_queue_name)

    def get_output_queue_name(self, input_queue_name: str, output_queue_name: str = None):
        """
        If output_queue_name was empty or None, set name for queue.
        """
        if not output_queue_name:
            output_queue_name = f'{input_queue_name}-output'
        return output_queue_name

    def safely_respond(self, model: Model) -> Tuple[List[Dict[str, str]], List[Dict[str, Any]]]:
        """
        Rescue against failures when attempting to respond (i.e. fingerprint) from models.
        Return responses if no failure.
        """
        messages = self.receive_messages(model.BATCH_SIZE)
        try:
            responses = model.respond(copy.deepcopy(messages))
        except:
            responses = []
        return messages, responses

    def fingerprint(self, model: Model):
        """
        Main routine. Given a model, in a loop, read tasks from input_queue_name at batch_size depth,
        pass messages to model to respond (i.e. fingerprint) them, then pass responses to output queue.
        If failures happen at any point, resend failed messages to input queue.
        """
        messages, responses = self.safely_respond(model)
        if responses:
            for message, response in zip(messages, responses):
                try:
                    self.return_response({"request": message, "response": response})
                except:
                    self.reset_messages([message])
        else:
            for message in messages:
                self.reset_messages(messages)

    def reset_messages(self, messages: Union[List[Dict[str, str]], Dict[str, str]]):
        """
        If, for some reason, we were unable to process the messages, pass back to input queue 
        for another worker to give them a shot.
        """
        for message in messages:
            self.push_message(self.input_queue, message)

    def return_response(self, message: Dict[str, Any]):
        """
        Send message to output queue
        """
        return self.push_message(self.output_queue, message)
        
    def push_message(self, queue: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generic pass
        """
        return message
