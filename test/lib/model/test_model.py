import os
import unittest
from lib.model.model import Model


class TestModel(unittest.TestCase):
    def test_respond(self):
        model = Model()
        self.assertEqual(model.respond({"text": "hello"}), [])

if __name__ == '__main__':
    unittest.main()