from sentence_transformers import SentenceTransformer

from lib.model.generic_transformer import GenericTransformerModel
MODEL_NAME = 'facebook/fasttext-language-identification'

class Model(GenericTransformerModel):
    BATCH_SIZE = 100
    def __init__(self):
        """
        Init Facebook FastText language identification model. Fairly standard for all vectorizers.
        """
        super().__init__(MODEL_NAME)
