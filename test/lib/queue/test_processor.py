import unittest
from unittest.mock import MagicMock, patch
import json

from lib.queue.processor import QueueProcessor
from lib import schemas
from test.lib.queue.fake_sqs_message import FakeSQSMessage
class TestQueueProcessor(unittest.TestCase):

    @patch('lib.queue.queue.boto3.resource')
    @patch('lib.helpers.get_environment_setting', return_value='us-west-1')
    def setUp(self, mock_get_env_setting, mock_boto_resource):
        self.queue_name_input = 'mean_tokens__Model'

        # Mock the SQS resource and the queues
        self.mock_sqs_resource = MagicMock()
        self.mock_input_queue = MagicMock()
        self.mock_input_queue.url = "http://queue/mean_tokens__Model"
        self.mock_sqs_resource.get_queue_by_name.return_value = self.mock_input_queue
        mock_boto_resource.return_value = self.mock_sqs_resource

        # Initialize the QueueProcessor instance
        self.queue_processor = QueueProcessor(self.queue_name_input, batch_size=2)

    def test_send_callbacks(self):
        # Mocking necessary methods and creating fake data
        self.queue_processor.receive_messages = MagicMock(
            return_value=[(FakeSQSMessage(receipt_handle="blah", body=json.dumps({"body": {"callback_url": "http://example.com", "text": "This is a test", "id": 1, "result": {"hash_value": [1,2,3]}}, "model_name": "mean_tokens__Model"})), self.mock_input_queue)]
        )
        self.queue_processor.send_callback = MagicMock(return_value=None)
        self.queue_processor.delete_messages = MagicMock(return_value=None)

        responses = self.queue_processor.send_callbacks()

        self.queue_processor.receive_messages.assert_called_once_with(2)
        self.queue_processor.send_callback.assert_called()
        self.queue_processor.delete_messages.assert_called()

    @patch('lib.queue.processor.requests.post')
    def test_send_callback(self, mock_post):
        message_body = {"body": {"callback_url": "http://example.com", "text": "This is a test", "id": 123, "result": {"hash_value": [1,2,3]}}, "model_name": "mean_tokens__Model"}
        self.queue_processor.send_callback(message_body)
        mock_post.assert_called_once_with("http://example.com", timeout=30, json=message_body)

    @patch('lib.queue.processor.requests.post')
    def test_send_callback_failure(self, mock_post):
        mock_post.side_effect = Exception("Request Failed!")
        message_body = {"body": {"callback_url": "http://example.com", "text": "This is a test", "id": 123, "result": {"hash_value": [1,2,3]}}, "model_name": "mean_tokens__Model"}
        with self.assertLogs(level='ERROR') as cm:
            self.queue_processor.send_callback(message_body)
        self.assertIn("Failed with Request Failed! on http://example.com with message of", cm.output[0])

if __name__ == '__main__':
    unittest.main()
