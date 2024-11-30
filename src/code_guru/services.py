import base64
import logging
from typing import Optional

from httpx import AsyncClient

from code_guru.api_responses import get_github_response_content
from code_guru.interfaces import (
    CodeReviewServiceInterface,
    GitHubServiceInterface,
)
from code_guru.schemas import CodeReviewRequest, CodeReviewResponse


logger = logging.getLogger("uvicorn.error")


class CodeReviewService(CodeReviewServiceInterface):
    def __init__(self, git_hub_service: GitHubServiceInterface):
        self._git_hub_service = git_hub_service

    async def review(
        self, code_review_request: CodeReviewRequest
    ) -> CodeReviewResponse:
        async with AsyncClient() as client:
            files_info = await self._git_hub_service.get_files_info(
                client=client,
                url=self._git_hub_service.get_api_url_from_usual_url(
                    code_review_request.github_repo_url
                )
            )
            logger.info(
                f"Got all files for -"
                f" {code_review_request.github_repo_url}"
            )

        return CodeReviewResponse(
            filenames=files_info.keys(),
            review_result=""
        )


class GitHubService(GitHubServiceInterface):
    def get_api_url_from_usual_url(self, usual_url: str) -> str:
        username, repo_name = usual_url.rstrip("/").split("/")[-2:]
        repo_name = repo_name.removesuffix(".git")

        return f"https://api.github.com/repos/{username}/{repo_name}/contents/"

    async def get_files_info(
        self, client: AsyncClient,
        url: str,
        parent_dir: Optional[str] = None
    ) -> dict[str, str]:
        content = await get_github_response_content(
            client=client,
            url=url,
            logger=logger
        )

        return await self._find_files_info(
            client=client,
            content=content,
            parent_dir=parent_dir
        )

    async def _find_files_info(
        self, client: AsyncClient,
        content: dict,
        parent_dir: Optional[str] = None
    ) -> dict[str, str]:
        files = {}
        for item in content:
            if item["type"] == "dir":
                sub_dir_path = (
                    f"{parent_dir}/{item['name']}"
                    if parent_dir else item["name"]
                )
                files.update(
                    await self.get_files_info(
                        client=client,
                        url=item["url"],
                        parent_dir=sub_dir_path
                    )
                )
            else:
                files[
                    f"{parent_dir}/{item['name']}"
                    if parent_dir else item["name"]
                ] = await self._get_file_content(client, item)

        return files

    @classmethod
    async def _get_file_content(
        cls, client: AsyncClient,
        item_data: dict
    ) -> str:
        file_data = await get_github_response_content(
            client=client,
            url=item_data["url"],
            logger=logger
        )

        try:
            return base64.b64decode(file_data["content"]).decode("utf-8")
        except UnicodeDecodeError:
            return file_data["name"]
