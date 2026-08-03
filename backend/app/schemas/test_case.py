import uuid
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class TestCaseResponse(BaseModel):
    id: uuid.UUID
    qa_plan_id: uuid.UUID
    title: str
    description: str
    test_type: str
    category: str
    acceptance_criteria_ids: List[str]
    rationale: str
    steps: List[str]
    expected_result: str
    preconditions: Optional[str] = None
    status: str
    priority: str
    is_duplicate: bool
    is_incomplete: bool
    flag_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UpdateTestCaseRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    steps: Optional[List[str]] = None
    expected_result: Optional[str] = None
    rationale: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
