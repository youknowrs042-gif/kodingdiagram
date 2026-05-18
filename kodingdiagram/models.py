"""Shared data models for the entire toolkit."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


def _new_id() -> str:
    return str(uuid.uuid4())


# --- Document ---

class Document(BaseModel):
    id: str = Field(default_factory=_new_id)
    name: str
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


# --- NLP ---

class LemmaResult(BaseModel):
    lemma: str
    frequency: int


class EntityResult(BaseModel):
    text: str
    label: str
    start_char: int
    end_char: int


class SentenceResult(BaseModel):
    text: str
    start_char: int
    end_char: int


# --- Coding ---

class Code(BaseModel):
    id: str = Field(default_factory=_new_id)
    name: str
    color: str = "#3b82f6"
    description: str = ""
    group: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Quotation(BaseModel):
    id: str = Field(default_factory=_new_id)
    document_id: str
    code_ids: list[str] = Field(default_factory=list)
    text: str
    start_char: int
    end_char: int
    comment: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Memo(BaseModel):
    id: str = Field(default_factory=_new_id)
    title: str
    content: str
    linked_codes: list[str] = Field(default_factory=list)
    linked_quotations: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CodeGroup(BaseModel):
    id: str = Field(default_factory=_new_id)
    name: str
    code_ids: list[str] = Field(default_factory=list)


# --- Theming ---

class ThemeLevel(str, Enum):
    INITIAL = "initial"
    ORGANIZING = "organizing"
    GLOBAL = "global"


class Theme(BaseModel):
    id: str = Field(default_factory=_new_id)
    name: str
    level: ThemeLevel = ThemeLevel.INITIAL
    description: str = ""
    code_ids: list[str] = Field(default_factory=list)
    parent_theme_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


# --- Visualization ---

class NodeType(str, Enum):
    DOCUMENT = "document"
    CODE = "code"
    QUOTATION = "quotation"
    THEME = "theme"
    ENTITY = "entity"


class NetworkNode(BaseModel):
    id: str
    label: str
    node_type: NodeType
    metadata: dict = Field(default_factory=dict)


class NetworkEdge(BaseModel):
    source: str
    target: str
    relation: str
    weight: float = 1.0


class NetworkGraph(BaseModel):
    nodes: list[NetworkNode] = Field(default_factory=list)
    edges: list[NetworkEdge] = Field(default_factory=list)
