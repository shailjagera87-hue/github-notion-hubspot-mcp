"""Manually verify access to the configured Groq model."""

import asyncio

from enterprise_mcp.llm.client import create_groq_client, generate_text


async def main() -> None:
    async with create_groq_client() as client:
        answer = await generate_text(
            client,
            "In one sentence, explain why automated code reviews are useful.",
        )
        print(answer)


if __name__ == "__main__":
    asyncio.run(main())
