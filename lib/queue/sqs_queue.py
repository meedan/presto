import boto3

from lib.queue.queue import Queue

class SQSQueue(Queue):
    def __init__(self, input_queue_name, output_queue_name, batch_size):
        self.sqs = boto3.resource('sqs')
        self.input_queue = self.sqs.get_queue_by_name(QueueName=input_queue_name)
        self.output_queue = self.sqs.get_queue_by_name(QueueName=output_queue_name)
        super().__init__(input_queue_name, output_queue_name, batch_size)

    def return_response(self, message):
        self.output_queue.send_message(MessageBody=message)

    def receive_messages(self, batch_size=1):
        messages = self.input_queue.receive_messages(MaxNumberOfMessages=batch_size)
        return messages
