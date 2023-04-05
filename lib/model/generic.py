from sentence_transformers import SentenceTransformer

from lib.model.model import Model
class GenericTransformerModel(Model):
    def __init__(self):
        self.model = SentenceTransformer(MODEL_NAME)

    def respond(self, docs):
        if not isinstance(docs, list):
            docs = [docs]
        vectorizable_texts = [e.get("text") for e in docs]
        vectorized = self.vectorize(vectorizable_texts)
        for doc, vector in zip(docs, vectorized):
            doc["vector_output"] = vector
        return docs

    def vectorize(self, doc):
        return self.model.encode(doc).tolist()
