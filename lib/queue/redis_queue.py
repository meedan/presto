import os
import json

import redis

from lib.queue.queue import Queue

class RedisQueue(Queue):
    def __init__(self, input_queue_name, output_queue_name, batch_size):
        super().__init__(input_queue_name, output_queue_name, batch_size)
        self.redis = redis.Redis(host=os.getenv("REDIS_HOST", "redis"), port=os.getenv("REDIS_PORT", 6379), db=os.getenv("REDIS_DB", 0))

    def return_response(self, message):
        self.redis.rpush(self.output_queue_name, message)

    def receive_messages(self, batch_size=1):
        messages = []
        for i in range(batch_size):
            raw_message = self.redis.lpop(self.input_queue_name)
            if raw_message:
                messages.append(json.loads(raw_message))
            else:
                break
        return messages
