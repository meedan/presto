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
        self.mock_model.predict.return_value = (['__label__eng_Latn'], np.array([0.902323124]))
        model = FasttextModel()  # Now it uses mocked functions
        query = [schemas.Message(body=schemas.TextInput(id="123", callback_url="http://example.com/callback", text="Hello, how are you?"))]
        response = model.respond(query)
        self.assertEqual(len(response), 1)
        self.assertEqual(response[0].response, {'language': 'en', 'script': None, 'score': 0.9})

if __name__ == '__main__':
    unittest.main()
