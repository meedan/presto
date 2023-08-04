from typing import Any, List, Union
from pydantic import BaseModel, HttpUrl

# Output hash values can be of different types.
HashValue = Union[List[float], str, int]
class TextInput(BaseModel):
    id: str
    callback_url: HttpUrl
    text: str

class TextOutput(BaseModel):
    id: str
    callback_url: HttpUrl
    text: str
    response: Union[List[float], str]

class VideoInput(BaseModel):
    id: str
    callback_url: HttpUrl
    url: HttpUrl

class VideoOutput(BaseModel):
    id: str
    callback_url: HttpUrl
    url: HttpUrl
    bucket: str
    outfile: str
    hash_value: HashValue

class AudioInput(BaseModel):
    id: str
    callback_url: HttpUrl
    url: HttpUrl

class AudioOutput(BaseModel):
    id: str
    callback_url: HttpUrl
    url: HttpUrl
    hash_value: HashValue

class ImageInput(BaseModel):
    id: str
    callback_url: HttpUrl
    url: HttpUrl

class ImageOutput(BaseModel):
    id: str
    callback_url: HttpUrl
    url: HttpUrl
    hash_value: HashValue

class Message(BaseModel):
    body: Union[TextIinput, VideoInput, AudioInput, ImageInput]
    response: Any

