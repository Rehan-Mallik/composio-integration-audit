from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class Confidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Authentication(BaseModel):
    method: str
    description: str
    source_url: str


class Evidence(BaseModel):
    claim: str
    source_url: str
    source_type: str
    quote: Optional[str] = None


class MCPInfo(BaseModel):
    available: bool
    type: Optional[str] = None
    source_url: Optional[str] = None


class AppResearch(BaseModel):
    app_name: str
    category: str

    website: str

    authentication: List[Authentication] = Field(
        default_factory=list
    )

    api_available: bool

    api_documentation_url: Optional[str] = None

    api_access: Optional[str] = None

    api_surface: List[str] = Field(
        default_factory=list
    )

    mcp: MCPInfo

    toolkit_feasibility: Optional[str] = None

    blockers: List[str] = Field(
        default_factory=list
    )

    evidence: List[Evidence] = Field(
        default_factory=list
    )

    confidence: Confidence

    needs_verification: bool = False

    notes: Optional[str] = None
