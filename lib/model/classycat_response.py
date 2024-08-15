from typing import Optional, List
from pydantic import BaseModel


class ClassyCatResponse(BaseModel):
    responseMessage: Optional[str] = None


class ClassyCatBatchClassificationResponse(ClassyCatResponse):
    classification_results: Optional[List[dict]] = []


class ClassyCatSchemaResponse(ClassyCatResponse):
    schema_id: Optional[str] = None