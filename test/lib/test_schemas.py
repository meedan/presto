import unittest
from unittest.mock import MagicMock

from botocore.exceptions import ClientError
import boto3

from lib import schemas
class TestSchemas(unittest.TestCase):
    def test_audio_output(self):
        message = schemas.parse_input_message({
            'body': {
                'id': '123',
                'callback_url': 'http://0.0.0.0:80/callback_url',
                'url': "https://example.com/audio.mp3",
                'text': None,
                'raw': {},
                'parameters': {},
                'result': {"hash_value": [1,2,3]}
            },
            'model_name': 'audio.Model'
        })
        self.assertIsInstance(message.body, schemas.GenericItem)
        self.assertIsInstance(message.body.result, schemas.MediaResponse)

    def test_image_output(self):
        message = schemas.parse_input_message({
            'body': {
                'id': '123',
                'callback_url': 'http://0.0.0.0:80/callback_url',
                'url': "https://example.com/audio.mp3",
                'text': None,
                'raw': {},
                'parameters': {},
                'result': {"hash_value": [1,2,3]}
            },
            'model_name': 'image.Model'
        })
        self.assertIsInstance(message.body, schemas.GenericItem)
        self.assertIsInstance(message.body.result, schemas.MediaResponse)

    def test_video_output(self):
        message = schemas.parse_input_message({
            'body': {
                'id': '123',
                'callback_url': 'http://0.0.0.0:80/callback_url',
                'url': "https://example.com/audio.mp3",
                'text': None,
                'raw': {},
                'parameters': {},
                'result': {"folder": "foo", "filepath": "bar", "hash_value": [1,2,3]}
            },
            'model_name': 'video.Model'
        })
        self.assertIsInstance(message.body, schemas.GenericItem)
        self.assertIsInstance(message.body.result, schemas.VideoResponse)

    def test_text_output(self):
        message = schemas.parse_input_message({
            'body': {
                'id': '123',
                'callback_url': 'http://0.0.0.0:80/callback_url',
                'url': None,
                'text': 'Presto is a Python service that aims to perform, most generally, on-demand media fingerprints at scale.',
                'raw': {},
                'parameters': {},
                'result': {"hash_value": [1,2,3]}
            },
            'model_name': 'mean_tokens.Model'
        })
        self.assertIsInstance(message.body, schemas.GenericItem)
        self.assertIsInstance(message.body.result, schemas.MediaResponse)

    def test_yake_keyword_output(self):
        message = schemas.parse_input_message({
            'body': {
                'id': '123',
                'callback_url': 'http://0.0.0.0:80/callback_url',
                'url': None,
                'text': 'Presto is a Python service that aims to perform, most generally, on-demand media fingerprints at scale.',
                'raw': {},
                'parameters': {},
                'result': {
                    'keywords': [
                        ['on-demand media fingerprints', 0.00037756579801656625],
                        ['Python service', 0.0026918756686680483],
                        ['Presto', 0.0680162625368027],
                        ['aims', 0.0680162625368027],
                        ['generally', 0.0680162625368027],
                        ['media', 0.0680162625368027],
                        ['scale', 0.0680162625368027],
                        ['service that aims', 0.07298009589946147],
                        ['fingerprints at scale', 0.0795563516909433]
                    ]
                }
            },
            'model_name': 'yake_keywords.Model'
        })
        self.assertIsInstance(message.body, schemas.GenericItem)
        self.assertIsInstance(message.body.result, schemas.YakeKeywordsResponse)

if __name__ == '__main__':
    unittest.main()