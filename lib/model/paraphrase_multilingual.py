from lib.model.generic_transformer import GenericTransformerModel
MODEL_NAME = 'sentence-transformers/paraphrase-multilingual-mpnet-base-v2'
class Model(GenericTransformerModel):
    BATCH_SIZE = 100
    def __init__(self):
        """
        Init ParaphraseMultilingual model. Fairly standard for all vectorizers.
        """
        super().__init__(MODEL_NAME)
