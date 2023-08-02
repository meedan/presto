import os
import unittest
from unittest.mock import MagicMock

import numpy as np

from lib.model.fasttext import FasttextModel

class TestFasttextModel(unittest.TestCase):
    def setUp(self):
        self.model = FasttextModel()
        self.mock_model = MagicMock()

    def test_respond(self):
        query = [{"body": {"text": "Hello, how are you?"}}, {"body": {"text": "今天是星期二"}}]

        response = self.model.respond(query)
      
        self.assertEqual(len(response), 2)
        self.assertEqual(response[0]["response"], "__label__eng_Latn")
        self.assertEqual(response[1]["response"], "__label__zho_Hans")

if __name__ == '__main__':
    unittest.main()
