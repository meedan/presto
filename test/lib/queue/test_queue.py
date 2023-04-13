import os
import unittest
from unittest.mock import MagicMock, patch

from lib.queue.queue import Queue
from lib.queue.sqs_queue import SQSQueue
from lib.queue.redis_queue import RedisQueue

class TestQueue(unittest.TestCase):
    def setUp(self):
        self.queue = Queue('input', 'output', 2)
    
    def test_get_output_queue_name(self):
        self.assertEqual(self.queue.get_output_queue_name('test'), 'test-output')
        self.assertEqual(self.queue.get_output_queue_name('test', 'new-output'), 'new-output')
    
    def test_create(self):
        redis_queue = Queue.create('redis_queue.RedisQueue', 'zinput', 'output', 2)
        self.assertIsInstance(redis_queue, RedisQueue)
        with self.assertRaises(ModuleNotFoundError):
            Queue.create('invalidqueue', 'input', 'output', 2)
    
    def test_process_messages(self):
        self.queue.receive_messages = MagicMock(return_value=['msg1'])
        self.queue.respond = MagicMock(return_value=None)
        self.queue.send_message = MagicMock(return_value=None)
        self.queue.process_messages()
        self.queue.receive_messages.assert_called_once_with(2)
        self.queue.respond.assert_called_with('msg1')
        self.queue.send_message.assert_called_with(None)

if __name__ == '__main__':
    unittest.main()