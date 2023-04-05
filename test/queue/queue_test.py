import os
import unittest
from unittest.mock import MagicMock, patch

from lib.queue.queue import Queue

class TestQueue(unittest.TestCase):
    def setUp(self):
        self.queue = Queue('input', batch_size=2, output_queue_name='output')
    
    def test_get_output_queue_name(self):
        self.assertEqual(self.queue.get_output_queue_name(), 'output-output')
        self.assertEqual(self.queue.get_output_queue_name('new-output'), 'new-output')
    
    def test_create(self):
        sqs_queue = Queue.create('sqs.SQSQueue', 'input', 'output', 2)
        self.assertIsInstance(sqs_queue, SQSQueue)
        redis_queue = Queue.create('redis.RedisQueue', 'input', 'output', 2)
        self.assertIsInstance(redis_queue, RedisQueue)
        with self.assertRaises(AttributeError):
            Queue.create('invalidqueue', 'input', 'output', 2)
    
    def test_process_messages(self):
        self.queue.receive_messages = MagicMock(return_value=['msg1', 'msg2'])
        self.queue.respond = MagicMock(return_value=None)
        self.queue.send_message = MagicMock(return_value=None)
        self.queue.process_messages()
        self.queue.receive_messages.assert_called_once_with(2)
        self.queue.respond.assert_called_with('msg1')
        self.queue.send_message.assert_called_with(None)

if __name__ == '__main__':
    unittest.main()