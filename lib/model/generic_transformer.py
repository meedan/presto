import os
from typing import Union, Dict, List, Any
from sentence_transformers import SentenceTransformer
from lib.logger import logger
from lib.model.model import Model
from lib import schemas
from lib.cache import Cache

class GenericTransformerModel(Model):
    def __init__(self, model_name: str):
        """
        Load specified model name from subclass constant as HuggingFace transformer.
        """
        self.model = None
        self.model_name = os.environ.get("MODEL_NAME")
        self.internal_model_name = model_name
        if self.internal_model_name:
            self.model = SentenceTransformer(self.internal_model_name, cache_folder=os.getenv("MODEL_DIR", "./models"))

    def respond(self, docs: Union[List[schemas.Message], schemas.Message]) -> List[schemas.GenericItem]:
        """
        Respond to a batch of messages by vectorizing uncached texts.
        """
        docs = self._ensure_list(docs)
        self._log_docs(docs)
        docs_to_process, texts_to_vectorize = self._separate_cached_docs(docs)

        if texts_to_vectorize:
            self._vectorize_and_cache(docs_to_process, texts_to_vectorize)

        return docs

    def _ensure_list(self, docs: Union[List[schemas.Message], schemas.Message]) -> List[schemas.Message]:
        """
        Ensure the input is a list of messages.
        """
        return docs if isinstance(docs, list) else [docs]

    def _log_docs(self, docs: List[schemas.Message]):
        """
        Log the documents for debugging purposes.
        """
        logger.info(docs)

    def _separate_cached_docs(self, docs: List[schemas.Message]) -> (List[schemas.Message], List[str]):
        """
        Separate cached documents from those that need to be vectorized.
        """
        docs_to_process = []
        texts_to_vectorize = []

        for doc in docs:
            cached_result = Cache.get_cached_result(doc.body.content_hash)
            if cached_result:
                doc.body.result = cached_result
            else:
                docs_to_process.append(doc)
                texts_to_vectorize.append(doc.body.text)

        return docs_to_process, texts_to_vectorize

    def _vectorize_and_cache(self, docs_to_process: List[schemas.Message], texts_to_vectorize: List[str]):
        """
        Vectorize the uncached texts and store the results in the cache.
        """
        try:
            vectorized = self.vectorize(texts_to_vectorize)
            for doc, vector in zip(docs_to_process, vectorized):
                doc.body.result = vector
                Cache.set_cached_result(doc.body.content_hash, vector)
        except Exception as e:
            self.handle_fingerprinting_error(e, 500, {"texts_to_vectorize": texts_to_vectorize})

    def vectorize(self, texts: List[str]) -> List[List[float]]:
        """
        Vectorize the text! Run as batch.
        """
        return self.model.encode(texts).tolist()


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