import os
import unittest
from unittest.mock import MagicMock, patch

from lib.queue.sqs_queue import SQSQueue

class TestSQSQueue(unittest.TestCase):
    @patch.object(boto3, 'resource')
    def setUp(self, mock_resource):
        self.mock_sqs = MagicMock()
        mock_resource.return_value = self.mock_sqs
        self.queue = SQSQueue('input', output_queue_name='output', batch_size=2)
    
    def test_receive_messages(self):
        self.mock_sqs.get_queue_by_name.return_value.receive_messages.return_value = ['msg1', 'msg2']
        messages = self.queue.receive_messages()
        self.assertEqual(messages, ['msg1', 'msg2'])
    
    def test_delete_message(self):
        message = MagicMock()
        self.queue.delete_message(message)
        message.delete.assert_called_once()
    
    def test_respond(self):
        self.mock_sqs.get_queue_by_name.return_value.send_message.return_value = None
        self.queue.respond('response')
        self.mock_sqs.get_queue_by_name.assert_called_with(QueueName='output')
        self.mock_sqs.get_queue_by_name.return_value.send_message.assert_called_with(MessageBody='response')
    
if __name__ == '__main__':
    unittest.main()