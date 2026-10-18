
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from pydantic import SecretStr

from enterprise_mcp.config import settings
from enterprise_mcp.llm.client import create_groq_client, generate_text


def test_create_client_requires_api_key(monkeypatch):
    monkeypatch.setattr(settings, "groq_api_key", None)

    with pytest.raises(RuntimeError, match="GROQ_API_KEY"):
        create_groq_client()


def test_create_client_rejects_placeholder_key(monkeypatch):
    monkeypatch.setattr(
        settings,
        "groq_api_key",
        SecretStr("your_groq_api_key_here"),
    )

    with pytest.raises(RuntimeError, match="placeholder"):
        create_groq_client()


@pytest.mark.asyncio
async def test_generate_text_returns_model_response():
    client = SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(
                create=AsyncMock(
                    return_value=SimpleNamespace(
                        choices=[
                            SimpleNamespace(
                                message=SimpleNamespace(
                                    content="Automated reviews catch defects early."
                                )
                            )
                        ]
                    )
                )
            )
        )
    )

    result = await generate_text(client, "Why review code?")

    assert result == "Automated reviews catch defects early."
    client.chat.completions.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_generate_text_rejects_empty_prompt():
    client = SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(create=AsyncMock())
        )
    )

    with pytest.raises(ValueError, match="Prompt must not be empty"):
        await generate_text(client, "   ")

    client.chat.completions.create.assert_not_awaited()


@pytest.mark.asyncio
async def test_generate_text_rejects_empty_response():
    client = SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(
                create=AsyncMock(
                    return_value=SimpleNamespace(
                        choices=[
                            SimpleNamespace(
                                message=SimpleNamespace(content=None)
                            )
                        ]
                    )
                )
            )
        )
    )

    with pytest.raises(RuntimeError, match="empty response"):
        await generate_text(client, "Review this code")
