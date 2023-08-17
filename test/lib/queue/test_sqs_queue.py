import unittest
from unittest.mock import patch, MagicMock
from lib.queue.sqs_queue import SQSQueue

class TestSQSQueue(unittest.TestCase):

    @patch('your_module.boto3.resource')
    @patch('your_module.get_environment_setting', return_value='us-west-1')
    def setUp(self, mock_get_env_setting, mock_boto_resource):
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
        self.sqs_queue = SQSQueue(self.queue_name_input, self.queue_name_output, self.batch_size)

    def test_receive_messages(self):
        mock_messages = [
            {"Body": "Test Message 1"},
            {"Body": "Test Message 2"},
        ]
        self.mock_input_queue.receive_messages.return_value = {'Messages': mock_messages}
        
        received_messages = self.sqs_queue.receive_messages(self.batch_size)

        # Check if the right number of messages were received and the content is correct
        self.assertEqual(len(received_messages), 2)
        self.assertIn("Test Message 1", received_messages)
        self.assertIn("Test Message 2", received_messages)

    def test_pop_message(self):
        mock_messages = [
            {"Body": "Test Message 3"},
            {"Body": "Test Message 4"},
        ]
        self.mock_input_queue.receive_messages.return_value = {'Messages': mock_messages}
        
        popped_messages = self.sqs_queue.pop_message(self.mock_input_queue, self.batch_size)

        # Check if the right number of messages were popped and the content is correct
        self.assertEqual(len(popped_messages), 2)
        self.assertIn("Test Message 3", popped_messages)
        self.assertIn("Test Message 4", popped_messages)

    def test_push_message(self):
        message_to_push = {"key": "value"}

        # Call push_message
        returned_message = self.sqs_queue.push_message(self.mock_output_queue, message_to_push)

        # Check if the message was correctly serialized and sent
        self.mock_output_queue.send_message.assert_called_once_with(MessageBody='{"key": "value"}')
        self.assertEqual(returned_message, message_to_push)

if __name__ == '__main__':
    unittest.main()
