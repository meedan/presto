import json
import os
import unittest
from unittest.mock import MagicMock, patch
from pydantic import BaseModel
import numpy as np

from lib.model.generic_transformer import GenericTransformerModel
from lib.queue.queue import Queue
from lib import schemas
class FakeSQSMessage(BaseModel):
    body: str
    receipt_handle: str

class TestQueue(unittest.TestCase):
    @patch('lib.queue.queue.boto3.resource')
    @patch('lib.helpers.get_environment_setting', return_value='us-west-1')
    def setUp(self, mock_get_env_setting, mock_boto_resource):
        self.model = GenericTransformerModel(None)
        self.mock_model = MagicMock()
        self.queue_name_input = 'test-input-queue'
        self.queue_name_output = 'test-output-queue'
        self.batch_size = 5

        # Mock the SQS resource and the queues
        self.mock_sqs_resource = MagicMock()
        self.mock_input_queue = MagicMock()
        self.mock_output_queue = MagicMock()

        self.mock_sqs_resource.get_queue_by_name.side_effect = [self.mock_input_queue, self.mock_output_queue]
        mock_boto_resource.return_value = self.mock_sqs_resource

        # Initialize the SQSQueue instance
        self.queue = Queue(self.queue_name_input, self.queue_name_output, self.batch_size)
    
    def test_get_output_queue_name(self):
        self.assertEqual(self.queue.get_output_queue_name('test'), 'test-output')
        self.assertEqual(self.queue.get_output_queue_name('test', 'new-output'), 'new-output')

    def test_fingerprint(self):
        self.queue.receive_messages = MagicMock(return_value=[(FakeSQSMessage(receipt_handle="blah", body=json.dumps({"body": {"id": 1, "callback_url": "http://example.com", "text": "This is a test"}})), self.mock_input_queue)])
        self.queue.input_queue = MagicMock(return_value=None)
        self.model.model = self.mock_model
        self.model.model.encode = MagicMock(return_value=np.array([[4, 5, 6], [7, 8, 9]]))
        self.queue.return_response = MagicMock(return_value=None)
        self.queue.fingerprint(self.model)
        self.queue.receive_messages.assert_called_once_with(1)

    def test_receive_messages(self):
        mock_queue1 = MagicMock()
        mock_queue1.receive_messages.return_value = [FakeSQSMessage(receipt_handle="blah", body=json.dumps({"body": {"id": 1, "callback_url": "http://example.com", "text": "This is a test"}}))]

        mock_queue2 = MagicMock()
        mock_queue2.receive_messages.return_value = [FakeSQSMessage(receipt_handle="blah", body=json.dumps({"body": {"id": 2, "callback_url": "http://example.com", "text": "This is another test"}}))]
        self.queue.input_queues = [mock_queue1, mock_queue2]
        received_messages = self.queue.receive_messages(self.batch_size)
    
        # Check if the right number of messages were received and the content is correct
        self.assertEqual(len(received_messages), 2)
        self.assertIn("a test", received_messages[0][0].body)
        self.assertIn("another test", received_messages[1][0].body)

    def test_restrict_queues_by_suffix(self):
        queues = [
            MagicMock(url='http://test.com/test_input'),
            MagicMock(url='http://test.com/test_input_output'),
            MagicMock(url='http://test.com/test_another_input')
        ]
        restricted_queues = self.queue.restrict_queues_by_suffix(queues, "_output")
        self.assertEqual(len(restricted_queues), 2)  # expecting two queues that don't end with _output

    def test_group_deletions(self):
        messages_with_queues = [
            (FakeSQSMessage(receipt_handle="blah", body=json.dumps({"body": "msg1"})), self.mock_input_queue),
            (FakeSQSMessage(receipt_handle="blah", body=json.dumps({"body": "msg2"})), self.mock_output_queue)
        ]
        grouped = self.queue.group_deletions(messages_with_queues)
        self.assertTrue(self.mock_input_queue in grouped)
        self.assertTrue(self.mock_output_queue in grouped)
        self.assertEqual(len(grouped[self.mock_input_queue]), 1)
        self.assertEqual(len(grouped[self.mock_output_queue]), 1)

    @patch('lib.queue.queue.logger.debug')
    def test_delete_messages_from_queue(self, mock_logger):
        mock_messages = [
            FakeSQSMessage(receipt_handle="r1", body=json.dumps({"body": "msg1"})),
            FakeSQSMessage(receipt_handle="r2", body=json.dumps({"body": "msg2"}))
        ]
        self.queue.delete_messages_from_queue(self.mock_input_queue, mock_messages)
        # Check if the correct number of calls to delete_messages were made
        self.mock_input_queue.delete_messages.assert_called_once()
        mock_logger.assert_called_with(f"Deleting message: {mock_messages[-1]}")

    def test_push_message(self):
        message_to_push = schemas.Message(body={"id": 1, "callback_url": "http://example.com", "text": "This is a test"})
        # Call push_message
        returned_message = self.queue.push_message(self.mock_output_queue, message_to_push)
        # Check if the message was correctly serialized and sent
        self.mock_output_queue.send_message.assert_called_once_with(MessageBody='{"body": {"id": "1", "callback_url": "http://example.com", "text": "This is a test"}, "response": null}')
        self.assertEqual(returned_message, message_to_push)

if __name__ == '__main__':
    unittest.main()