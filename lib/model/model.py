from abc import ABC, abstractmethod
import os

from lib.helpers import get_class

class Model(ABC):
    def respond(self, messages):
        return []
    
    @classmethod
    def create(cls, model_name):
        return get_class('lib.model.', model_name)()
