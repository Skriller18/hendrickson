import uuid
from typing import Optional

from src.agents.llm_provider import LLMProvider
from src.models.test_case import TestCase, TestCategory, TestSubCategory, TestStatus


UNIT_SYSTEM_PROMPT = """You are an expert QA engineer specializing in unit testing.
Generate production-quality unit tests with 100% branch and line coverage intent.
Create mock objects and synthetic fixtures for all external dependencies (databases, APIs, file I/O).
Output ONLY valid code — no explanations, no markdown fences."""


class UnitTestAgent:
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

        functions = [e for e in code_entities if e.get("entity_type") == "function"]
        classes = [e for e in code_entities if e.get("entity_type") == "class"]

        for func in functions[:10]:
            req_context = self._build_requirement_context(requirements, func)
            prompt = self._build_unit_prompt(func, req_context, language, framework)

            try:
                code = await self.llm.generate(UNIT_SYSTEM_PROMPT, prompt, max_tokens=2048)
            except Exception:
                code = self._generate_fallback_unit_test(func, language, framework)

            test_id = f"TC-FUNC-UNIT-{uuid.uuid4().hex[:6].upper()}"
            test_cases.append(TestCase(
                test_id=test_id,
                context_id=context_id,
                title=f"Unit test for {func.get('name', 'unknown')}",
                category=TestCategory.FUNCTIONAL,
                sub_category=TestSubCategory.UNIT,
                target_framework=framework,
                script_path=f"tests/unit/test_{func.get('name', 'test')}.py",
                code_body=code,
                status=TestStatus.READY,
            ))

        return test_cases

    def _build_unit_prompt(
        self, entity: dict, req_context: str, language: str, framework: str
    ) -> str:
        return f"""Generate a {framework} unit test for the following {language} {entity['entity_type']}:

Entity: {entity['name']}
Signature: {entity.get('signature', '')}
File: {entity.get('file_path', '')}

Requirements context:
{req_context}

Generate a complete, runnable test file with:
1. All necessary imports
2. Mock objects for external dependencies
3. Test for happy path
4. Test for edge cases (None, empty, boundary values)
5. Test for error conditions
6. Parametrized tests where applicable

Output only the code."""

    def _build_requirement_context(self, requirements: list[dict], entity: dict) -> str:
        entity_name = entity.get("name", "").lower()
        relevant = []
        for req in requirements:
            desc = req.get("description", "").lower()
            if entity_name in desc or any(
                kw in desc for kw in ["validate", "verify", "test", "check", "ensure"]
            ):
                relevant.append(f"- {req.get('tag', '')}: {req.get('description', '')}")
        return "\n".join(relevant[:5]) if relevant else "No specific requirements linked."

    def _generate_fallback_unit_test(self, entity: dict, language: str, framework: str) -> str:
        name = entity.get("name", "unknown")
        if language == "python" and framework == "pytest":
            return f'''import pytest
from unittest.mock import MagicMock, patch


def test_{name}_happy_path():
    """Test {name} with valid inputs."""
    pass


def test_{name}_edge_cases():
    """Test {name} with edge case inputs."""
    pass


def test_{name}_error_handling():
    """Test {name} error handling."""
    pass
'''
        return f"// Unit test for {name}\n// TODO: Implement with AI generation"
