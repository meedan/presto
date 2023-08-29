import time
import os
import importlib
from lib.queue.processor import QueueProcessor
from lib.model.model import Model
from lib.logger import logger
queue = QueueProcessor.create()

logger.info("Beginning callback loop...")
while True:
    queue.send_callbacks()