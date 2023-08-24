from typing import Union, Dict, List

import fasttext
from huggingface_hub import hf_hub_download

from langcodes import *

from lib.model.model import Model
from lib import schemas

class FasttextModel(Model):
    def __init__(self):
        """
        Load fasttext model (https://huggingface.co/facebook/fasttext-language-identification)
        """
        model_path = hf_hub_download(repo_id="facebook/fasttext-language-identification", filename="model.bin")
        self.model = fasttext.load_model(model_path)

    
    def respond(self, docs: Union[List[schemas.Message], schemas.Message]) -> List[schemas.TextOutput]:
        """
        Force messages as list of messages in case we get a singular item. Then, run fingerprint routine.
        Respond can probably be genericized across all models.
        """
        if not isinstance(docs, list):
            docs = [docs]
        detectable_texts = [e.body.text for e in docs]
        detected_langs = []
        for text in detectable_texts:
            detected_langs.append(standardize_tag(self.model.predict(text)[0][0][9:], macro = True))

        for doc, detected_lang in zip(docs, detected_langs):
            doc.response = detected_lang
        return docs
