import traceback
from typing import Union, List, Dict, Any
from abc import ABC, abstractmethod
import os
import tempfile

import urllib.request

from lib.helpers import get_class
from lib import schemas
from lib.cache import Cache
from lib.sentry import capture_custom_message
from lib.base_exception import PrestoBaseException
from lib.logger import logger


class Model(ABC):
    BATCH_SIZE = 1

    def __init__(self):
        self.model_name = os.environ.get("MODEL_NAME")

    def get_tempfile_for_url(self, url: str) -> str:
        """
        Loads a file based on specified URL into a named tempfile. 
        Do not allow the tempfile to be deleted- we manage that directly to 
        avoid unintended mid-process file loss.
        """
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        with open(temp_file.name, 'wb') as out_file:
            out_file.write(
                urllib.request.urlopen(
                    urllib.request.Request(
                        url,
                        headers={'User-Agent': 'Mozilla/5.0'}
                    )
                ).read()
            )
        return temp_file.name

    def get_tempfile(self) -> Any:
        """
        Get an immediately tossable file. Used for images only, which only needs the io bytes instead of a file.
        """
        return tempfile.NamedTemporaryFile()

    def process(self, messages: Union[List[schemas.Message], schemas.Message]) -> List[schemas.Message]:
        return []

    def handle_fingerprinting_error(self, e: Exception, response_code: int = 500) -> schemas.ErrorResponse:
        error_context = {"error": str(e)}
        for attr in ["__cause__", "__context__", "args", "__traceback__"]:
            if attr in dir(e):
                if attr == "__traceback__":
                    error_context[attr] = '\n'.join(traceback.format_tb(getattr(e, attr)))
                else:
                    error_context[attr] = getattr(e, attr)
        capture_custom_message("Error during fingerprinting for {self.model_name}", 'info', error_context)
        return schemas.ErrorResponse(error=str(e), error_details=error_context, error_code=response_code)

    def get_response(self, message: schemas.Message) -> schemas.GenericItem:  # TODO note: the return type is wrong here
        """
        Perform a lookup on the cache for a message, and if found, return that cached value.
        """
        result = Cache.get_cached_result(message.body.content_hash)
        if not result:
            try:
                result = self.process(message)
                Cache.set_cached_result(message.body.content_hash, result)
            except Exception as e:
                if isinstance(e, PrestoBaseException):
                    return self.handle_fingerprinting_error(e, e.error_code)
                else:
                    return self.handle_fingerprinting_error(e)
        return result

    def respond(self, messages: Union[List[schemas.Message], schemas.Message]) -> List[schemas.Message]:
        """
        Force messages as list of messages in case we get a singular item. Then, run fingerprint routine.
        """
        if not isinstance(messages, list):
            messages = [messages]
        for message in messages:
            message.body.result = self.get_response(message)
        return messages

    @classmethod
    def create(cls):
        """
        abstraction for loading model based on os environment-specified model.
        """
        model = get_class('lib.model.', os.environ.get('MODEL_NAME'))
        return model()
