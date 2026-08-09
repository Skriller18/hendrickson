from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    context_id: str | None = None
    model: str | None = None


class ChatResponse(BaseModel):
    reply: str
    actions: list[dict] = []


CHAT_SYSTEM_PROMPT = """You are Hendrickson, an AI-driven QA testing harness assistant.
You help users generate, inspect, execute, and analyze test suites.
You can:
- Generate test suites from PRD requirements (unit, integration, E2E, UAT)
- Run sanity checks against JIRA tickets
- Execute regression test suites
- Analyze test metrics and coverage
- Create JIRA tickets for test failures

Respond concisely and actionably. When the user asks to generate tests, run tests, or analyze results,
acknowledge the request and describe what you will do.

If provided with relevant requirements and code context below, use it to give specific, informed answers."""


@router.post("/send", response_model=ChatResponse)
async def send_message(req: ChatRequest, request: Request):
    llm = request.app.state.llm
    vector_store = request.app.state.vector_store

    rag_context = ""
    if req.context_id:
        try:
            reqs = await vector_store.search_requirements(req.message, limit=5)
            code = await vector_store.search_code(req.message, limit=5)
            if reqs:
                rag_context += "\n\nRelevant Requirements:\n" + "\n".join(
                    f"- {r.get('tag', '')}: {r.get('description', '')}" for r in reqs
                )
            if code:
                rag_context += "\n\nRelevant Code Entities:\n" + "\n".join(
                    f"- {c.get('name', '')} ({c.get('entity_type', '')}) in {c.get('file_path', '')}"
                    for c in code
                )
        except Exception:
            pass

    user_prompt = req.message
    if rag_context:
        user_prompt = f"Context:\n{rag_context}\n\nUser: {req.message}"

    model = req.model or request.app.state.llm.default_model

    try:
        reply = await llm.generate(
            system_prompt=CHAT_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            model=model,
            max_tokens=1024,
        )
    except Exception as e:
        reply = (
            f"I understand you want to: {req.message}. However, I encountered an issue: {str(e)}. "
            "Please ensure an LLM provider is configured (OPENAI_API_KEY, ANTHROPIC_API_KEY, or DEEPSEEK_API_KEY)."
        )

    return ChatResponse(reply=reply, actions=[])
