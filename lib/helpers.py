from typing import Any
import importlib

def get_class(prefix, class_name: str) -> Any:
    module = prefix+str.join(".", class_name.split('.')[:-1])
    module_obj = importlib.import_module(module)
    return getattr(module_obj, class_name.split('.')[-1])
    