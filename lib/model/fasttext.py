from typing import Union, Dict, List, Any

import fasttext
from huggingface_hub import hf_hub_download

from langcodes import standardize_tag

from lib.model.model import Model
from lib import schemas


class FasttextModel(Model):
    def __init__(self):
        """
        Load fasttext model (https://huggingface.co/facebook/fasttext-language-identification)
        """
        model_path = hf_hub_download(repo_id="facebook/fasttext-language-identification", filename="model.bin")
        self.model = fasttext.load_model(model_path)

    
    def respond(self, docs: Union[List[schemas.Message], schemas.Message]) -> List[schemas.GenericItem]:
        """
        Force messages as list of messages in case we get a singular item. Then, run fingerprint routine.
        Respond can probably be genericized across all models.
        """
        if not isinstance(docs, list):
            docs = [docs]
        detectable_texts = [e.body.text for e in docs]
        detected_langs = []
        for text in detectable_texts:
            model_output = self.model.predict(text)  #format (('__label__zho_Hans',), array([0.81644011])), where zho is 3-letter ISO code, Hans is script tag, and 0.81 is certainty
            model_certainty = model_output[1][0].round(4)  #value representing model's certainty

            #standardize_tag will standardize to 2-letter codes where possible
            #and will remove the script tag unless the language is often written in different scripts
            #setting macro=True allows us to standardize ISO macro languages (eg. swa == swh -> sw)
            model_language = standardize_tag(model_output[0][0][9:], macro = True)  
            model_script = None
            if '-' in model_language: 
                [model_language, model_script] = model_language.split('-')
            
            detected_langs.append({'language': model_language, 'script': model_script, 'score': model_certainty})  

        for doc, detected_lang in zip(docs, detected_langs):
            doc.body.result = detected_lang
        return docs

    @classmethod
    def validate_input(cls, data: Dict) -> None:
        """
        Validate input data. Must be implemented by all child "Model" classes.
        """
        pass

    @classmethod
    def parse_input_message(cls, data: Dict) -> Any:
        """
        Validate input data. Must be implemented by all child "Model" classes.
        """
        return None