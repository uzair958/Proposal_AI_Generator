from pydantic import BaseModel


class RevisionRequest(BaseModel):
    request: str