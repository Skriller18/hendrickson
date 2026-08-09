import uuid
import asyncio
from datetime import datetime
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel

from src.services.sandbox import SandboxExecutor
from src.services.metrics import MetricsCalculator
from src.models.test_run import TestRun, RunStatus, TestResult

router = APIRouter()


class RunTestsRequest(BaseModel):
    context_id: str
    test_ids: list[str] | None = None
    environment: str = "sandbox"


class RunStatusResponse(BaseModel):
    run_id: str
    status: str
    total_tests: int
    passed: int
    failed: int
    errors: int
    duration_ms: int


@router.post("/execute", response_model=RunStatusResponse)
async def execute_tests(req: RunTestsRequest, request: Request):
    db = request.app.state.mongo_db

    query = {"context_id": req.context_id}
    if req.test_ids:
        query["test_id"] = {"$in": req.test_ids}

    test_docs = []
    cursor = db.test_cases.find(query)
    async for doc in cursor:
        doc.pop("_id", None)
        test_docs.append(doc)

    if not test_docs:
        raise HTTPException(status_code=404, detail="No test cases found")

    run_id = f"RUN-{uuid.uuid4().hex[:8].upper()}"
    test_run = TestRun(
        run_id=run_id,
        context_id=req.context_id,
        test_ids=[t["test_id"] for t in test_docs],
        status=RunStatus.RUNNING,
        environment=req.environment,
        total_tests=len(test_docs),
        started_at=datetime.utcnow(),
    )
    await db.test_runs.insert_one(test_run.model_dump())

    executor = SandboxExecutor()
    calculator = MetricsCalculator()

    results = []
    for test_doc in test_docs:
        result = await executor.execute_test(
            test_code=test_doc.get("code_body", ""),
            language="python",
            framework=test_doc.get("target_framework", "pytest"),
            test_id=test_doc["test_id"],
        )

        test_result = TestResult(
            test_id=test_doc["test_id"],
            title=test_doc.get("title", ""),
            status=result["status"],
            duration_ms=result.get("duration_ms", 0),
            error_message=result.get("stderr", ""),
            stdout=result.get("stdout", ""),
            stderr=result.get("stderr", ""),
        )
        results.append(test_result)

        await db.test_cases.update_one(
            {"test_id": test_doc["test_id"]},
            {"$set": {
                "status": result["status"],
                "metrics.last_execution": datetime.utcnow(),
                "metrics.status": result["status"],
                "metrics.duration_ms": result.get("duration_ms", 0),
            }},
        )

    aggregated = calculator.aggregate_run_metrics([
        {"status": r.status, "duration_ms": r.duration_ms} for r in results
    ])

    completed_at = datetime.utcnow()
    duration_ms = int((completed_at - test_run.started_at).total_seconds() * 1000)

    await db.test_runs.update_one(
        {"run_id": run_id},
        {"$set": {
            "status": RunStatus.COMPLETED,
            "results": [r.model_dump() for r in results],
            "passed": aggregated["passed"],
            "failed": aggregated["failed"],
            "errors": aggregated["errors"],
            "duration_ms": duration_ms,
            "completed_at": completed_at,
        }},
    )

    return RunStatusResponse(
        run_id=run_id,
        status="Completed",
        total_tests=aggregated["total"],
        passed=aggregated["passed"],
        failed=aggregated["failed"],
        errors=aggregated["errors"],
        duration_ms=duration_ms,
    )


@router.get("/{run_id}")
async def get_run(run_id: str, request: Request):
    db = request.app.state.mongo_db
    doc = await db.test_runs.find_one({"run_id": run_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Test run not found")
    doc.pop("_id", None)
    return doc


@router.get("/")
async def list_runs(context_id: str | None = None, request: Request = None):
    db = request.app.state.mongo_db
    query = {}
    if context_id:
        query["context_id"] = context_id

    cursor = db.test_runs.find(query).sort("created_at", -1).limit(20)
    runs = []
    async for doc in cursor:
        doc.pop("_id", None)
        runs.append(doc)
    return runs
