from abc import ABC
import importlib

class Queue(ABC):
    @classmethod
    def create(cls, queue_name, input_queue_name, output_queue_name, batch_size):
        module = 'lib.queue.'+str.join(".", queue_name.split('.')[:-1])
        queue_module = importlib.import_module(module)
        queue_class = getattr(queue_module, queue_name.split('.')[-1])
        return queue_class(input_queue_name, output_queue_name, batch_size)

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

