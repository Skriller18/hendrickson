import httpx
from typing import Optional


class JIRAConnector:
    def __init__(self, url: str, email: str, api_token: str):
        self.base_url = url.rstrip("/")
        self.auth = (email, api_token)
        self.headers = {"Accept": "application/json"}

    async def get_issue(self, issue_key: str) -> Optional[dict]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}/rest/api/3/issue/{issue_key}",
                auth=self.auth,
                headers=self.headers,
            )
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "external_id": data["key"],
                    "title": data["fields"].get("summary", ""),
                    "description": self._extract_description(data),
                    "status": data["fields"].get("status", {}).get("name", "Unknown"),
                    "ticket_type": data["fields"].get("issuetype", {}).get("name", "Task"),
                    "source": "jira",
                }
            return None

    async def search_issues(self, jql: str, max_results: int = 50) -> list[dict]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}/rest/api/3/search",
                auth=self.auth,
                headers=self.headers,
                params={"jql": jql, "maxResults": max_results},
            )
            if resp.status_code == 200:
                data = resp.json()
                return [
                    {
                        "external_id": issue["key"],
                        "title": issue["fields"].get("summary", ""),
                        "description": self._extract_description(issue),
                        "status": issue["fields"].get("status", {}).get("name", "Unknown"),
                        "ticket_type": issue["fields"].get("issuetype", {}).get("name", "Task"),
                        "source": "jira",
                    }
                    for issue in data.get("issues", [])
                ]
            return []

    async def create_issue(
        self,
        project_key: str,
        summary: str,
        description: str,
        issue_type: str = "Bug",
    ) -> Optional[dict]:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/rest/api/3/issue",
                auth=self.auth,
                headers={**self.headers, "Content-Type": "application/json"},
                json={
                    "fields": {
                        "project": {"key": project_key},
                        "summary": summary,
                        "description": {
                            "type": "doc",
                            "version": 1,
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [{"type": "text", "text": description}],
                                }
                            ],
                        },
                        "issuetype": {"name": issue_type},
                    }
                },
            )
            if resp.status_code in (200, 201):
                data = resp.json()
                return {"external_id": data["key"], "url": f"{self.base_url}/browse/{data['key']}"}
            return None

    async def transition_issue(self, issue_key: str, transition_name: str) -> bool:
        async with httpx.AsyncClient() as client:
            transitions_resp = await client.get(
                f"{self.base_url}/rest/api/3/issue/{issue_key}/transitions",
                auth=self.auth,
                headers=self.headers,
            )
            if transitions_resp.status_code != 200:
                return False

            transitions = transitions_resp.json().get("transitions", [])
            transition_id = None
            for t in transitions:
                if t.get("name", "").lower() == transition_name.lower():
                    transition_id = t["id"]
                    break

            if not transition_id:
                return False

            resp = await client.post(
                f"{self.base_url}/rest/api/3/issue/{issue_key}/transitions",
                auth=self.auth,
                headers={**self.headers, "Content-Type": "application/json"},
                json={"transition": {"id": transition_id}},
            )
            return resp.status_code == 204

    def _extract_description(self, issue_data: dict) -> str:
        fields = issue_data.get("fields", {})
        desc = fields.get("description", {})
        if isinstance(desc, dict):
            content = desc.get("content", [])
            texts = []
            for block in content:
                for item in block.get("content", []):
                    if item.get("type") == "text":
                        texts.append(item.get("text", ""))
            return " ".join(texts)
        return str(desc) if desc else ""
