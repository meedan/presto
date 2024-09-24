from typing import Optional, List
from pydantic import BaseModel


class ClassyCatResponse(BaseModel):
    # TODO: replase with the presto repose class?
    responseMessage: Optional[str] = None


class ClassyCatBatchClassificationResponse(ClassyCatResponse):
    results: List[dict] = []


class ClassyCatSchemaResponse(ClassyCatResponse):
    schema_id: Optional[str] = None
