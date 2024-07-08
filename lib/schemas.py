from pydantic import BaseModel, ValidationError
from typing import Any, Dict, List, Optional, Union

class MediaResponse(BaseModel):
    hash_value: Optional[Any] = None

class VideoResponse(MediaResponse):
    folder: Optional[str] = None
    filepath: Optional[str] = None

class YakeKeywordsResponse(BaseModel):
    keywords: Optional[List[List[Union[str, float]]]] = None

class ClassyCatResponse(BaseModel):
    responseMessage: Optional[str] = None

class ClassyCatBatchClassificationResponse(ClassyCatResponse):
    classification_results: Optional[List[Dict[Union[str, int], Union[str, List[str]]]]] = []

class ClassyCatSchemaResponse(ClassyCatResponse):
    schema_id: Optional[str] = None

class GenericItem(BaseModel):
    id: Union[str, int, float]
    content_hash: Optional[str] = None
    callback_url: Optional[str] = None
    url: Optional[str] = None
    text: Optional[str] = None
    raw: Optional[Dict] = {}
    parameters: Optional[Dict] = {}
    result: Optional[Union[MediaResponse, VideoResponse, YakeKeywordsResponse, ClassyCatSchemaResponse, ClassyCatBatchClassificationResponse]] = None

class Message(BaseModel):
    body: GenericItem
    model_name: str
    retry_count: int = 0

def parse_message(message_data: Dict) -> Message:
    body_data = message_data['body']
    model_name = message_data['model_name']
    result_data = body_data.get('result', {})
    if 'yake_keywords' in model_name:
        result_instance = YakeKeywordsResponse(**result_data)
    elif 'classycat' in model_name:
        event_type = body_data['parameters']['event_type']
        if event_type == 'classify':
            result_instance = ClassyCatBatchClassificationResponse(**result_data)
        elif event_type == 'schema_lookup' or event_type == 'schema_create':
            result_instance = ClassyCatSchemaResponse(**result_data)
        else:
            result_instance = ClassyCatResponse(**result_data)
    elif 'video' in model_name:
        result_instance = VideoResponse(**result_data)
    else:
        result_instance = MediaResponse(**result_data)
    if 'result' in body_data:
        del body_data['result']
    body_instance = GenericItem(**body_data)
    body_instance.result = result_instance
    message_instance = Message(body=body_instance, model_name=model_name)
    return message_instance
