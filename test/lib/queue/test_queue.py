import os
import unittest
from unittest.mock import MagicMock, patch
import numpy as np

from lib.model.generic_transformer import GenericTransformerModel
from lib.queue.queue import Queue
from lib.queue.sqs_queue import SQSQueue
from lib.queue.redis_queue import RedisQueue
from lib import schemas

class TestQueue(unittest.TestCase):
    def setUp(self):
        self.model = GenericTransformerModel(None)
        self.mock_model = MagicMock()
        self.queue = Queue('input', 'output', 2)
    
    def test_get_output_queue_name(self):
        self.assertEqual(self.queue.get_output_queue_name('test'), 'test-output')
        self.assertEqual(self.queue.get_output_queue_name('test', 'new-output'), 'new-output')
    
    def test_create(self):
        redis_queue = Queue.create('zinput', 'output', 'redis_queue.RedisQueue', 2)
        self.assertIsInstance(redis_queue, RedisQueue)
        with self.assertRaises(ModuleNotFoundError):
            Queue.create('input', 'output', 'invalidqueue', 2)
    
    def test_fingerprint(self):
        self.queue.receive_messages = MagicMock(return_value=[schemas.TextInput(id="123", callback_url="http://example.com?callback=1", text="msg1")])
        self.queue.input_queue = MagicMock(return_value=None)
        self.model.model = self.mock_model
        self.model.model.encode = MagicMock(return_value=np.array([[4, 5, 6], [7, 8, 9]]))
        self.queue.return_response = MagicMock(return_value=None)
        self.queue.fingerprint(self.model)
        self.queue.receive_messages.assert_called_once_with(1)

if __name__ == '__main__':
    unittest.main()