import os
import json

import redis

from lib.queue.queue import Queue

class RedisQueue(Queue):
    def __init__(self, input_queue_name, output_queue_name, batch_size):
        self.redis = redis.Redis(host=os.getenv("REDIS_HOST", "redis"), port=os.getenv("REDIS_PORT", 6379), db=os.getenv("REDIS_DB", 0))
        self.input_queue = input_queue_name
        self.output_queue = output_queue_name
        super().__init__(input_queue_name, output_queue_name, batch_size)

    def return_response(self, message):
        self.push_message(self.output_queue_name, message)

    def pop_message(self, queue):
        return self.redis.lpop(queue)
        
    def push_message(self, queue, message):
        self.redis.rpush(queue, message)
        return message
    
    def receive_messages(self, batch_size=1):
        messages = []
        for i in range(batch_size):
            raw_message = self.pop_message(self.input_queue_name)
            if raw_message:
                messages.append(json.loads(raw_message))
            else:
                break
        return messages
