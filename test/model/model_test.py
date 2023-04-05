import os
import unittest
from lib.model.generic import GenericTransformerModel


class TestModel(unittest.TestCase):
    def test_vectorize(self):
        model = Model()
        with self.assertRaises(NotImplementedError):
            model.vectorize("hello")

    def test_respond(self):
        model = Model()
        with self.assertRaises(NotImplementedError):
            model.respond("hello")

if __name__ == '__main__':
    unittest.main()