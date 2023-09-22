from typing import Any, List, Optional, Union
from pydantic import BaseModel

# Output hash values can be of different types.
HashValue = Union[List[float], str, int]
class TextInput(BaseModel):
    id: str
    callback_url: str
    text: str

class TextOutput(BaseModel):
    id: str
    callback_url: str
    text: str

class VideoInput(BaseModel):
    id: str
    callback_url: str
    url: str

class VideoOutput(BaseModel):
    id: str
    callback_url: str
    url: str
    bucket: str
    outfile: str
    hash_value: HashValue

class AudioInput(BaseModel):
    id: str
    callback_url: str
    url: str

class AudioOutput(BaseModel):
    id: str
    callback_url: str
    url: str
    hash_value: HashValue

class ImageInput(BaseModel):
    id: str
    callback_url: str
    url: str

class ImageOutput(BaseModel):
    id: str
    callback_url: str
    url: str
    hash_value: HashValue

class GenericInput(BaseModel):
    id: str
    callback_url: str
    url: Optional[str] = None
    text: Optional[str] = None
    raw: Optional[dict] = {}

class Message(BaseModel):
    body: GenericInput
    response: Any