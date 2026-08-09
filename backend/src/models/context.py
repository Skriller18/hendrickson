from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class PRDReference(BaseModel):
    id: str
    version: str
    title: str


class CodebaseReference(BaseModel):
    repository: str
    branch: str
    commit_hash: str
    affected_files: list[str] = Field(default_factory=list)


class TicketingReference(BaseModel):
    jira_issue_keys: list[str] = Field(default_factory=list)
    linear_issue_ids: list[str] = Field(default_factory=list)
    status: str = "Open"


class Context(BaseModel):
    context_id: str
    prd: Optional[PRDReference] = None
    codebase: Optional[CodebaseReference] = None
    ticketing: Optional[TicketingReference] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Requirement(BaseModel):
    requirement_id: str
    context_id: str
    tag: str
    description: str
    acceptance_criteria: list[str] = Field(default_factory=list)
    source_document: str
    source_line: int = 0


class CodeEntity(BaseModel):
    entity_id: str
    context_id: str
    file_path: str
    entity_type: str
    name: str
    signature: str
    dependencies: list[str] = Field(default_factory=list)
    ast_node_type: str


class Ticket(BaseModel):
    ticket_id: str
    context_id: str
    external_id: str
    source: str
    title: str
    description: str
    status: str
    ticket_type: str
    linked_requirements: list[str] = Field(default_factory=list)
