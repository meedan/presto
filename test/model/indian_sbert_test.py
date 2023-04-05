import os
import unittest
from lib.model.model.fptg import IndianSbert

class TestIndianSbert(unittest.TestCase):
    def setUp(self):
        self.model = IndianSbert()

    def test_vectorize(self):
        texts = ["Hello, how are you?", "I'm doing great, thanks!"]
        vectors = self.model.vectorize(texts)
        self.assertEqual(vectors.shape, (2, 768))

    def test_respond(self):
        query = "What is the capital of India?"
        response = self.model.respond(query)
        self.assertIsInstance(response, str)

if __name__ == '__main__':
    unittest.main()