import uuid
from typing import Optional

from src.agents.llm_provider import LLMProvider
from src.agents.unit_agent import UnitTestAgent
from src.agents.integration_agent import IntegrationTestAgent
from src.agents.e2e_agent import E2ETestAgent
from src.agents.uat_agent import UATTestAgent
from src.models.test_case import TestCase, TestCategory, TestSubCategory, TestStatus


class TestOrchestrator:
    def __init__(self, llm_provider: LLMProvider):
        self.llm = llm_provider
        self.unit_agent = UnitTestAgent(llm_provider)
        self.integration_agent = IntegrationTestAgent(llm_provider)
        self.e2e_agent = E2ETestAgent(llm_provider)
        self.uat_agent = UATTestAgent(llm_provider)

    async def generate_full_suite(
        self,
        context_id: str,
        requirements: list[dict],
        code_entities: list[dict],
        language: str = "python",
        framework: str = "pytest",
    ) -> list[TestCase]:
        test_cases = []

        unit_tests = await self.unit_agent.generate(
            context_id, requirements, code_entities, language, framework
        )
        test_cases.extend(unit_tests)

        integration_tests = await self.integration_agent.generate(
            context_id, requirements, code_entities, language, framework
        )
        test_cases.extend(integration_tests)

        e2e_tests = await self.e2e_agent.generate(
            context_id, requirements, code_entities
        )
        test_cases.extend(e2e_tests)

        uat_tests = await self.uat_agent.generate(
            context_id, requirements
        )
        test_cases.extend(uat_tests)

        return test_cases

    async def generate_category(
        self,
        context_id: str,
        category: TestCategory,
        sub_category: TestSubCategory,
        requirements: list[dict],
        code_entities: list[dict],
        language: str = "python",
        framework: str = "pytest",
    ) -> list[TestCase]:
        if sub_category == TestSubCategory.UNIT:
            return await self.unit_agent.generate(
                context_id, requirements, code_entities, language, framework
            )
        elif sub_category == TestSubCategory.INTEGRATION:
            return await self.integration_agent.generate(
                context_id, requirements, code_entities, language, framework
            )
        elif sub_category == TestSubCategory.E2E:
            return await self.e2e_agent.generate(context_id, requirements, code_entities)
        elif sub_category == TestSubCategory.UAT:
            return await self.uat_agent.generate(context_id, requirements)
        else:
            return await self.unit_agent.generate(
                context_id, requirements, code_entities, language, framework
            )
