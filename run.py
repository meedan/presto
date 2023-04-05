import os
import importlib
from abc import ABC, abstractmethod
from lib.queue.queue import Queue
batch_map = {
    "indian_sbert": 100,
    "mean_tokens": 100,
    "fptg": 100,
    "video": 1,
    "audio": 1
}
queue = Queue.create(
    os.environ.get('QUEUE_TYPE'),
    os.environ.get('INPUT_QUEUE_NAME'),
    os.environ.get('OUTPUT_QUEUE_NAME'),
    batch_map.get(model_name, 1)
)

model = Model.create(
    os.environ.get('MODEL_NAME')
)

while True:
    messages = queue.receive_messages()
    responses = model.respond(messages)
    for message, response in zip(messages, resposnes):
        queue.respond(response)
        queue.delete_message(message)
