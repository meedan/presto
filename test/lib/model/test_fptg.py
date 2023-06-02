import os
import unittest
from unittest.mock import MagicMock

import numpy as np

from lib.model.generic_transformer import GenericTransformerModel

class TestMdebertaFilipino(unittest.TestCase):
    def setUp(self):
        self.model = GenericTransformerModel(None)
        self.mock_model = MagicMock()

    def test_vectorize(self):
        texts = [{"body": {"text": "Hello, how are you?"}}, {"body": {"text": "I'm doing great, thanks!"}}]
        self.model.model = self.mock_model
        self.model.model.encode = MagicMock(return_value=np.array([[4, 5, 6], [7, 8, 9]]))
        vectors = self.model.vectorize(texts)
        self.assertEqual(len(vectors), 2)
        self.assertEqual(vectors[0], [4, 5, 6])
        self.assertEqual(vectors[1], [7, 8, 9])

    def test_respond(self):
        query = {"body": {"text": "Anong pangalan mo?"}}
        self.model.vectorize = MagicMock(return_value=[[1, 2, 3]])
        response = self.model.respond(query)
        self.assertEqual(len(response), 1)
        self.assertIn("response", response[0])
        self.assertEqual(response[0]["response"], [1, 2, 3])

if __name__ == '__main__':
    unittest.main()