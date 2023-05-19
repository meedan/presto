from typing import Union, List, Dict, Any
from abc import ABC, abstractmethod
import os
import tempfile

import urllib.request

from lib.helpers import get_class

class Model(ABC):
    BATCH_SIZE = 1
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

    def fingerprint(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        return []
        
    def respond(self, messages: Union[List[Dict[str, str]], Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Force messages as list of messages in case we get a singular item. Then, run fingerprint routine.
        """
        if not isinstance(messages, list):
            messages = [messages]
        for message in messages:
            message["response"] = self.fingerprint(message)
        return messages
    
    @classmethod
    def create(cls):
        """
        abstraction for loading model based on os environment-specified model.
        """
        model = get_class('lib.model.', os.environ.get('MODEL_NAME'))
        return model()
