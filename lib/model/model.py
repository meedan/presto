from typing import Any
from abc import ABC, abstractmethod
import os
import tempfile

import urllib.request

from lib.helpers import get_class

class Model(ABC):
    BATCH_SIZE = 1
    def get_tempfile_for_url(self, url: str) -> str:
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
        return tempfile.NamedTemporaryFile()

    def respond(self, messages):
        return []
    
    @classmethod
    def create(cls):
        model = get_class('lib.model.', os.environ.get('MODEL_NAME'))
        return model()
