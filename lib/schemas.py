from typing import Any, List, Optional, Union
from pydantic import BaseModel, root_validator

# Output hash values can be of different types.
class GenericItem(BaseModel):
    id: str
    callback_url: Optional[str] = None
    url: Optional[str] = None
    text: Optional[str] = None
    raw: Optional[dict] = {}

class MediaItem(GenericItem):
    hash_value: Optional[Any] = None

class VideoItem(MediaItem):
    folder: Optional[str] = None
    filepath: Optional[str] = None

class YakeKeywordsItem(GenericItem):
    keywords: Optional[Any] = None

class Message(BaseModel):
    body: Union[MediaItem, VideoItem, YakeKeywordsItem]
    model_name: str
    @root_validator(pre=True)
    def set_body(cls, values):
        body = values.get("body")
        model_name = values.get("model_name")
        if model_name == "video__Model":
            values["body"] = VideoItem(**values["body"]).dict()
        elif model_name in ["audio__Model", "image__Model", "fptg__Model", "indian_sbert__Model", "mean_tokens__Model", "fasttext__Model"]:
            values["body"] = MediaItem(**values["body"]).dict()
        elif model_name == "yake_keywords__Model":
            values["body"] = YakeKeywordsItem(**values["body"]).dict()
        return values
