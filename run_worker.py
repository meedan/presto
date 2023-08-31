import time
import os
import importlib
from lib.queue.worker import QueueWorker
from lib.model.model import Model
from lib.logger import logger
queue = QueueWorker.create()

model = Model.create()

logger.info("Beginning work loop...")
while True:
    queue.process(model)
