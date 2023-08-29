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
        query = [schemas.Message(body=schemas.TextInput(id="123", callback_url="http://example.com/callback", text="Hello, how are you?")), 
                 schemas.Message(body=schemas.TextInput(id="123", callback_url="http://example.com/callback", text="今天是星期二")),
                 schemas.Message(body=schemas.TextInput(id="123", callback_url="http://example.com/callback", text="چھِ کٲشرۍ نٹن گۅرزٕ خنجر وُچھِتھ		اَژان لرزٕ چھُکھ کانہہ دِلاور وُچھِتھ")),
                 schemas.Message(body=schemas.TextInput(id="123", callback_url="http://example.com/callback", text="🐐🐐🐐🐐123")),
                schemas.Message(body=schemas.TextInput(id="123", callback_url="http://example.com/callback", text=""))]
        

        response = self.model.respond(query)
      
        self.assertEqual(len(response), 2)
        self.assertEqual(response[0].response, {'language': 'en', 'script': None, 'score': 1.0})
        self.assertEqual(response[1].response, {'language': 'zh', 'script': 'Hans', 'score': 0.8305})
        self.assertEqual(response[2].response, {'language': 'ks', 'script': 'Arab', 'score': 0.9999})
        self.assertEqual(response[3].response, {'language': 'bo', 'script': 'Tibt', 'score': 0.2168}) #non-text content returns random language with low certainty
        self.assertEqual(response[3].response, {'language': 'en', 'script': None, 'score': 0.8267})  #empty string returns english with high-ish confidence

if __name__ == '__main__':
    unittest.main()
