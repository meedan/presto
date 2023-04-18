from sentence_transformers import SentenceTransformer

from lib.model.generic_transformer import GenericTransformerModel
MODEL_NAME = 'meedan/indian-sbert'
class IndianSbert(GenericTransformerModel):
    BATCH_SIZE = 100
    def __init__(self):
        super().__init__(MODEL_NAME)
