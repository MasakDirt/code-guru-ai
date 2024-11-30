from logging import Logger

from httpx import AsyncClient

from code_guru.exceptions import GitHubError
from settings import GITHUB_API_TOKEN


async def get_github_response_content(
    client: AsyncClient,
    url: str,
    logger: Logger
) -> dict:
    response = await client.get(
        url=url,
        headers={
            "Authorization": f"Bearer {GITHUB_API_TOKEN}"
        }
    )
    content = response.json()

    if response.is_error:
        status = int(content["status"])
        message = content['message']
        logger.error(
            f"GitHubAPI response error, status - {status} |"
            f" message - '{message}' on url - {url}"
        )
        raise GitHubError(
            status_code=status,
            message=f"GitHub API error, detailed: '{message}'"
        )

    return content
