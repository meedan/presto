from typing import Any, List, Optional, Union
from pydantic import BaseModel

# Output hash values can be of different types.
HashValue = Union[List[float], str, int]
class GenericItem(BaseModel):
    id: Optional[str] = None
    callback_url: Optional[str] = None
    url: Optional[str] = None
    text: Optional[str] = None
    raw: Optional[dict] = {}

class MediaItem(GenericItem):
    hash_value: Optional[HashValue] = None

class VideoItem(MediaItem):
    bucket: Optional[str] = None
    outfile: Optional[str] = None

class Message(BaseModel):
    body: Union[GenericItem, MediaItem, VideoItem]