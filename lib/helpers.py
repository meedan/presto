from typing import Any
import importlib
def get_setting(current_value: Any, default_os_key: str):
    """
    Get settings either via current passed value or backup
    default value accessed via os environment, defined by default_os_key.
    """
    return current_value or os.environ.get(default_os_key)

def get_class(prefix: str, class_name: str) -> Any:
    """
    Instantiate class from strings of prefix/class_name. Used to
    convert settings values to reference to actual classes
    """
    module = prefix+str.join(".", class_name.split('.')[:-1])
    module_obj = importlib.import_module(module)
    return getattr(module_obj, class_name.split('.')[-1])
    