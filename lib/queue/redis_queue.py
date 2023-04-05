import os
import redis

class RedisQueue(Queue):
    def __init__(self, input_queue_name, output_queue_name, batch_size=1):
        super().__init__(input_queue_name, output_queue_name, batch_size=batch_size)
        self.redis = redis.Redis(host=os.getenv("redis_host", "localhost"), port=os.getenv("redis_port", 6379), db=os.getenv("redis_db", 0))

    def receive_messages(self):
        messages = []
        for i in range(self.batch_size):
            message = self.redis.lpop(self.input_queue_name)
            if message:
                messages.append(message.decode())
            else:
                break
        return messages

    def receive_messages(self):
        return self.redis.lrange(self.queue_name, 0, -1)
    
    def delete_message(self, message):
        self.redis.lrem(self.queue_name, 0, message)

    def respond(self, response):
        self.redis.rpush(self.output_queue_name, response)