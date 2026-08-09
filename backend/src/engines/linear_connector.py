from typing import Optional

import httpx


class LinearConnector:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.linear.app/graphql"
        self.headers = {
            "Authorization": api_key,
            "Content-Type": "application/json",
        }

    async def _graphql(self, query: str, variables: dict | None = None) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                self.base_url,
                headers=self.headers,
                json={"query": query, "variables": variables or {}},
            )
            resp.raise_for_status()
            return resp.json()

    async def get_issue(self, issue_id: str) -> Optional[dict]:
        query = """
        query GetIssue($id: String!) {
            issue(id: $id) {
                id
                identifier
                title
                description
                state { name }
                priority
                assignee { name }
                labels { nodes { name } }
                team { name }
                url
            }
        }
        """
        try:
            data = await self._graphql(query, {"id": issue_id})
            issue = data.get("data", {}).get("issue")
            if not issue:
                return None
            return {
                "external_id": issue.get("identifier", issue_id),
                "title": issue.get("title", ""),
                "description": issue.get("description", "") or "",
                "status": self._extract_status(issue),
                "ticket_type": self._extract_type(issue),
                "source": "linear",
                "url": issue.get("url", ""),
            }
        except Exception:
            return None

    async def search_issues(self, team_id: str, max_results: int = 50) -> list[dict]:
        query = """
        query SearchIssues($teamId: String!, $first: Int!) {
            issues(filter: { team: { id: { eq: $teamId } } }, first: $first) {
                nodes {
                    id
                    identifier
                    title
                    description
                    state { name }
                    priority
                    assignee { name }
                    labels { nodes { name } }
                    team { name }
                    url
                }
            }
        }
        """
        try:
            data = await self._graphql(query, {"teamId": team_id, "first": max_results})
            issues = data.get("data", {}).get("issues", {}).get("nodes", [])
            return [
                {
                    "external_id": issue.get("identifier", ""),
                    "title": issue.get("title", ""),
                    "description": issue.get("description", "") or "",
                    "status": self._extract_status(issue),
                    "ticket_type": self._extract_type(issue),
                    "source": "linear",
                    "url": issue.get("url", ""),
                }
                for issue in issues
            ]
        except Exception:
            return []

    async def get_teams(self) -> list[dict]:
        query = """
        query GetTeams {
            teams {
                nodes {
                    id
                    name
                    key
                }
            }
        }
        """
        try:
            data = await self._graphql(query)
            return data.get("data", {}).get("teams", {}).get("nodes", [])
        except Exception:
            return []

    async def create_issue(
        self,
        team_id: str,
        title: str,
        description: str,
        priority: int = 0,
    ) -> Optional[dict]:
        query = """
        mutation CreateIssue(
            $teamId: String!,
            $title: String!,
            $description: String!,
            $priority: Int!
        ) {
            issueCreate(input: {
                teamId: $teamId
                title: $title
                description: $description
                priority: $priority
            }) {
                success
                issue {
                    id
                    identifier
                    url
                }
            }
        }
        """
        try:
            data = await self._graphql(query, {
                "teamId": team_id,
                "title": title,
                "description": description,
                "priority": priority,
            })
            result = data.get("data", {}).get("issueCreate", {})
            if result.get("success") and result.get("issue"):
                issue = result["issue"]
                return {"external_id": issue["identifier"], "url": issue["url"]}
            return None
        except Exception:
            return None

    @staticmethod
    def _extract_status(issue: dict) -> str:
        state = issue.get("state")
        if state and isinstance(state, dict):
            return state.get("name", "Unknown")
        return "Unknown"

    @staticmethod
    def _extract_type(issue: dict) -> str:
        labels = issue.get("labels", {})
        nodes = labels.get("nodes", []) if isinstance(labels, dict) else []
        if nodes and isinstance(nodes[0], dict):
            return nodes[0].get("name", "Task")
        return "Task"
