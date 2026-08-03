from typing import List
from pydantic import BaseModel, Field

class TestCaseSchema(BaseModel):
    """Represents a single generated test case."""
    title: str = Field(..., description="Short, descriptive title of the test case")
    description: str = Field(..., description="Overall description of the test scenario")
    test_type: str = Field(
        ..., 
        description="Must be one of: UNIT, API, INTEGRATION, E2E, PLAYWRIGHT, MANUAL"
    )
    category: str = Field(
        ...,
        description="Must be one of: HAPPY_PATH, EDGE_CASE, PERMISSION, FAILURE_STATE, REGRESSION"
    )
    rationale: str = Field(..., description="Why is this test relevant and necessary?")
    steps: List[str] = Field(default_factory=list, description="Step-by-step instructions to execute the test")
    expected_result: str = Field(..., description="The expected outcome of the test")
    covered_acceptance_criteria: List[str] = Field(
        default_factory=list, 
        description="List of acceptance criteria identifiers (e.g., 'AC1') covered by this test"
    )

class AnalysisOutput(BaseModel):
    """Structured output for the Requirement Analysis node."""
    user_flows: list[str] = Field(description="Main user flows identified from the requirements")
    assumptions: list[str] = Field(description="Assumptions made about the requirements or missing context")
    risks: list[str] = Field(description="Potential risks, edge cases, or regression areas identified")

class TestGenerationOutput(BaseModel):
    """Structured output for the Test Generation node."""
    test_cases: list[TestCaseSchema]
