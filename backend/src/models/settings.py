from datetime import datetime

from pydantic import BaseModel, Field


class ProviderKey(BaseModel):
    provider: str
    api_key: str
    label: str = ""


class JIRASettings(BaseModel):
    url: str = ""
    email: str = ""
    api_token: str = ""


class LinearSettings(BaseModel):
    api_key: str = ""


class GitHubSettings(BaseModel):
    token: str = ""
    connected: bool = False
    username: str = ""


class ConnectorSettings(BaseModel):
    jira: JIRASettings = Field(default_factory=JIRASettings)
    linear: LinearSettings = Field(default_factory=LinearSettings)
    github: GitHubSettings = Field(default_factory=GitHubSettings)


class UserSettings(BaseModel):
    settings_id: str = "default"
    provider_keys: list[ProviderKey] = Field(default_factory=list)
    connectors: ConnectorSettings = Field(default_factory=ConnectorSettings)
    default_model: str = "gpt-5.6-terra"
    updated_at: datetime = Field(default_factory=datetime.utcnow)
