from typing import Any, List, Optional, Union
from pydantic import BaseModel, root_validator

# Output hash values can be of different types.
class MediaResponse(BaseModel):
    hash_value: Optional[Any] = None

class VideoResponse(MediaResponse):
    folder: Optional[str] = None
    filepath: Optional[str] = None

class YakeKeywordsResponse(BaseModel):
    keywords: Optional[Any] = None

class GenericItem(BaseModel):
    id: str
    callback_url: Optional[str] = None
    url: Optional[str] = None
    text: Optional[str] = None
    raw: Optional[dict] = {}
    parameters: Optional[dict] = {}
    result: Optional[Union[MediaResponse, VideoResponse, YakeKeywordsResponse]] = None

class Message(BaseModel):
    body: GenericItem
    model_name: str
    @root_validator(pre=True)
    def set_body(cls, values):
        body = values.get("body")
        model_name = values.get("model_name")
        if model_name == "video__Model":
            values["body"]["result"] = VideoResponse(**values["body"]).dict()
        elif model_name in ["audio__Model", "image__Model", "fptg__Model", "indian_sbert__Model", "mean_tokens__Model", "fasttext__Model"]:
            values["body"]["result"] = MediaResponse(**values["body"]).dict()
        if model_name == "yake_keywords__Model":
            values["body"]["result"] = YakeKeywordsResponse(**values["body"]).dict()
        return values
