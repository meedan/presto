import os
import unittest
from unittest.mock import MagicMock, patch

import boto3

from lib.queue.sqs_queue import SQSQueue

class TestSQSQueue(unittest.TestCase):
    @patch.object(boto3, 'resource')
    def setUp(self, mock_resource):
        self.mock_sqs = MagicMock()
        mock_resource.return_value = self.mock_sqs
        self.queue = SQSQueue('input', 'output', 2)
    
    def test_receive_messages(self):
        self.mock_sqs.get_queue_by_name.return_value.receive_messages.return_value = ['msg1', 'msg2']
        messages = self.queue.receive_messages()
        self.assertEqual(messages, ['msg1', 'msg2'])
    
    def test_respond(self):
        self.mock_sqs.get_queue_by_name.return_value.send_message.return_value = None
        self.queue.return_response('response')
        self.mock_sqs.get_queue_by_name.assert_called_with(QueueName='output')
        self.mock_sqs.get_queue_by_name.return_value.send_message.assert_called_with(MessageBody='response')
    
if __name__ == '__main__':
    unittest.main()