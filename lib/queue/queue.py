import os
from abc import ABC

from lib.helpers import get_class
BATCH_MAP = {
    "indian_sbert.IndianSbert": 100,
    "mean_tokens.XlmRBertBaseNliStsbMeanTokens": 100,
    "fptg.MdebertaFilipino": 100,
    "video.VideoModel": 1,
    "audio.AudioModel": 1
}

class Queue(ABC):
    @classmethod
    def get_setting(cls, current_value, default_os_key):
        return current_value or os.environ.get(default_os_key)
        
    @classmethod
    def create(cls, queue_name=None, input_queue_name=None, output_queue_name=None, batch_size=None):
        queue_name = cls.get_setting(queue_name, "QUEUE_TYPE")
        input_queue_name = cls.get_setting(input_queue_name, "INPUT_QUEUE_NAME")
        output_queue_name = cls.get_setting(output_queue_name, "OUTPUT_QUEUE_NAME")
        return get_class('lib.queue.', queue_name)(input_queue_name, output_queue_name, batch_size)

    def __init__(self, input_queue_name, output_queue_name, batch_size):
        self.input_queue_name = input_queue_name
        self.output_queue_name = self.get_output_queue_name(input_queue_name, output_queue_name)
        self.batch_size = batch_size or BATCH_MAP.get(os.environ.get('MODEL_NAME'), 10)

    def get_output_queue_name(self, input_queue_name, output_queue_name=None):
        if not output_queue_name:
            output_queue_name = f'{input_queue_name}-output'
        return output_queue_name

    def process_messages(self):
        messages = self.receive_messages(self.batch_size)
        for message in messages:
            response = self.respond(message)
            self.send_message(response)

    def add_message(self, message):
        pass

    def receive_messages(self):
        pass
    
    def delete_message(self, message):
        pass

