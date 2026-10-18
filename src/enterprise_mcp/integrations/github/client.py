
"""Shared asynchronous GitHub REST API client."""

import httpx

from enterprise_mcp.config import settings

GITHUB_API_VERSION = "2022-11-28"


class GitHubAPIError(RuntimeError):
    """Raised when the GitHub API request fails."""


def create_github_client() -> httpx.AsyncClient:
    """Create an authenticated GitHub API client."""
    if not settings.github_token:
        raise RuntimeError(
            "GITHUB_TOKEN is not configured. Set it in your local .env file."
        )

    token = settings.github_token.get_secret_value().strip()

    if not token or token == "replace_with_your_github_token":
        raise RuntimeError(
            "GITHUB_TOKEN is missing or still contains the example placeholder."
        )

    return httpx.AsyncClient(
        base_url=settings.github_api_base_url.rstrip("/"),
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": GITHUB_API_VERSION,
        },
        timeout=httpx.Timeout(15.0, connect=5.0),
    )


async def github_get(
    client: httpx.AsyncClient,
    path: str,
    *,
    params: dict[str, str | int] | None = None,
) -> dict | list:
    """Perform a GET request and return decoded JSON."""
    try:
        response = await client.get(path, params=params)
    except httpx.TimeoutException as exc:
        raise GitHubAPIError("GitHub API request timed out.") from exc
    except httpx.RequestError as exc:
        raise GitHubAPIError("Could not connect to the GitHub API.") from exc

    if response.status_code == 401:
        raise GitHubAPIError(
            "GitHub authentication failed. Check that GITHUB_TOKEN is valid."
        )

    if response.status_code == 403:
        raise GitHubAPIError(
            "GitHub denied the request. Check token permissions, organization "
            "approval, and API rate limits."
        )

    if response.status_code == 404:
        raise GitHubAPIError(
            "GitHub resource not found or not accessible to this token."
        )

    if response.status_code >= 400:
        raise GitHubAPIError(
            f"GitHub API returned HTTP {response.status_code}."
        )

    try:
        data = response.json()
    except ValueError as exc:
        raise GitHubAPIError("GitHub returned an invalid JSON response.") from exc

    if not isinstance(data, (dict, list)):
        raise GitHubAPIError("GitHub returned an unexpected response format.")

    return data
