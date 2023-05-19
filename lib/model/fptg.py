from sentence_transformers import SentenceTransformer

from lib.model.generic_transformer import GenericTransformerModel
MODEL_NAME = 'meedan/paraphrase-filipino-mpnet-base-v2'
class MdebertaFilipino(GenericTransformerModel):
    BATCH_SIZE = 100
    def __init__(self):
        """
        Init FPTG model. Fairly standard for all vectorizers.
        """
        super().__init__(MODEL_NAME)
