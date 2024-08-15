from pydantic import BaseModel
from typing import Any, Dict, List, Optional, Union
from lib.helpers import get_class
import os


class ErrorResponse(BaseModel):
    error: Optional[str] = None
    error_details: Optional[Dict] = None
    error_code: int = 500

# TODO move below definition to the model specific file. ticket: https://meedan.atlassian.net/browse/CV2-5093
class MediaResponse(BaseModel):
    hash_value: Optional[Any] = None

# TODO move below definition to the model specific file. ticket: https://meedan.atlassian.net/browse/CV2-5093
class VideoResponse(MediaResponse):
    folder: Optional[str] = None
    filepath: Optional[str] = None

# TODO move below definition to the model specific file. ticket: https://meedan.atlassian.net/browse/CV2-5093
class YakeKeywordsResponse(BaseModel):
    keywords: Optional[List[List[Union[str, float]]]] = None


class GenericItem(BaseModel):
    id: Union[str, int, float]
    content_hash: Optional[str] = None
    callback_url: Optional[str] = None
    url: Optional[str] = None
    text: Optional[str] = None
    raw: Optional[Dict] = {}
    parameters: Optional[Dict] = {}
    result: Optional[Any] = None

class Message(BaseModel):
    body: GenericItem
    model_name: str
    retry_count: int = 0

def parse_input_message(message_data: Dict) -> Message:
    body_data = message_data['body']
    model_name = message_data['model_name']
    result_data = body_data.get('result', {})

    modelClass = get_class('lib.model.', os.environ.get('MODEL_NAME'))
    modelClass.validate_input(body_data)  # will raise exceptions in case of validation errors
    # parse_input_message will enable us to have more complicated result types without having to change the schema file
    result_instance = modelClass.parse_input_message(body_data)  # assumes input is valid

    # TODO: the following is a temporary solution to handle the case where the model does not have a
    # parse_input_message method implemented but we must ultimately implement parse_input_message and
    # validate_input in all models. ticket: https://meedan.atlassian.net/browse/CV2-5093
    if result_instance is None:  # in case the model does not have a parse_input_message method implemented
        if 'yake_keywords' in model_name:
            result_instance = YakeKeywordsResponse(**result_data)
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


def parse_output_message(message_data: Message) -> None:
    pass