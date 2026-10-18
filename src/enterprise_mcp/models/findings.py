"""Structured models for engineering review findings."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class Severity(StrEnum):
    """Severity assigned to an engineering finding."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class FindingCategory(StrEnum):
    """Category assigned to an engineering finding."""

    SECURITY = "security"
    CORRECTNESS = "correctness"
    PERFORMANCE = "performance"
    RELIABILITY = "reliability"
    MAINTAINABILITY = "maintainability"


class ReviewFinding(BaseModel):
    """One validated finding from an engineering review."""

    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=160)
    severity: Severity
    category: FindingCategory
    description: str = Field(min_length=1, max_length=2000)
    evidence: str = Field(min_length=1, max_length=2000)
    recommendation: str = Field(min_length=1, max_length=2000)
    file_path: str | None = None
    line_number: int | None = Field(default=None, ge=1)
    
