from sentence_transformers import SentenceTransformer

from lib.model.model import Model
class GenericTransformerModel(Model):
    def __init__(self, model_name):
        self.model = None
        if model_name:
            self.model = SentenceTransformer(model_name)

    def respond(self, docs):
        if not isinstance(docs, list):
            docs = [docs]
        vectorizable_texts = [e.get("text") for e in docs]
        vectorized = self.vectorize(vectorizable_texts)
        for doc, vector in zip(docs, vectorized):
            doc["response"] = vector
        return docs

    def vectorize(self, doc):
        return self.model.encode(doc).tolist()
