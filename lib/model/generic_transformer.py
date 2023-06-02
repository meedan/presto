from typing import Union, Dict, List
from sentence_transformers import SentenceTransformer

from lib.model.model import Model
class GenericTransformerModel(Model):
    def __init__(self, model_name: str):
        """
        Load specified model name from subclass constant as HuggingFace transformer.
        """
        self.model = None
        if model_name:
            self.model = SentenceTransformer(model_name)

    def respond(self, docs: Union[List[Dict[str, str]], Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Force messages as list of messages in case we get a singular item. Then, run fingerprint routine.
        Respond can probably be genericized across all models.
        """
        if not isinstance(docs, list):
            docs = [docs]
        vectorizable_texts = [e.get("body", {}).get("text") for e in docs]
        vectorized = self.vectorize(vectorizable_texts)
        for doc, vector in zip(docs, vectorized):
            doc["response"] = vector
        return docs

    def vectorize(self, texts: List[str]) -> List[List[float]]:
        """
        Vectorize the text! Run as batch.
        """
        return self.model.encode(texts).tolist()
