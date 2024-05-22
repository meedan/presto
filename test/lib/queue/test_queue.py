import json
import os
import unittest
from unittest.mock import MagicMock, patch
import numpy as np
import time

from lib.model.generic_transformer import GenericTransformerModel
from lib.queue.queue import Queue
from lib.queue.worker import QueueWorker
from lib import schemas
from test.lib.queue.fake_sqs_message import FakeSQSMessage
from concurrent.futures import TimeoutError

class TestQueueWorker(unittest.TestCase):
    @patch('lib.queue.queue.boto3.resource')
    @patch('lib.helpers.get_environment_setting', return_value='us-west-1')
    def setUp(self, mock_get_env_setting, mock_boto_resource):#, mock_restrict_queues_by_suffix):
        self.model = GenericTransformerModel(None)
        self.model.model_name = "generic"
        self.mock_model = MagicMock()
        self.queue_name_input = Queue.get_input_queue_name()
        self.queue_name_output = Queue.get_output_queue_name()
        self.queue_name_dlq = Queue.get_dead_letter_queue_name()

        # Mock the SQS resource and the queues
        self.mock_sqs_resource = MagicMock()
        self.mock_input_queue = MagicMock()
        self.mock_input_queue.url = f"http://queue/{self.queue_name_input}"
        self.mock_input_queue.attributes = {"QueueArn": f"queue:{self.queue_name_input}"}
        self.mock_output_queue = MagicMock()
        self.mock_output_queue.url = f"http://queue/{self.queue_name_output}"
        self.mock_output_queue.attributes = {"QueueArn": f"queue:{self.queue_name_output}"}
        self.mock_dlq_queue = MagicMock()
        self.mock_dlq_queue.url = f"http://queue/{self.queue_name_dlq}"
        self.mock_dlq_queue.attributes = {"QueueArn": f"queue:{self.queue_name_dlq}"}
        self.mock_sqs_resource.queues.filter.return_value = [self.mock_input_queue, self.mock_output_queue, self.mock_dlq_queue]
        mock_boto_resource.return_value = self.mock_sqs_resource

        # Initialize the SQSQueue instance
        self.queue = QueueWorker(self.queue_name_input, self.queue_name_output, self.queue_name_dlq)

    def test_get_output_queue_name(self):
        self.assertEqual(self.queue.get_output_queue_name().replace(".fifo", ""), (self.queue.get_input_queue_name()+'_output').replace(".fifo", ""))

    def test_get_dead_letter_queue_name(self):
        self.assertEqual(self.queue.get_dead_letter_queue_name().replace(".fifo", ""), (self.queue.get_input_queue_name()+'_dlq').replace(".fifo", ""))

    @patch('lib.queue.worker.time.time', side_effect=[0, 1])
    @patch('lib.queue.worker.cloudwatch.put_metric_data')
    def test_execute_with_timeout_failure(self, mock_put_metric_data, mock_time, mock_log_error):
        def test_func(args):
            raise TimeoutError

        with patch('lib.queue.worker.QueueWorker.log_and_handle_error') as mock_log_error:
            responses, success = QueueWorker.execute_with_timeout(test_func, [], timeout_seconds=1)
            self.assertEqual(responses, [])
            self.assertFalse(success)
            mock_log_error.assert_called_once_with("Model respond timeout exceeded.")
            mock_put_metric_data.assert_called_once_with(
                Namespace='QueueWorkerMetrics',
                MetricData=[{
                    'MetricName': 'test_func_ExecutionTime',
                    'Dimensions': [{'Name': 'FunctionName', 'Value': 'test_func'}],
                    'Unit': 'Seconds',
                    'Value': 1
                }]
            )

    @patch('lib.queue.worker.time.time', side_effect=[0, 0.5])
    @patch('lib.queue.worker.cloudwatch.put_metric_data')
    def test_execute_with_timeout_success(self, mock_put_metric_data, mock_time, mock_log_error):
        def test_func(args):
            return ["response"]

        with patch('lib.queue.worker.QueueWorker.log_and_handle_error') as mock_log_error:
            responses, success = QueueWorker.execute_with_timeout(test_func, [], timeout_seconds=1)
            self.assertEqual(responses, ["response"])
            self.assertTrue(success)
            mock_log_error.assert_not_called()
            mock_put_metric_data.assert_called_once_with(
                Namespace='QueueWorkerMetrics',
                MetricData=[{
                    'MetricName': 'test_func_ExecutionTime',
                    'Dimensions': [{'Name': 'FunctionName', 'Value': 'test_func'}],
                    'Unit': 'Seconds',
                    'Value': 0.5
                }]
            )

    def test_process(self):
        self.queue.receive_messages = MagicMock(return_value=[(FakeSQSMessage(receipt_handle="blah", body=json.dumps({
            "body": {"id": 1, "callback_url": "http://example.com", "text": "This is a test"},
            "model_name": "generic"
        })), self.mock_input_queue)])
        self.queue.input_queue = MagicMock(return_value=None)
        self.model.model = self.mock_model
        self.model.model.encode = MagicMock(return_value=np.array([[4, 5, 6], [7, 8, 9]]))
        self.queue.return_response = MagicMock(return_value=None)
        self.queue.process(self.model)
        self.queue.receive_messages.assert_called_once_with(1)

    def test_receive_messages(self):
        mock_queue1 = MagicMock()
        mock_queue1.receive_messages.return_value = [FakeSQSMessage(receipt_handle="blah", body=json.dumps({"body": {"id": 1, "callback_url": "http://example.com", "text": "This is a test"}}))]

        mock_queue2 = MagicMock()
        mock_queue2.receive_messages.return_value = [FakeSQSMessage(receipt_handle="blah", body=json.dumps({"body": {"id": 2, "callback_url": "http://example.com", "text": "This is another test"}}))]
        self.queue.input_queues = [mock_queue1, mock_queue2]
        received_messages = self.queue.receive_messages(5)

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

    def test_restrict_queues_to_suffix(self):
        queues = [
            MagicMock(url='http://test.com/test_input'),
            MagicMock(url='http://test.com/test_input_output'),
            MagicMock(url='http://test.com/test_another_input')
        ]
        restricted_queues = self.queue.restrict_queues_to_suffix(queues, "_output")
        self.assertEqual(len(restricted_queues), 1)  # expecting one queue that ends with _output

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
        message_to_push = schemas.parse_message({"body": {"id": 1, "callback_url": "http://example.com", "text": "This is a test"}, "model_name": "mean_tokens__Model"})
        # Call push_message
        returned_message = self.queue.push_message(self.queue_name_output, message_to_push)
        # Check if the message was correctly serialized and sent
        self.mock_output_queue.send_message.assert_called_once_with(MessageBody='{"body": {"id": 1, "callback_url": "http://example.com", "url": null, "text": "This is a test", "raw": {}, "parameters": {}, "result": {"hash_value": null}}, "model_name": "mean_tokens__Model", "retry_count": 0}')
        self.assertEqual(returned_message, message_to_push)

    def test_push_to_dead_letter_queue(self):
        message_to_push = schemas.parse_message({"body": {"id": 1, "callback_url": "http://example.com", "text": "This is a test"}, "model_name": "mean_tokens__Model"})
        # Call push_to_dead_letter_queue
        self.queue.push_to_dead_letter_queue(message_to_push)
        # Check if the message was correctly serialized and sent to the DLQ
        self.mock_dlq_queue.send_message.assert_called_once_with(MessageBody='{"body": {"id": 1, "callback_url": "http://example.com", "url": null, "text": "This is a test", "raw": {}, "parameters": {}, "result": {"hash_value": null}}, "model_name": "mean_tokens__Model", "retry_count": 0}')

    def test_increment_message_error_counts_exceed_max_retries(self):
        message_body = {
            "body": {"id": 1, "callback_url": "http://example.com", "text": "This is a test"},
            "retry_count": 5,  # Already at max retries
            "model_name": "mean_tokens__Model"
        }
        fake_message = FakeSQSMessage(receipt_handle="blah", body=json.dumps(message_body))
        messages_with_queues = [(fake_message, self.mock_input_queue)]

        self.queue.push_to_dead_letter_queue = MagicMock()
        self.queue.push_message = MagicMock()

        self.queue.increment_message_error_counts(messages_with_queues)

        self.queue.push_to_dead_letter_queue.assert_called_once()
        self.queue.push_message.assert_not_called()

    def test_increment_message_error_counts_increment(self):
        message_body = {
            "body": {"id": 1, "callback_url": "http://example.com", "text": "This is a test"},
            "retry_count": 2,  # Less than max retries
            "model_name": "mean_tokens__Model"
        }
        fake_message = FakeSQSMessage(receipt_handle="blah", body=json.dumps(message_body))
        messages_with_queues = [(fake_message, self.mock_input_queue)]

        self.queue.push_to_dead_letter_queue = MagicMock()
        self.queue.push_message = MagicMock()

        self.queue.increment_message_error_counts(messages_with_queues)

        self.queue.push_to_dead_letter_queue.assert_not_called()
        self.queue.push_message.assert_called_once()

    def test_extract_messages(self):
        messages_with_queues = [
            (FakeSQSMessage(receipt_handle="blah", body=json.dumps({
                "body": {"id": "1", "text": "Test message 1", "callback_url": "http://example.com"},
                "model_name": "mean_tokens__Model"
            })), self.mock_input_queue),
            (FakeSQSMessage(receipt_handle="blah", body=json.dumps({
                "body": {"id": "2", "text": "Test message 2", "callback_url": "http://example.com"},
                "model_name": "mean_tokens__Model"
            })), self.mock_input_queue)
        ]
        extracted_messages = QueueWorker.extract_messages(messages_with_queues, self.model)
        self.assertEqual(len(extracted_messages), 2)
        self.assertIsInstance(extracted_messages[0].body, schemas.GenericItem)
        self.assertEqual(extracted_messages[0].body.text, "Test message 1")
        self.assertEqual(extracted_messages[1].body.text, "Test message 2")
        self.assertEqual(extracted_messages[0].model_name, "generic")

    @patch('lib.queue.worker.QueueWorker.log_and_handle_error')
    def test_execute_with_timeout_success(self, mock_log_error):
        def test_func(args):
            return ["response"]

        with patch('lib.queue.worker.time.time', side_effect=[0, 0.5]):  # Mocking time to simulate execution time
            with patch('lib.queue.worker.cloudwatch.put_metric_data') as mock_put_metric_data:
                responses, success = QueueWorker.execute_with_timeout(test_func, [], timeout_seconds=1)
                self.assertEqual(responses, ["response"])
                self.assertTrue(success)
                mock_log_error.assert_not_called()
                mock_put_metric_data.assert_called_once_with(
                    Namespace='QueueWorkerMetrics',
                    MetricData=[{
                        'MetricName': 'test_func_ExecutionTime',
                        'Dimensions': [{'Name': 'FunctionName', 'Value': 'test_func'}],
                        'Unit': 'Seconds',
                        'Value': 0.5
                    }]
                )

    @patch('lib.queue.worker.QueueWorker.log_and_handle_error')
    def test_execute_with_timeout_failure(self, mock_log_error):
        def test_func(args):
            raise TimeoutError

        with patch('lib.queue.worker.time.time', side_effect=[0, 1]):  # Mocking time to simulate execution time
            with patch('lib.queue.worker.cloudwatch.put_metric_data') as mock_put_metric_data:
                responses, success = QueueWorker.execute_with_timeout(test_func, [], timeout_seconds=1)
                self.assertEqual(responses, [])
                self.assertFalse(success)
                mock_log_error.assert_called_once_with("Model respond timeout exceeded.")
                mock_put_metric_data.assert_called_once_with(
                    Namespace='QueueWorkerMetrics',
                    MetricData=[{
                        'MetricName': 'test_func_ExecutionTime',
                        'Dimensions': [{'Name': 'FunctionName', 'Value': 'test_func'}],
                        'Unit': 'Seconds',
                        'Value': 1
                    }]
                )

    @patch('lib.queue.worker.logger.error')
    def test_log_and_handle_error(self, mock_logger_error):
        QueueWorker.log_and_handle_error("Test error")
        mock_logger_error.assert_called_once_with("Test error")

    @patch('lib.queue.worker.QueueWorker.delete_messages')
    def test_delete_processed_messages(self, mock_delete_messages):
        messages_with_queues = [
            (FakeSQSMessage(receipt_handle="blah", body="message 1"), self.mock_input_queue),
            (FakeSQSMessage(receipt_handle="blah", body="message 2"), self.mock_input_queue)
        ]
        self.queue.delete_processed_messages(messages_with_queues)
        mock_delete_messages.assert_called_once_with(messages_with_queues)

if __name__ == '__main__':
    unittest.main()
