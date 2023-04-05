import boto3
class SQSQueue(Queue):
    def __init__(self, input_queue_name, output_queue_name=None, batch_size=1):
        super().__init__(input_queue_name, output_queue_name, batch_size=batch_size)
        self.sqs = boto3.resource('sqs')
        self.input_queue = self.sqs.get_queue_by_name(QueueName=input_queue_name)
        self.output_queue = self.sqs.get_queue_by_name(QueueName=output_queue_name)

    def receive_messages(self):
        messages = self.input_queue.receive_messages(MaxNumberOfMessages=self.batch_size)
        return messages
    
    def receive_messages(self):
        return self.queue.receive_messages()
    
    def delete_message(self, message):
        message.delete()

    def respond(self, response):
        self.output_queue.send_message(MessageBody=response)
