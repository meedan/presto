from abc import ABC

from lib.helpers import get_class

class Queue(ABC):
    @classmethod
    def create(cls, queue_name, input_queue_name, output_queue_name, batch_size):
        return get_class('lib.queue.', queue_name)(input_queue_name, output_queue_name, batch_size)

    def __init__(self, input_queue_name, output_queue_name, batch_size):
        self.input_queue_name = input_queue_name
        self.output_queue_name = self.get_output_queue_name(input_queue_name, output_queue_name)
        self.batch_size = batch_size

    def get_output_queue_name(self, input_queue_name, output_queue_name=None):
        if not output_queue_name:
            output_queue_name = f'{input_queue_name}-output'
        return output_queue_name

    def process_messages(self):
        messages = self.receive_messages(self.batch_size)
        for message in messages:
            response = self.respond(message)
            self.send_message(response)

    def receive_messages(self):
        pass
    
    def delete_message(self, message):
        pass

