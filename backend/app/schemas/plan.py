import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

from app.schemas.test_case import TestCaseResponse
from app.schemas.version import QAPlanVersionResponse

class AcceptanceCriteriaResponse(BaseModel):
    id: uuid.UUID
    identifier: str
    text: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ExecutionLogResponse(BaseModel):
    id: uuid.UUID
    node: str
    status: str
    message: str
    details: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class QAPlanResponse(BaseModel):
    id: uuid.UUID
    title: str
    status: str
    current_version: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class QAPlanDetailResponse(QAPlanResponse):
    requirement_or_user_story: str
    implementation_summary: Optional[str] = None
    assumptions: List[str]
    coverage_summary: Dict[str, Any]
    
    acceptance_criteria: List[AcceptanceCriteriaResponse] = []
    test_cases: List[TestCaseResponse] = []
    versions: List[QAPlanVersionResponse] = []
    execution_logs: List[ExecutionLogResponse] = []

    model_config = ConfigDict(from_attributes=True)

class GeneratePlanRequest(BaseModel):
    title: str
    user_story: str
    acceptance_criteria: List[str]
    implementation_summary: str

class UpdatePlanRequest(BaseModel):
    status: str
