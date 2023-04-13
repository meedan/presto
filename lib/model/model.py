from abc import ABC, abstractmethod
import os
import importlib

class Model(ABC):
    def respond(self, messages):
        return []
    
    @classmethod
    def create(cls, model_name):
        module_name, class_name = model_name.rsplit('.', 1)
        module = importlib.import_module(module_name)
        model_class = getattr(module, class_name)
        return model_class()