import os
import unittest
from unittest.mock import MagicMock

import numpy as np

from lib.model.fasttext import FasttextModel
from lib import schemas

class TestFasttextModel(unittest.TestCase):
    def setUp(self):
        self.model = FasttextModel()
        self.mock_model = MagicMock()

    def test_respond(self):
        query = [schemas.Message(body=schemas.TextInput(id="123", callback_url="http://example.com/callback", text="Hello, how are you?")), schemas.Message(body=schemas.TextInput(id="123", callback_url="http://example.com/callback", text="今天是星期二"))]

        response = self.model.respond(query)
      
        self.assertEqual(len(response), 2)
        self.assertEqual(response[0].response, {'language': 'en', 'script': None, 'score': 1.0000062})
        self.assertEqual(response[1].response, {'language': 'zh', 'script': 'Hans', 'score': 0.83046132})

if __name__ == '__main__':
    unittest.main()
