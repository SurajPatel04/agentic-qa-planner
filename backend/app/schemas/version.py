import uuid
from typing import Dict, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class QAPlanVersionResponse(BaseModel):
    id: uuid.UUID
    qa_plan_id: uuid.UUID
    version_number: int
    change_summary: str
    snapshot: Dict[str, Any]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CreateVersionRequest(BaseModel):
    change_summary: str
