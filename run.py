import time
import os
import importlib
import copy
from lib.queue.queue import Queue
from lib.model.model import Model

queue = Queue.create()

model = Model.create()

while True:
    messages = queue.receive_messages()
    responses = model.respond(copy.deepcopy(messages))
    for message, response in zip(messages, responses):
        queue.respond(response)
        queue.delete_message(message)
