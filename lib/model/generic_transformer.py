import os
from typing import Union, Dict, List, Any
from sentence_transformers import SentenceTransformer
from lib.logger import logger
from lib.model.model import Model
from lib import schemas

class GenericTransformerModel(Model):
    def __init__(self, model_name: str):
        """
        Load specified model name from subclass constant as HuggingFace transformer.
        """
        self.model = None
        self.model_name = model_name
        if model_name:
            self.model = SentenceTransformer(model_name, cache_folder=os.getenv("MODEL_DIR", "./models"))

    def respond(self, docs: Union[List[schemas.Message], schemas.Message]) -> List[schemas.GenericItem]:
        """
        Force messages as list of messages in case we get a singular item. Then, run fingerprint routine.
        Respond can probably be genericized across all models.
        """
        if not isinstance(docs, list):
            docs = [docs]
        logger.info(docs)
        vectorizable_texts = [e.body.text for e in docs]
        vectorized = self.vectorize(vectorizable_texts)
        for doc, vector in zip(docs, vectorized):
            doc.body.result = vector
        return docs

    def vectorize(self, texts: List[str]) -> List[List[float]]:
        """
        Vectorize the text! Run as batch.
        """
        return {"hash_value": self.model.encode(texts).tolist()}

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