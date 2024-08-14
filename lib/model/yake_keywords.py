from typing import Dict, Any
import io
import urllib.request

from lib.model.model import Model

from lib import schemas

import yake

class Model(Model):
    def run_yake(self, text: str,
                 language: str,
                 max_ngram_size: int,
                 deduplication_threshold: float,
                 deduplication_algo: str,
                 window_size: int,
                 num_of_keywords: int) -> str:
        """run key word/phrase extraction using Yake library in reference https://github.com/LIAAD/yake
        :param text: str
        :param language: str
        :param max_ngram_size: int
        :param deduplication_threshold: float
        :param deduplication_algo: str
        :param window_size: int
        :param num_of_keywords: int
        :returns: str
        """
        custom_kw_extractor = yake.KeywordExtractor(lan=language, n=max_ngram_size, dedupLim=deduplication_threshold,
                                                    dedupFunc=deduplication_algo, windowsSize=window_size,
                                                    top=num_of_keywords, features=None)
        return {"keywords": custom_kw_extractor.extract_keywords(text)}

    def get_params(self, message: schemas.Message) -> dict:
        params = {
            "text": message.body.text,
            "language": message.body.parameters.get("language", "en"),
            "max_ngram_size": message.body.parameters.get("max_ngram_size", 3),
            "deduplication_threshold": message.body.parameters.get("deduplication_threshold", 0.25),
            "deduplication_algo": message.body.parameters.get("deduplication_algo", 'seqm'),
            "window_size": message.body.parameters.get("window_size", 0),
            "num_of_keywords": message.body.parameters.get("num_of_keywords", 10)
        }
        assert params.get("text") is not None
        return params

    def process(self, message: schemas.Message) -> schemas.YakeKeywordsResponse:
        """
        Generic function for returning the actual response.
        """
        keywords = self.run_yake(**self.get_params(message))
        return keywords

    @classmethod
    def validate_input(cls, data: Dict) -> None:
        """
        Validate input data. Must be implemented by all child "Model" classes.
        """
        pass

    @classmethod
    def parse_input_message(cls, data: Dict) -> Any:
        """
        Validate input data. Must be implemented by all child "Model" classes.
        """
        return None
