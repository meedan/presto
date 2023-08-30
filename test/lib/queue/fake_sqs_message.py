from pydantic import BaseModel
class FakeSQSMessage(BaseModel):
    body: str
    receipt_handle: str

