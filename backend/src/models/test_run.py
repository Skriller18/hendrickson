from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class RunStatus(str, Enum):
    PENDING = "Pending"
    RUNNING = "Running"
    COMPLETED = "Completed"
    FAILED = "Failed"


class TestResult(BaseModel):
    test_id: str
    title: str
    status: str
    duration_ms: int = 0
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None
    stdout: str = ""
    stderr: str = ""


class CoverageMetrics(BaseModel):
    line_coverage_pct: float = 0.0
    branch_coverage_pct: float = 0.0
    function_coverage_pct: float = 0.0
    lines_covered: int = 0
    lines_total: int = 0


class TestRun(BaseModel):
    run_id: str
    context_id: str
    test_ids: list[str] = Field(default_factory=list)
    status: RunStatus = RunStatus.PENDING
    environment: str = "sandbox"
    results: list[TestResult] = Field(default_factory=list)
    coverage: Optional[CoverageMetrics] = None
    total_tests: int = 0
    passed: int = 0
    failed: int = 0
    errors: int = 0
    duration_ms: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
