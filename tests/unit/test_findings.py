"""Tests for structured engineering findings."""

import pytest
from pydantic import ValidationError

from enterprise_mcp.models.findings import (
    FindingCategory,
    ReviewFinding,
    Severity,
)


def test_valid_finding_is_accepted():
    finding = ReviewFinding(
        title="Unsafe SQL construction",
        severity=Severity.HIGH,
        category=FindingCategory.SECURITY,
        description="User input is concatenated into an SQL query.",
        evidence="The query uses a value derived from user input.",
        recommendation="Use parameterized SQL queries.",
        file_path="src/database.py",
        line_number=42,
    )

    assert finding.severity == Severity.HIGH
    assert finding.line_number == 42


def test_invalid_severity_is_rejected():
    with pytest.raises(ValidationError):
        ReviewFinding(
            title="Example",
            severity="urgent",
            category="security",
            description="Description",
            evidence="Evidence",
            recommendation="Recommendation",
        )


def test_unknown_fields_are_rejected():
    with pytest.raises(ValidationError):
        ReviewFinding(
            title="Example",
            severity="low",
            category="correctness",
            description="Description",
            evidence="Evidence",
            recommendation="Recommendation",
            confidence="100%",
        )


def test_invalid_line_number_is_rejected():
    with pytest.raises(ValidationError):
        ReviewFinding(
            title="Example",
            severity="low",
            category="correctness",
            description="Description",
            evidence="Evidence",
            recommendation="Recommendation",
            line_number=0,
        )
