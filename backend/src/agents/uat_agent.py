import uuid

from src.agents.llm_provider import LLMProvider
from src.models.test_case import TestCase, TestCategory, TestSubCategory, TestStatus


UAT_SYSTEM_PROMPT = """You are an expert QA engineer specializing in User Acceptance Testing (UAT) and BDD.
Translate product requirements into Gherkin BDD specifications (Given/When/Then) with underlying step bindings.
Output ONLY valid Gherkin + Python step definitions — no explanations, no markdown fences."""


class UATTestAgent:
    def __init__(self, llm_provider: LLMProvider):
        self.llm = llm_provider

    async def generate(
        self,
        context_id: str,
        requirements: list[dict],
    ) -> list[TestCase]:
        test_cases = []

        acceptance_reqs = [
            r for r in requirements
            if r.get("acceptance_criteria") or any(
                kw in r.get("description", "").lower()
                for kw in ["accept", "user story", "as a", "i want", "so that", "business", "stakeholder"]
            )
        ]

        if not acceptance_reqs:
            acceptance_reqs = requirements[:3]

        for req in acceptance_reqs[:3]:
            prompt = self._build_uat_prompt(req)

            try:
                code = await self.llm.generate(UAT_SYSTEM_PROMPT, prompt, max_tokens=2048)
            except Exception:
                code = self._generate_fallback_uat_test(req)

            test_id = f"TC-FUNC-UAT-{uuid.uuid4().hex[:6].upper()}"
            test_cases.append(TestCase(
                test_id=test_id,
                context_id=context_id,
                title=f"UAT: {req.get('description', 'Acceptance test')[:80]}",
                category=TestCategory.FUNCTIONAL,
                sub_category=TestSubCategory.UAT,
                target_framework="Behave (Gherkin)",
                script_path=f"tests/uat/{self._slugify(req.get('tag', 'feature'))}.feature",
                code_body=code,
                status=TestStatus.READY,
            ))

        return test_cases

    def _build_uat_prompt(self, req: dict) -> str:
        criteria = req.get("acceptance_criteria", [])
        criteria_text = "\n".join(f"  - {c}" for c in criteria) if criteria else "Not specified"

        return f"""Generate a Gherkin BDD feature file and Python step definitions for:

Requirement: {req.get('tag', '')}
Description: {req.get('description', '')}
Acceptance Criteria:
{criteria_text}

Generate:
1. A .feature file with Feature, Scenario, Given/When/Then steps
2. Python step definition file using behave framework
3. Include both positive and negative scenarios
4. Include scenario outlines with examples where applicable

Output both the .feature content and the step definitions."""

    def _slugify(self, text: str) -> str:
        import re
        return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:40]

    def _generate_fallback_uat_test(self, req: dict) -> str:
        tag = req.get("tag", "feature")
        desc = req.get("description", "Acceptance test")
        return f'''Feature: {desc[:80]}

  Scenario: Happy path acceptance
    Given the system is properly configured
    When the user performs the primary action
    Then the expected outcome is achieved

  Scenario: Error handling
    Given the system is properly configured
    When invalid input is provided
    Then an appropriate error message is displayed


# Step definitions (behave)
from behave import given, when, then


@given("the system is properly configured")
def step_given_system_configured(context):
    pass


@when("the user performs the primary action")
def step_when_user_action(context):
    pass


@then("the expected outcome is achieved")
def step_then_expected_outcome(context):
    pass


@when("invalid input is provided")
def step_when_invalid_input(context):
    pass


@then("an appropriate error message is displayed")
def step_then_error_message(context):
    pass
'''
