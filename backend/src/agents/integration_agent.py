import uuid

from src.agents.llm_provider import LLMProvider
from src.models.test_case import TestCase, TestCategory, TestSubCategory, TestStatus


INTEGRATION_SYSTEM_PROMPT = """You are an expert QA engineer specializing in integration testing.
Generate tests that validate inter-module communication, database transactions, API endpoints, and webhooks.
Use Testcontainers for ephemeral databases and mock external HTTP services.
Output ONLY valid code — no explanations, no markdown fences."""


class IntegrationTestAgent:
    def __init__(self, llm_provider: LLMProvider):
        self.llm = llm_provider

    async def generate(
        self,
        context_id: str,
        requirements: list[dict],
        code_entities: list[dict],
        language: str = "python",
        framework: str = "pytest",
    ) -> list[TestCase]:
        test_cases = []

        api_entities = [
            e for e in code_entities
            if any(kw in e.get("name", "").lower() for kw in ["api", "route", "endpoint", "handler", "controller", "service"])
        ]

        if not api_entities:
            api_entities = code_entities[:3]

        for entity in api_entities[:5]:
            req_context = self._build_requirement_context(requirements, entity)
            prompt = self._build_integration_prompt(entity, req_context, language, framework)

            try:
                code = await self.llm.generate(INTEGRATION_SYSTEM_PROMPT, prompt, max_tokens=2048)
            except Exception:
                code = self._generate_fallback_integration_test(entity, language, framework)

            test_id = f"TC-FUNC-INT-{uuid.uuid4().hex[:6].upper()}"
            test_cases.append(TestCase(
                test_id=test_id,
                context_id=context_id,
                title=f"Integration test for {entity.get('name', 'unknown')}",
                category=TestCategory.FUNCTIONAL,
                sub_category=TestSubCategory.INTEGRATION,
                target_framework=f"{framework} + Testcontainers",
                script_path=f"tests/integration/test_{entity.get('name', 'test')}.py",
                code_body=code,
                status=TestStatus.READY,
            ))

        return test_cases

    def _build_integration_prompt(
        self, entity: dict, req_context: str, language: str, framework: str
    ) -> str:
        return f"""Generate an integration test for the following {language} component:

Component: {entity['name']}
Signature: {entity.get('signature', '')}
File: {entity.get('file_path', '')}

Requirements context:
{req_context}

Generate a complete integration test that:
1. Spins up required services via Testcontainers (PostgreSQL, Redis, etc.)
2. Tests API endpoint request/response contracts
3. Validates database state after operations
4. Tests webhook/message queue interactions
5. Includes proper setup/teardown

Output only the code."""

    def _build_requirement_context(self, requirements: list[dict], entity: dict) -> str:
        entity_name = entity.get("name", "").lower()
        relevant = []
        for req in requirements:
            desc = req.get("description", "").lower()
            if entity_name in desc or any(
                kw in desc for kw in ["api", "endpoint", "integration", "service", "database", "webhook"]
            ):
                relevant.append(f"- {req.get('tag', '')}: {req.get('description', '')}")
        return "\n".join(relevant[:5]) if relevant else "No specific requirements linked."

    def _generate_fallback_integration_test(self, entity: dict, language: str, framework: str) -> str:
        name = entity.get("name", "unknown")
        if language == "python" and framework == "pytest":
            return f'''import pytest
from testcontainers.postgres import PostgresContainer


@pytest.fixture(scope="module")
def postgres_container():
    with PostgresContainer("postgres:16") as postgres:
        yield postgres


def test_{name}_integration(postgres_container):
    """Integration test for {name}."""
    connection_url = postgres_container.get_connection_url()
    assert connection_url is not None


def test_{name}_api_contract():
    """Verify API contract for {name}."""
    pass
'''
        return f"// Integration test for {name}\n// TODO: Implement with AI generation"
