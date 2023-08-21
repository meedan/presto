import time
import os
import importlib
from lib.queue.queue import Queue
from lib.model.model import Model
from lib.logger import logger
queue = Queue.create()

model = Model.create()

logger.info("Beginning fingerprinter loop...")
while True:
    queue.fingerprint(model)
