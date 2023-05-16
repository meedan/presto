import os
import unittest
from unittest.mock import MagicMock, patch
import numpy as np

from lib.model.generic_transformer import GenericTransformerModel
from lib.queue.queue import Queue
from lib.queue.sqs_queue import SQSQueue
from lib.queue.redis_queue import RedisQueue

class TestQueue(unittest.TestCase):
    def setUp(self):
        self.model = GenericTransformerModel(None)
        self.mock_model = MagicMock()
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
        self.queue.receive_messages = MagicMock(return_value=[{"text": 'msg1'}])
        self.model.model = self.mock_model
        self.model.model.encode = MagicMock(return_value=np.array([[4, 5, 6], [7, 8, 9]]))
        self.queue.return_response = MagicMock(return_value=None)
        self.queue.process_messages(self.model)
        self.queue.receive_messages.assert_called_once_with(1)
        self.queue.return_response.assert_called_with({'request': {'text': 'msg1'}, 'response': {'text': 'msg1', 'response': [4, 5, 6]}})

if __name__ == '__main__':
    unittest.main()