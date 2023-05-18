from typing import Any, List, Dict, Tuple, Union
import copy
import os
from abc import ABC

from lib.helpers import get_class
from lib.model.model import Model

class Queue(ABC):
    @classmethod
    def get_setting(cls, current_value: Any, default_os_key):
        return current_value or os.environ.get(default_os_key)
        
    @classmethod
    def create(cls, queue_name: str = None, input_queue_name: str = None, output_queue_name: str = None, batch_size: int = None):
        queue_name = cls.get_setting(queue_name, "QUEUE_TYPE")
        input_queue_name = cls.get_setting(input_queue_name, "INPUT_QUEUE_NAME")
        output_queue_name = cls.get_setting(output_queue_name, "OUTPUT_QUEUE_NAME")
        return get_class('lib.queue.', queue_name)(input_queue_name, output_queue_name, batch_size)

    def __init__(self, input_queue_name: str, output_queue_name: str, batch_size: int):
        self.input_queue_name = input_queue_name
        self.output_queue_name = self.get_output_queue_name(input_queue_name, output_queue_name)

    def get_output_queue_name(self, input_queue_name: str, output_queue_name: str = None):
        if not output_queue_name:
            output_queue_name = f'{input_queue_name}-output'
        return output_queue_name

    def safely_respond(self, model: Model) -> Tuple[List[Dict[str, str]], List[Dict[str, Any]]]:
        messages = self.receive_messages(model.BATCH_SIZE)
        try:
            responses = model.respond(copy.deepcopy(messages))
        except:
            responses = []
        return messages, responses

    def fingerprint(self, model: Model):
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
        for message in messages:
            self.push_message(self.input_queue, message)