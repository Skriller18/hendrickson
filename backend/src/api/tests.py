import uuid
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel

from src.models.test_case import TestCase, TestCategory, TestSubCategory, TestStatus

router = APIRouter()


class GenerateTestsRequest(BaseModel):
    context_id: str
    category: str = "Functional"
    sub_category: str = "Unit"
    language: str = "python"
    framework: str = "pytest"


class TestCaseResponse(BaseModel):
    test_id: str
    context_id: str
    title: str
    category: str
    sub_category: str
    target_framework: str
    script_path: str
    code_body: str
    status: str
    prd_reference: str | None = None
    jira_reference: str | None = None


@router.post("/generate", response_model=list[TestCaseResponse])
async def generate_tests(req: GenerateTestsRequest, request: Request):
    db = request.app.state.mongo_db
    orchestrator = request.app.state.orchestrator

    context_doc = await db.contexts.find_one({"context_id": req.context_id})
    if not context_doc:
        raise HTTPException(status_code=404, detail="Context not found")

    requirements = []
    async for req_doc in db.requirements.find({"context_id": req.context_id}):
        req_doc.pop("_id", None)
        requirements.append(req_doc)

    code_entities = []
    async for ent_doc in db.code_entities.find({"context_id": req.context_id}):
        ent_doc.pop("_id", None)
        code_entities.append(ent_doc)

    category = TestCategory(req.category)
    sub_category = TestSubCategory(req.sub_category)

    test_cases = await orchestrator.generate_category(
        context_id=req.context_id,
        category=category,
        sub_category=sub_category,
        requirements=requirements,
        code_entities=code_entities,
        language=req.language,
        framework=req.framework,
    )

    for tc in test_cases:
        await db.test_cases.insert_one(tc.model_dump())

    return [
        TestCaseResponse(
            test_id=tc.test_id,
            context_id=tc.context_id,
            title=tc.title,
            category=tc.category.value,
            sub_category=tc.sub_category.value,
            target_framework=tc.target_framework,
            script_path=tc.script_path,
            code_body=tc.code_body,
            status=tc.status.value,
            prd_reference=tc.prd_reference,
            jira_reference=tc.jira_reference,
        )
        for tc in test_cases
    ]


@router.get("/")
async def list_tests(context_id: str | None = None, request: Request = None):
    db = request.app.state.mongo_db
    query = {}
    if context_id:
        query["context_id"] = context_id

    cursor = db.test_cases.find(query).sort("created_at", -1).limit(50)
    tests = []
    async for doc in cursor:
        doc.pop("_id", None)
        tests.append(doc)
    return tests


@router.get("/{test_id}")
async def get_test(test_id: str, request: Request):
    db = request.app.state.mongo_db
    doc = await db.test_cases.find_one({"test_id": test_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Test case not found")
    doc.pop("_id", None)
    return doc


@router.put("/{test_id}")
async def update_test(test_id: str, update: dict, request: Request):
    db = request.app.state.mongo_db
    result = await db.test_cases.update_one(
        {"test_id": test_id}, {"$set": update}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Test case not found")
    return {"status": "updated"}
