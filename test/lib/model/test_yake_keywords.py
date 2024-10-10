import unittest
from unittest.mock import ANY, MagicMock, patch

from lib.model.yake_keywords import Model
from lib import schemas

class TestYakeKeywordsModel(unittest.TestCase):
    def setUp(self):
        self.yake_model = Model()

    @patch('yake.KeywordExtractor.extract_keywords')
    def test_process(self, mock_yake_response):
        message = schemas.parse_input_message({
            "body": {
                "id": "1234",
                "text": "Some Text",
            },
            "model_name": "yake_keywords__Model"
        })
        mock_yake_response.return_value = [["ball", 0.23]]
        self.assertEqual(self.yake_model.process(message), {"keywords": [["ball", 0.23]]})

    @patch('yake.KeywordExtractor.extract_keywords')
    def test_run_yake(self, mock_yake_response):
        message = schemas.parse_input_message({
            "body": {
                "id": "1234",
                "text": "Some Text",
            },
            "model_name": "yake_keywords__Model"
        })
        mock_yake_response.return_value = [["ball", 0.23]]
        self.assertEqual(self.yake_model.run_yake(**self.yake_model.get_params(message)), {"keywords": [["ball", 0.23]]})

    def test_run_yake_real(self):
        message = schemas.parse_input_message({
            "body": {
                "id": "1234",
                "text": "I love Meedan",
            },
            "model_name": "yake_keywords__Model"
        })
        results = self.yake_model.run_yake(**self.yake_model.get_params(message))
        self.assertEqual(results, {"keywords": [('love Meedan', 0.0013670273525686505)]})

    def test_keep_largest_overlapped_keywords(self):
        keywords_test = [('Alegre', 0),('Alegre', 0),('Timpani', 0), ('Presto Timpani', 0), ('AlegreAlegre', 0), ('Alegre Alegre', 0), ("Presto", 0)]
        expected = [('Presto Timpani', 0), ('AlegreAlegre', 0), ('Alegre Alegre', 0)]
        self.assertEqual(self.yake_model.keep_largest_overlapped_keywords(keywords_test), expected)

    def test_normalize_special_characters(self):
        text = "`‘’“”"
        expected = "'''\"\""
        self.assertEqual(self.yake_model.normalize_special_characters(text), expected)

    def test_run_chinese_segmentation(self):
        test_text = '''哈里斯同意与特朗普再进行一次美大选辩论'''
        expected = "哈里斯 同意 与 特朗 普再 进行 一 次 美 大选 辩论"
        self.assertEqual(self.yake_model.run_chinese_segmentation(test_text), expected)

    def test_run_yake_real_with_chinese(self):
        message = schemas.parse_input_message({
            "body": {
                "id": "1234",
                "text": "哈里斯同意与特朗普再进行一次美大选辩论",
            },
            "model_name": "yake_keywords__Model"
        })
        results = self.yake_model.run_yake(**self.yake_model.get_params(message))
        self.assertEqual(results, {'keywords': [('哈里斯', 0.04491197687864554)]})

    def test_get_params_with_defaults(self):
        message = schemas.parse_input_message({
            "body": {
                "id": "1234",
                "text": "Some Text",
            },
            "model_name": "yake_keywords__Model"
        })
        expected = {'text': 'Some Text', 'language': "auto", 'max_ngram_size': 3, 'deduplication_threshold': 0.25, 'deduplication_algo': 'seqm', 'window_size': 0, 'num_of_keywords': 10}
        self.assertEqual(self.yake_model.get_params(message), expected)

    def test_get_params_with_specifics(self):
        params = {'language': "hi", 'max_ngram_size': 10, 'deduplication_threshold': 0.2, 'deduplication_algo': 'goop', 'window_size': 10, 'num_of_keywords': 100}
        message = schemas.parse_input_message({
            "body": {
                "id": "1234",
                "text": "Some Text",
                "parameters": params
            },
            "model_name": "yake_keywords__Model"
        })
        expected = dict(**{'text': 'Some Text'}, **params)
        self.assertEqual(self.yake_model.get_params(message), expected)

    def test_get_params_with_defaults_no_text(self):
        message = schemas.parse_input_message({
            "body": {
                "id": "1234",
            },
            "model_name": "yake_keywords__Model"
        })
        with self.assertRaises(AssertionError):
            self.yake_model.get_params(message)

