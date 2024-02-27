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

class YakeItem(GenericItem):
    language: Optional[str] = None
    max_ngram_size: Optional[int] = None
    deduplication_threshold: Optional[float] = None
    deduplication_algo: Optional[str] = None
    windowSize: Optional[int] = None
    numOfKeywords: Optional[int] = None

class Message(BaseModel):
    body: Union[YakeItem, MediaItem, VideoItem]
    model_name: str
    @root_validator(pre=True)
    def set_body(cls, values):
        body = values.get("body")
        model_name = values.get("model_name")
        if model_name == "video__Model":
            values["body"] = VideoItem(**values["body"]).dict()
        if model_name in ["audio__Model", "image__Model", "fptg__Model", "indian_sbert__Model", "mean_tokens__Model", "fasttext__Model"]:
            values["body"] = MediaItem(**values["body"]).dict()
        if model_name == "yake__Model":
            values["body"] = YakeItem(**values["body"]).dict()
        return values
