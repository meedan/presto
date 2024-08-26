from lib.model.generic_transformer import GenericTransformerModel

MODEL_NAME = 'xlm-r-bert-base-nli-stsb-mean-tokens'


class Model(GenericTransformerModel):
    BATCH_SIZE = 100

    def __init__(self):
        """
        Init MeanTokens model. Fairly standard for all vectorizers.
        """
        super().__init__(MODEL_NAME)
