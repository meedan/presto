import os
import unittest
from lib.model.generic import GenericTransformerModel

class TestGenericTransformerModel(unittest.TestCase):
    def test_vectorize(self):
        model = GenericTransformerModel()
        with self.assertRaises(NotImplementedError):
            model.vectorize("hello")

    def test_respond(self):
        model = GenericTransformerModel()
        with self.assertRaises(NotImplementedError):
            model.respond("hello")


if __name__ == '__main__':
    unittest.main()