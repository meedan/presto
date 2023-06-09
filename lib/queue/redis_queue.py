from typing import Dict, List, Any
import os
import json

import redis

from lib.queue.queue import Queue

class RedisQueue(Queue):
    def __init__(self, input_queue_name: str, output_queue_name: str, batch_size: int):
        """
        Initialize Redis queue - requires string names for intput / output queues,
        and batch_size to determine number of messages to pull off queue at each pull.
        """
        self.redis = redis.Redis(host=os.getenv("REDIS_HOST", "redis"), port=os.getenv("REDIS_PORT", 6379), db=os.getenv("REDIS_DB", 0))
        self.input_queue = input_queue_name
        self.output_queue = output_queue_name
        super().__init__(input_queue_name, output_queue_name, batch_size)

    def receive_messages(self, batch_size: int = 1) -> List[Dict[str, Any]]:
        """
        Pull batch_size messages from input queue
        """
        messages = []
        for i in range(batch_size):
            raw_message = self.pop_message(self.input_queue_name)
            if raw_message:
                messages.append(json.loads(raw_message))
            else:
                break
        return messages

    def pop_message(self, queue: str):
        """
        Actual redis-specific logic for pulling batch_size messages from a queue
        """
        message = self.redis.lpop(queue)
        if message:
            return json.loads(message)
        
    def push_message(self, queue: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Actual redis-specific logic for pushing a message to a queue
        """
        self.redis.rpush(queue, json.dumps(message))
        return message
    
