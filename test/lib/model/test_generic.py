import unittest
from unittest.mock import MagicMock, patch

import numpy as np

from lib.model.generic_transformer import GenericTransformerModel
from lib import schemas

class TestGenericTransformerModel(unittest.TestCase):
    def setUp(self):
        self.model = GenericTransformerModel(None)
        self.mock_model = MagicMock()

    def test_vectorize(self):
        texts = ["Hello, how are you?", "I'm doing great, thanks!"]
        self.model.model = self.mock_model
        self.model.model.encode = MagicMock(return_value=np.array([[4, 5, 6], [7, 8, 9]]))
        vectors = self.model.vectorize(texts)
        self.assertEqual(len(vectors), 2)
        self.assertEqual(vectors[0], [4, 5, 6])
        self.assertEqual(vectors[1], [7, 8, 9])

    @patch('lib.cache.Cache.get_cached_result')
    @patch('lib.cache.Cache.set_cached_result')
    def test_respond_with_cache(self, mock_set_cache, mock_get_cache):
        # Simulate cache hit
        mock_get_cache.return_value = [1, 2, 3]

        query = schemas.parse_input_message({
            "body": {
                "id": "123",
                "callback_url": "http://example.com/callback",
                "text": "Anong pangalan mo?"
            },
            "model_name": "fptg__Model"
        })

        response = self.model.respond(query)
        self.assertEqual(len(response), 1)
        self.assertEqual(response[0].body.result, [1, 2, 3])
        mock_set_cache.assert_not_called()

    @patch('lib.cache.Cache.get_cached_result')
    @patch('lib.cache.Cache.set_cached_result')
    def test_respond_without_cache(self, mock_set_cache, mock_get_cache):
        # Simulate cache miss
        mock_get_cache.return_value = None

        query = schemas.parse_input_message({
            "body": {
                "id": "123",
                "callback_url": "http://example.com/callback",
                "text": "Anong pangalan mo?"
            },
            "model_name": "fptg__Model"
        })

        self.model.vectorize = MagicMock(return_value=[[1, 2, 3]])

        response = self.model.respond(query)
        self.assertEqual(len(response), 1)
        self.assertEqual(response[0].body.result, [1, 2, 3])
        mock_set_cache.assert_called_once_with(query.body.content_hash, [1, 2, 3])

    def test_ensure_list(self):
        single_doc = schemas.parse_input_message({
            "body": {
                "id": "123",
                "callback_url": "http://example.com/callback",
                "text": "Hello"
            },
            "model_name": "fptg__Model"
        })

        result = self.model._ensure_list(single_doc)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], single_doc)

    def test_separate_cached_docs(self):
        # Mock cache
        with patch('lib.cache.Cache.get_cached_result') as mock_cache:
            mock_cache.side_effect = [None, [4, 5, 6]]

            docs = [
                schemas.parse_input_message({
                    "body": {
                        "id": "123",
                        "callback_url": "http://example.com/callback",
                        "text": "Hello"
                    },
                    "model_name": "fptg__Model"
                }),
                schemas.parse_input_message({
                    "body": {
                        "id": "456",
                        "callback_url": "http://example.com/callback",
                        "text": "How are you?"
                    },
                    "model_name": "fptg__Model"
                })
            ]

            docs_to_process, texts_to_vectorize = self.model._separate_cached_docs(docs)
            self.assertEqual(len(docs_to_process), 1)
            self.assertEqual(len(texts_to_vectorize), 1)
            self.assertEqual(texts_to_vectorize[0], "Hello")
            self.assertEqual(docs[1].body.result, [4, 5, 6])

    @patch('lib.sentry.capture_custom_message')
    def test_handle_fingerprinting_error(self, mock_capture_custom_message):
        error = ValueError("An error occurred")
        response = self.model.handle_fingerprinting_error(error)
        self.assertIsInstance(response, schemas.ErrorResponse)

if __name__ == '__main__':
    unittest.main()
