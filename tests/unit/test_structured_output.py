"""Tests for Groq structured output generation."""

import json
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from pydantic import ValidationError

from enterprise_mcp.llm.structured_output import generate_review_finding


def make_client(content: str):
    create = AsyncMock(
        return_value=SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(
                        content=content,
                        refusal=None,
                    )
                )
            ]
        )
    )
    client = SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(create=create)
        )
    )
    return client, create


def valid_finding_json() -> str:
    return json.dumps(
        {
            "title": "Unsafe SQL construction",
            "severity": "high",
            "category": "security",
            "description": "User input is concatenated into an SQL query.",
            "evidence": "The query contains a value derived from user input.",
            "recommendation": "Use parameterized SQL queries.",
            "file_path": None,
            "line_number": None,
        }
    )


@pytest.mark.asyncio
async def test_generates_validated_finding():
    client, create = make_client(valid_finding_json())

    result = await generate_review_finding(
        client,
        "query = 'SELECT * FROM users WHERE name = ' + user_input",
    )

    assert result.title == "Unsafe SQL construction"
    assert result.severity.value == "high"
    assert result.file_path is None

    request = create.await_args.kwargs
    assert request["response_format"]["type"] == "json_schema"
    assert request["response_format"]["json_schema"]["strict"] is True


@pytest.mark.asyncio
async def test_rejects_empty_code_context():
    client, create = make_client(valid_finding_json())

    with pytest.raises(ValueError, match="Code context"):
        await generate_review_finding(client, "  ")

    create.assert_not_awaited()


@pytest.mark.asyncio
async def test_rejects_invalid_structured_response():
    client, _ = make_client('{"title": "Missing required fields"}')

    with pytest.raises(ValidationError):
        await generate_review_finding(client, "example code")


@pytest.mark.asyncio
async def test_rejects_empty_response():
    client, _ = make_client("")

    with pytest.raises(RuntimeError, match="empty structured response"):
        await generate_review_finding(client, "example code")
