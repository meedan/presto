import os
import unittest
from unittest.mock import MagicMock, patch

from lib.queue.redis_queue import RedisQueue

class TestRedisQueue(unittest.TestCase):
    def setUp(self):
        self.mock_redis = MagicMock()
        self.queue = RedisQueue('input', 'output', batch_size=2)
        self.queue.redis = self.mock_redis
    
    def test_receive_messages(self):
        self.mock_redis.lpop.side_effect = [b'msg1', b'msg2', None]
        messages = self.queue.receive_messages()
        self.assertEqual(messages, ['msg1', 'msg2'])
    
    def test_delete_message(self):
        self.queue.delete_message('message')
        self.mock_redis.lrem.assert_called_with('output', 0, 'message')
    
    def test_respond(self):
        self.mock_redis.rpush.return_value = None
        self.queue.respond('response')
        self.mock_redis.rpush.assert_called_with('output', 'response')

if __name__ == '__main__':
    unittest.main()