from enum import Enum


class PlanStatus(str, Enum):
    DRAFT = "draft"
    REVIEWED = "reviewed"
    APPROVED = "approved"
    ARCHIVED = "archived"


class TestType(str, Enum):
    UNIT = "unit"
    API = "api"
    INTEGRATION = "integration"
    E2E = "e2e"
    PLAYWRIGHT = "playwright"
    MANUAL = "manual"


class TestCategory(str, Enum):
    HAPPY_PATH = "happy_path"
    EDGE_CASE = "edge_case"
    PERMISSION = "permission"
    FAILURE_STATE = "failure_state"
    REGRESSION = "regression"


class TestStatus(str, Enum):
    PROPOSED = "proposed"
    APPROVED = "approved"
    REJECTED = "rejected"
    EDITED = "edited"


class TestPriority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ReviewAction(str, Enum):
    APPROVED = "approved"
    REJECTED = "rejected"
    EDITED = "edited"
    PRIORITY_CHANGED = "priority_changed"
    STATUS_CHANGED = "status_changed"
