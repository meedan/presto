import os
import unittest
from unittest.mock import MagicMock, patch

from lib.queue.redis_queue import RedisQueue

class TestRedisQueue(unittest.TestCase):
    def setUp(self):
        self.mock_redis = MagicMock()
        self.queue = RedisQueue('input', 'output', 2)
        self.queue.redis = self.mock_redis
    
    def test_receive_messages(self):
        self.mock_redis.lpop.side_effect = [b'msg1', b'msg2', None]
        messages = self.queue.receive_messages()
        self.assertEqual(messages, ['msg1', 'msg2'])
    
    def test_respond(self):
        self.mock_redis.rpush.return_value = None
        self.queue.return_response('response')
        self.mock_redis.rpush.assert_called_with('output', 'response')

if __name__ == '__main__':
    unittest.main()