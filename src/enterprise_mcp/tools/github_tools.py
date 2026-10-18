
"""Read-only GitHub tools for repository intelligence."""

import re

from enterprise_mcp.integrations.github.client import (
    GitHubAPIError,
    create_github_client,
    github_get,
)


_REPOSITORY_NAME = re.compile(r"^[A-Za-z0-9_.-]+$")


def _validate_repository_name(owner: str, repo: str) -> None:
    """Reject malformed owner/repository names before making a request."""
    if not _REPOSITORY_NAME.fullmatch(owner) or owner in {".", ".."}:
        raise ValueError("Invalid GitHub owner name.")

    if not _REPOSITORY_NAME.fullmatch(repo) or repo in {".", ".."}:
        raise ValueError("Invalid GitHub repository name.")


async def get_repository(owner: str, repo: str) -> dict:
    """Get metadata for a GitHub repository."""
    _validate_repository_name(owner, repo)

    async with create_github_client() as client:
        data = await github_get(client, f"/repos/{owner}/{repo}")

    if not isinstance(data, dict):
        raise GitHubAPIError("GitHub returned an unexpected repository response.")

    license_data = data.get("license")

    return {
        "name": data.get("name"),
        "full_name": data.get("full_name"),
        "description": data.get("description"),
        "url": data.get("html_url"),
        "visibility": data.get("visibility"),
        "default_branch": data.get("default_branch"),
        "is_archived": data.get("archived"),
        "open_issues_count": data.get("open_issues_count"),
        "stars": data.get("stargazers_count"),
        "forks": data.get("forks_count"),
        "language": data.get("language"),
        "license": license_data.get("spdx_id") if isinstance(license_data, dict) else None,
    }


async def list_repository_issues(
    owner: str,
    repo: str,
    state: str = "open",
    limit: int = 10,
) -> dict:
    """List GitHub issues, excluding pull requests."""
    _validate_repository_name(owner, repo)

    if state not in {"open", "closed", "all"}:
        raise ValueError("state must be 'open', 'closed', or 'all'.")

    if not 1 <= limit <= 100:
        raise ValueError("limit must be between 1 and 100.")

    async with create_github_client() as client:
        data = await github_get(
            client,
            f"/repos/{owner}/{repo}/issues",
            params={
                "state": state,
                "per_page": limit,
                "page": 1,
                "sort": "updated",
                "direction": "desc",
            },
        )

    if not isinstance(data, list):
        raise GitHubAPIError("GitHub returned an unexpected issues response.")

    issues = []
    for item in data:
        if not isinstance(item, dict):
            continue

        # GitHub's issues endpoint also returns pull requests.
        if "pull_request" in item:
            continue

        user = item.get("user")
        labels = item.get("labels", [])

        issues.append(
            {
                "number": item.get("number"),
                "title": item.get("title"),
                "state": item.get("state"),
                "url": item.get("html_url"),
                "author": user.get("login") if isinstance(user, dict) else None,
                "labels": [
                    label.get("name")
                    for label in labels
                    if isinstance(label, dict) and isinstance(label.get("name"), str)
                ],
                "created_at": item.get("created_at"),
                "updated_at": item.get("updated_at"),
                "comments": item.get("comments"),
            }
        )

    return {
        "repository": f"{owner}/{repo}",
        "state_filter": state,
        "count": len(issues),
        "issues": issues,
    }

async def get_pull_request(
    owner: str,
    repo: str,
    pull_number: int,
) -> dict:
    """Get metadata and review status for a GitHub pull request."""
    _validate_repository_name(owner, repo)

    if pull_number < 1:
        raise ValueError("pull_number must be greater than zero.")

    async with create_github_client() as client:
        data = await github_get(
            client,
            f"/repos/{owner}/{repo}/pulls/{pull_number}",
        )

    if not isinstance(data, dict):
        raise GitHubAPIError("GitHub returned an unexpected pull request response.")

    user = data.get("user")
    head = data.get("head")
    base = data.get("base")
    head_repo = head.get("repo") if isinstance(head, dict) else None

    return {
        "number": data.get("number"),
        "title": data.get("title"),
        "body": data.get("body"),
        "state": data.get("state"),
        "url": data.get("html_url"),
        "author": user.get("login") if isinstance(user, dict) else None,
        "draft": data.get("draft"),
        "merged": data.get("merged"),
        "created_at": data.get("created_at"),
        "updated_at": data.get("updated_at"),
        "changed_files": data.get("changed_files"),
        "additions": data.get("additions"),
        "deletions": data.get("deletions"),
        "head_branch": head.get("ref") if isinstance(head, dict) else None,
        "head_repository": (
            head_repo.get("full_name") if isinstance(head_repo, dict) else None
        ),
        "base_branch": base.get("ref") if isinstance(base, dict) else None,
    }


async def list_pull_request_files(
    owner: str,
    repo: str,
    pull_number: int,
    limit: int = 30,
) -> dict:
    """List files changed by a GitHub pull request."""
    _validate_repository_name(owner, repo)

    if pull_number < 1:
        raise ValueError("pull_number must be greater than zero.")

    if not 1 <= limit <= 100:
        raise ValueError("limit must be between 1 and 100.")

    async with create_github_client() as client:
        data = await github_get(
            client,
            f"/repos/{owner}/{repo}/pulls/{pull_number}/files",
            params={"per_page": limit, "page": 1},
        )

    if not isinstance(data, list):
        raise GitHubAPIError("GitHub returned an unexpected pull request files response.")

    files = []
    for item in data:
        if not isinstance(item, dict):
            continue

        files.append(
            {
                "filename": item.get("filename"),
                "status": item.get("status"),
                "additions": item.get("additions"),
                "deletions": item.get("deletions"),
                "changes": item.get("changes"),
                "patch": item.get("patch"),
                "url": item.get("blob_url"),
            }
        )

    return {
        "repository": f"{owner}/{repo}",
        "pull_number": pull_number,
        "count": len(files),
        "files": files,
    }
