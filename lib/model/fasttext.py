from typing import Union, Dict, List
from lib.model.model import Model

import fasttext
from huggingface_hub import hf_hub_download


class FasttextModel(Model):
    def __init__(self):
        """
        Load fasttext model
        """
        model_path = hf_hub_download(repo_id="facebook/fasttext-language-identification", filename="model.bin")
        self.model = fasttext.load_model(model_path)

    
    def respond(self, docs: Union[List[Dict[str, str]], Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Force messages as list of messages in case we get a singular item. Then, run fingerprint routine.
        Respond can probably be genericized across all models.
        """
        if not isinstance(docs, list):
            docs = [docs]
        detectable_texts = [e.get("body", {}).get("text") for e in docs]
        detected_langs = []
        for text in detectable_texts:
            detected_langs.append(self.model.predict(text)[0][0])

        for doc, vector in zip(docs, detected_langs):
            doc["response"] = detected_lang
        return docs
