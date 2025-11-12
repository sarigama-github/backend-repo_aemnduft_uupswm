"""
Database Schemas for TechVista HR Document Access System

Each Pydantic model maps to a MongoDB collection (lowercased class name).
"""
from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime

Department = Literal[
    "Engineering",
    "Sales",
    "Marketing",
    "Operations",
    "Finance",
    "Customer Support",
    "Design",
]

DocType = Literal[
    "Policies",
    "Forms",
    "Templates",
    "Guides",
    "Checklists",
]

FileFormat = Literal["PDF", "DOCX", "XLSX"]

class Document(BaseModel):
    title: str = Field(..., description="Document title")
    doc_type: DocType = Field(..., description="High-level document type")
    departments: List[Department] = Field(default_factory=list, description="Related departments")
    last_updated: datetime = Field(..., description="Last updated timestamp")
    version: str = Field(..., description="Semantic or incremental version string")
    latest: bool = Field(True, description="Whether this is the latest version")
    size_kb: int = Field(..., ge=0, description="Approximate file size in KB")
    format: FileFormat = Field(..., description="File format")
    canonical_id: str = Field(..., description="Stable canonical ID for this document across versions")
    download_url: str = Field(..., description="Direct download URL of this version")

class Favorite(BaseModel):
    user_id: str = Field(..., description="User identifier (e.g., email)")
    document_id: str = Field(..., description="Mongo _id string of a document")
    note: Optional[str] = Field(None, description="Optional note from the user")

class Bookmark(BaseModel):
    name: str = Field(..., description="Bookmark name")
    owner: str = Field(..., description="Owner (user or team)")
    document_id: str = Field(..., description="Mongo _id string of a document")
    shared: bool = Field(False, description="Whether this bookmark is shared with the team")
