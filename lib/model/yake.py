from typing import Dict
import io
import urllib.request

from lib.model.model import Model

from lib import schemas

from lib.logger import logger

import yake

class Model(Model):
    def run_yake(self, text: str,
                 language: str,
                 max_ngram_size: int,
                 deduplication_threshold: float,
                 deduplication_algo: str,
                 windowSize: int,
                 numOfKeywords: int) -> str:
        """run key word/phrase extraction using Yake library
        :param text: str
        :param language: str
        :param max_ngram_size: int
        :param deduplication_threshold: float
        :param deduplication_algo: str
        :param windowSize: int
        :param numOfKeywords: int
        :returns: str
        """
        custom_kw_extractor = yake.KeywordExtractor(lan=language, n=max_ngram_size, dedupLim=deduplication_threshold,
                                                    dedupFunc=deduplication_algo, windowsSize=windowSize,
                                                    top=numOfKeywords, features=None)
        keywords = custom_kw_extractor.extract_keywords(text)

        return keywords

    def process(self, text: schemas.Message) -> schemas.GenericItem:
        """
        Generic function for returning the actual response.
        """

        keywords = self.run_yake(text = text.body.text,
                                 language = text.body.language,
                                 max_ngram_size = text.body.max_ngram_size,
                                 deduplication_threshold = text.body.deduplication_threshold,
                                 deduplication_algo = text.body.deduplication_algo,
                                 windowSize = text.body.windowSize,
                                 numOfKeywords = text.body.numOfKeywords
                                 )
        return keywords
