from sentence_transformers import SentenceTransformer

from lib.model.generic import GenericTransformerModel
MODEL_NAME = 'meedan/indian-sbert'
class IndianSbert(GenericTransformerModel):
    def __init__(self):
        super().__init__(MODEL_NAME)
