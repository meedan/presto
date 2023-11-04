from typing import Any, List, Optional, Union
from pydantic import BaseModel

# Output hash values can be of different types.
class GenericItem(BaseModel):
    id: Optional[str] = None
    callback_url: Optional[str] = None
    url: Optional[str] = None
    text: Optional[str] = None
    raw: Optional[dict] = {}
    hash_value: Optional[Any] = None
    bucket: Optional[str] = None
    outfile: Optional[str] = None

class Message(BaseModel):
    body: Union[GenericItem]