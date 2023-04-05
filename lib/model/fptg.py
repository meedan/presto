from sentence_transformers import SentenceTransformer

from lib.model.generic import GenericTransformerModel
MODEL_NAME = 'meedan/paraphrase-filipino-mpnet-base-v2'
class MdebertaFilipino(GenericTransformerModel):
    def __init__(self):
        super().__init__(MODEL_NAME)
