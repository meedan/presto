message_data = {'body': {'id': '123', 'callback_url': 'http://0.0.0.0:80/callback_url', 'url': None, 'text': 'Presto is a Python service that aims to perform, most generally, on-demand media fingerprints at scale. In the context of text, fingerprints are transformer vectors - video is done by TMK, images by PDQ, and audio by chromaprint.', 'raw': {}, 'parameters': {}, 'result': {'keywords': [['on-demand media fingerprints', 0.00037756579801656625], ['Python service', 0.0026918756686680483], ['transformer vectors', 0.04263260949486705], ['Presto', 0.0680162625368027], ['aims', 0.0680162625368027], ['generally', 0.0680162625368027], ['media', 0.0680162625368027], ['scale', 0.0680162625368027], ['service that aims', 0.07298009589946147], ['fingerprints at scale', 0.0795563516909433]]}}, 'model_name': 'yake_keywords.Model'}
from pydantic import BaseModel, ValidationError
from typing import Any, Dict, List, Optional, Union

class MediaResponse(BaseModel):
    hash_value: Optional[Any] = None

class VideoResponse(MediaResponse):
    folder: Optional[str] = None
    filepath: Optional[str] = None

class YakeKeywordsResponse(BaseModel):
    keywords: List[List[Union[str, float]]]

class GenericItem(BaseModel):
    id: str
    callback_url: Optional[str] = None
    url: Optional[str] = None
    text: Optional[str] = None
    raw: Optional[Dict] = {}
    parameters: Optional[Dict] = {}
    result: Optional[Union[MediaResponse, VideoResponse, YakeKeywordsResponse]]

class Message(BaseModel):
    body: GenericItem
    model_name: str

def parse_message(message_data: Dict) -> Message:
    body_data = message_data['body']
    model_name = message_data['model_name']
    result_data = body_data.get('result', {})
    if 'yake_keywords' in model_name:
        result_instance = YakeKeywordsResponse(**result_data)
    elif 'video' in model_name:
        result_instance = VideoResponse(**result_data)
    else:
        result_instance = MediaResponse(**result_data)
    del body_data['result']
    body_instance = GenericItem(**body_data)
    body_instance.result = result_instance
    message_instance = Message(body=body_instance, model_name=model_name)
    return message_instance
