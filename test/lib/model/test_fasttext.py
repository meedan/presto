import unittest
from unittest.mock import patch, MagicMock
from lib.model.fasttext import FasttextModel
from lib import schemas

class TestFasttextModel(unittest.TestCase):
    def setUp(self):
        self.mock_model = MagicMock()

    @patch('lib.model.fasttext.hf_hub_download')
    @patch('lib.model.fasttext.fasttext.load_model')
    def test_respond(self, mock_fasttext_load_model, mock_hf_hub_download):
        mock_hf_hub_download.return_value = 'mocked_path'
        mock_fasttext_load_model.return_value = self.mock_model
        self.mock_model.predict.return_value = (['__label__eng_Latn'], [0.9])

        model = FasttextModel()  # Now it uses mocked functions
        query = [schemas.Message(body=schemas.TextInput(id="123", callback_url="http://example.com/callback", text="Hello, how are you?")), schemas.Message(body=schemas.TextInput(id="123", callback_url="http://example.com/callback", text="今天是星期二"))]

        response = model.respond(query)

        self.assertEqual(len(response), 2)
        self.assertEqual(response[0].response, '__label__eng_Latn')
        self.assertEqual(response[1].response, '__label__eng_Latn')  # Mocked, so it will be the same

if __name__ == '__main__':
    unittest.main()
