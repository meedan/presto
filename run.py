import time
import os
import importlib
from lib.queue.queue import Queue
from lib.model.model import Model

queue = Queue.create()

model = Model.create()

print("Beginning fingerprinter loop...")
while True:
    queue.fingerprint(model)
