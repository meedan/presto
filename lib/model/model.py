from abc import ABC, abstractmethod
import os
import tempfile

from lib.helpers import get_class

class Model(ABC):
    BATCH_SIZE = 1
    def get_tempfile(self):
        return tempfile.NamedTemporaryFile()

    def respond(self, messages):
        return []
    
    @classmethod
    def create(cls):
        model = get_class('lib.model.', os.environ.get('MODEL_NAME'))
        return model()
