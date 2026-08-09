from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class TestCategory(str, Enum):
    FUNCTIONAL = "Functional"
    OPERATIONAL = "Operational"
    NON_FUNCTIONAL = "Non-Functional"


class TestSubCategory(str, Enum):
    UNIT = "Unit"
    INTEGRATION = "Integration"
    SYSTEM = "System"
    E2E = "E2E"
    UAT = "UAT"
    SMOKE = "Smoke"
    SANITY = "Sanity"
    REGRESSION = "Regression"
    PERFORMANCE = "Performance"
    LOAD = "Load"
    STRESS = "Stress"
    SECURITY = "Security"


class TestStatus(str, Enum):
    DRAFT = "Draft"
    READY = "Ready"
    RUNNING = "Running"
    PASSED = "Passed"
    FAILED = "Failed"
    ERROR = "Error"


class TestMetrics(BaseModel):
    last_execution: Optional[datetime] = None
    status: Optional[TestStatus] = None
    duration_ms: Optional[int] = None
    memory_mb: Optional[float] = None
    flakiness_score: float = 0.0


class TestCase(BaseModel):
    test_id: str
    context_id: str
    title: str
    category: TestCategory
    sub_category: TestSubCategory
    prd_reference: Optional[str] = None
    jira_reference: Optional[str] = None
    target_framework: str
    script_path: str
    code_body: str
    status: TestStatus = TestStatus.DRAFT
    metrics: TestMetrics = Field(default_factory=TestMetrics)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
