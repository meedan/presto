from pydantic import BaseModel
from typing import Any, Dict, List, Optional, Union
from lib.helpers import get_class
from lib.base_exception import PrestoBaseException
import os


class ResponseItem:
    id: Union[
        str, int, float
    ]  # this id must match to the ids of GenericItem in request


class Response(BaseModel):
    status_code: int
    status_message: Optional[str] = None
    results: List[ResponseItem]  # this can be MediaResponse, etc


class ErrorResponse(Response):
    error: Optional[str] = None
    error_details: Optional[Dict] = None
    # error_code: int = 500   This should use the status code instead


# TODO move below definition to the model specific file. ticket: https://meedan.atlassian.net/browse/CV2-5093
class MediaResponse(ResponseItem):
    hash_value: Optional[Any] = None


# TODO move below definition to the model specific file. ticket: https://meedan.atlassian.net/browse/CV2-5093
class VideoResponse(MediaResponse):
    folder: Optional[str] = None
    filepath: Optional[str] = None


# TODO move below definition to the model specific file. ticket: https://meedan.atlassian.net/browse/CV2-5093
class YakeKeywordsResponse(ResponseItem):
    keywords: Optional[List[List[Union[str, float]]]] = None


class GenericItem(BaseModel):
    id: Union[str, int, float]  # id (in calling system) for this content
    content_hash: Optional[str] = None
    url: Optional[str] = None
    text: Optional[str] = None
    raw: Optional[Dict] = {}  # TODO: is this needed?
    parameters: Optional[Dict] = (
        {}
    )  # optional parameters specific to processing this item (i.e. language)


class Message(BaseModel):
    request_id: Union[str, int, float]
    items: List[GenericItem]  # to support batch, this is a list (can be only 1 item)
    model_name: str
    model_parameters: Optional[Dict] = (
        {}
    )  # optional parameters specific to this model call (i.e. threshold)
    retry_count: int = 0
    callback_url: Optional[str] = None


def parse_input_message(message_data: Dict) -> Message:
    if "body" not in message_data or "model_name" not in message_data:
        raise PrestoBaseException(
            "Invalid message data: message should at minimum include body and model_name",
            422,
        )

    body_data = message_data["body"]  # TODO: this becomes the 'items' list
    model_name = message_data["model_name"]
    result_data = body_data.get("result", {})
    # TODO: validate callback_url

    try:
        presto_model_class_name = model_name.replace(
            "__", "."
        )  # todo don't love this line of code
        model_class = get_class("lib.model.", presto_model_class_name)
    except Exception as e:
        raise PrestoBaseException(
            f"Error loading model {model_name}, model_name is not supported: {e}", 404
        ) from e

    model_class.validate_input(
        body_data
    )  # will raise exceptions in case of validation errors
    # parse_input_message will enable us to have more complicated result types without having to change the schema file
    result_instance = model_class.parse_input_message(
        body_data
    )  # assumes input is valid

    # TODO: the following is a temporary solution to handle the case where the model does not have a
    # parse_input_message method implemented but we must ultimately implement parse_input_message and
    # validate_input in all models. ticket: https://meedan.atlassian.net/browse/CV2-5093
    if (
        result_instance is None
    ):  # in case the model does not have a parse_input_message method implemented
        if "yake_keywords" in model_name:
            result_instance = YakeKeywordsResponse(**result_data)
        elif "video" in model_name:
            result_instance = VideoResponse(**result_data)
        else:
            result_instance = MediaResponse(**result_data)

    if "result" in body_data:
        del body_data["result"]

    body_instance = GenericItem(**body_data)
    body_instance.result = result_instance
    message_instance = Message(body=body_instance, model_name=model_name)
    return message_instance


def parse_output_message(message_data: Message) -> None:
    pass
    # TODO: make sure ids in the output correspond to ids in the input?
