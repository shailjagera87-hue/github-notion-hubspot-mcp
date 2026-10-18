"""Groq model client and text generation."""

from groq import AsyncGroq

from enterprise_mcp.config import settings


def create_groq_client() -> AsyncGroq:
    """Create an asynchronous Groq client using validated application settings."""
    if not settings.groq_api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not configured. Set it in your local .env file."
        )

    api_key = settings.groq_api_key.get_secret_value()

    if not api_key or api_key == "your_groq_api_key_here":
        raise RuntimeError(
            "GROQ_API_KEY is missing or still contains the example placeholder."
        )

    return AsyncGroq(
        api_key=api_key,
        timeout=30.0,
        max_retries=2,
    )


async def generate_text(
    client: AsyncGroq,
    prompt: str,
    system_prompt: str = "You are a helpful engineering assistant.",
) -> str:
    """Generate text using the configured Groq model."""
    if not prompt.strip():
        raise ValueError("Prompt must not be empty.")

    response = await client.chat.completions.create(
        model=settings.groq_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )

    content = response.choices[0].message.content

    if not content:
        raise RuntimeError("Groq returned an empty response.")

    return content
