import uuid
from datetime import datetime
from typing import Optional

from src.engines.prd_parser import PRDParser
from src.engines.github_indexer import GitHubIndexer
from src.engines.jira_connector import JIRAConnector
from src.models.context import Context, PRDReference, CodebaseReference, TicketingReference


class Triangulator:
    def __init__(
        self,
        github_token: str = "",
        jira_url: str = "",
        jira_email: str = "",
        jira_api_token: str = "",
    ):
        self.prd_parser = PRDParser()
        self.github_indexer = GitHubIndexer(token=github_token)
        self.jira = (
            JIRAConnector(jira_url, jira_email, jira_api_token)
            if jira_url and jira_email and jira_api_token
            else None
        )

    async def triangulate(
        self,
        prd_path: Optional[str] = None,
        prd_content: Optional[str] = None,
        repo_url: Optional[str] = None,
        branch: str = "main",
        jira_keys: Optional[list[str]] = None,
    ) -> dict:
        context_id = f"CTX-{uuid.uuid4().hex[:8].upper()}"
        result = {"context_id": context_id, "requirements": [], "code_entities": [], "tickets": []}

        if prd_path or prd_content:
            if prd_path:
                requirements = self.prd_parser.parse_file(prd_path)
            else:
                requirements = self.prd_parser.parse_text(prd_content or "", "inline")
            result["requirements"] = requirements

        if repo_url:
            code_data = self.github_indexer.clone_and_index(repo_url, branch)
            result["code_entities"] = code_data.get("entities", [])
            result["codebase"] = {
                "repository": repo_url,
                "branch": branch,
                "commit_hash": code_data.get("commit_hash", ""),
                "affected_files": code_data.get("affected_files", []),
            }

        if jira_keys and self.jira:
            tickets = []
            for key in jira_keys:
                issue = await self.jira.get_issue(key)
                if issue:
                    tickets.append(issue)
            result["tickets"] = tickets

        return result

    def build_context_document(self, triangulation_result: dict) -> Context:
        ctx = Context(context_id=triangulation_result["context_id"])

        if triangulation_result.get("requirements"):
            first_req = triangulation_result["requirements"][0]
            ctx.prd = PRDReference(
                id=ctx.context_id,
                version="1.0",
                title=first_req.get("source_document", "Untitled PRD"),
            )

        if triangulation_result.get("codebase"):
            cb = triangulation_result["codebase"]
            ctx.codebase = CodebaseReference(
                repository=cb["repository"],
                branch=cb["branch"],
                commit_hash=cb["commit_hash"],
                affected_files=cb["affected_files"],
            )

        if triangulation_result.get("tickets"):
            ctx.ticketing = TicketingReference(
                jira_issue_keys=[t["external_id"] for t in triangulation_result["tickets"]],
                status="In QA Verification",
            )

        return ctx
