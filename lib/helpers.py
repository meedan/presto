import os
from typing import Any
import importlib
def get_environment_setting(os_key: str) -> str:
    """
    Get environment variable helper. Could be augmented with credential store if/when necessary.
    Default to blank string as any .get on environ will result in string, so better to not create a None raise error
    """
    return os.environ.get(os_key, "")

def get_setting(current_value: Any, default_os_key: str) -> Any:
    """
    Get settings either via current passed value or backup
    default value accessed via os environment, defined by default_os_key.
    """
    return current_value or get_environment_setting(default_os_key)

def get_class(prefix: str, class_name: str) -> Any:
    """
    Instantiate class from strings of prefix/class_name. Used to
    convert settings values to reference to actual classes
    """
    module = prefix+str.join(".", class_name.split('.')[:-1])
    module_obj = importlib.import_module(module)
    return getattr(module_obj, class_name.split('.')[-1])
    