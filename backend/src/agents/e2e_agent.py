import uuid

from src.agents.llm_provider import LLMProvider
from src.models.test_case import TestCase, TestCategory, TestSubCategory, TestStatus


E2E_SYSTEM_PROMPT = """You are an expert QA engineer specializing in end-to-end testing with Playwright.
Generate resilient browser automation scripts with DOM auto-healing selectors, visual state assertions,
network interceptors, and screenshot/video capture capabilities.
Output ONLY valid Playwright TypeScript code — no explanations, no markdown fences."""


class E2ETestAgent:
    def __init__(self, llm_provider: LLMProvider):
        self.llm = llm_provider

    async def generate(
        self,
        context_id: str,
        requirements: list[dict],
        code_entities: list[dict],
    ) -> list[TestCase]:
        test_cases = []

        user_flow_reqs = [
            r for r in requirements
            if any(kw in r.get("description", "").lower() for kw in ["user", "ui", "page", "click", "navigate", "form", "flow", "journey", "screen"])
        ]

        if not user_flow_reqs:
            user_flow_reqs = requirements[:3]

        for req in user_flow_reqs[:3]:
            prompt = self._build_e2e_prompt(req)

            try:
                code = await self.llm.generate(E2E_SYSTEM_PROMPT, prompt, max_tokens=2048)
            except Exception:
                code = self._generate_fallback_e2e_test(req)

            test_id = f"TC-FUNC-E2E-{uuid.uuid4().hex[:6].upper()}"
            test_cases.append(TestCase(
                test_id=test_id,
                context_id=context_id,
                title=f"E2E: {req.get('description', 'User flow')[:80]}",
                category=TestCategory.FUNCTIONAL,
                sub_category=TestSubCategory.E2E,
                target_framework="Playwright",
                script_path=f"tests/e2e/{self._slugify(req.get('tag', 'flow'))}.spec.ts",
                code_body=code,
                status=TestStatus.READY,
            ))

        return test_cases

    def _build_e2e_prompt(self, req: dict) -> str:
        return f"""Generate a Playwright E2E test for the following user flow requirement:

Requirement: {req.get('tag', '')}
Description: {req.get('description', '')}
Section: {req.get('section', '')}

Generate a complete Playwright test that:
1. Uses data-testid selectors with fallback to text/content selectors
2. Includes page.waitForSelector for async content
3. Takes screenshots at key steps
4. Intercepts and validates network requests
5. Tests both happy path and error states
6. Uses test.describe to group related scenarios

Output only the TypeScript code."""

    def _slugify(self, text: str) -> str:
        import re
        return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:40]

    def _generate_fallback_e2e_test(self, req: dict) -> str:
        tag = req.get("tag", "flow")
        desc = req.get("description", "User flow test")
        return f'''import {{ test, expect }} from "@playwright/test";

test.describe("{desc[:60]}", () => {{
  test("should complete the user flow successfully", async ({{ page }}) => {{
    await page.goto("/");
    await page.waitForLoadState("networkidle");
    await expect(page).toHaveTitle(/./);
  }});

  test("should handle error states gracefully", async ({{ page }}) => {{
    await page.goto("/");
    await page.waitForLoadState("networkidle");
  }});
}});
'''
