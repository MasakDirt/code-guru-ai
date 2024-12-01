import base64
import logging
import time
from typing import Optional

from groq import APIStatusError, Groq
from httpx import AsyncClient
from redis.asyncio import Redis

from code_guru.exceptions import ChatBotError, GitHubError
from code_guru.interfaces import (
    CodeReviewServiceInterface,
    GitHubServiceInterface,
    GroqAIServiceInterface,
)
from code_guru.schemas import CodeReviewRequest, CodeReviewResponse
from settings import GITHUB_API_TOKEN


logger = logging.getLogger("uvicorn.error")


class CodeReviewService(CodeReviewServiceInterface):
    def __init__(
        self, git_hub_service: GitHubServiceInterface,
        groq_ai_service: GroqAIServiceInterface
    ):
        self._git_hub_service = git_hub_service
        self._groq_ai_service = groq_ai_service

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
        review_result = self._groq_ai_service.get_bot_response(
            assignment_description=code_review_request.assignment_description,
            candidate_level=code_review_request.candidate_level,
            files_info=files_info
        )

        return CodeReviewResponse(
            filenames=files_info.keys(),
            review_result=review_result
        )


class GitHubService(GitHubServiceInterface):
    def __init__(self, redis: Redis):
        self._redis = redis

    def get_api_url_from_usual_url(self, usual_url: str) -> str:
        username, repo_name = usual_url.rstrip("/").split("/")[-2:]
        repo_name = repo_name.removesuffix(".git")

        return f"https://api.github.com/repos/{username}/{repo_name}/contents/"

    async def _ensure_rate_limit(self) -> Optional[str]:
        remaining = await self._redis.get("github_rate_remaining")
        reset_time = await self._redis.get("github_rate_reset")
        if remaining is not None and int(remaining) == 0:
            sleep_time = int(reset_time) - int(time.time())
            if sleep_time > 0:
                message = (
                    f"Rate limit exceeded. "
                    f"Sleeping for {sleep_time} seconds."
                )
                logger.info(message)

                return message

    async def _get_github_response_content(
        self, client: AsyncClient,
        url: str
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
            message = content["message"]
            logger.error(
                f"GitHubAPI response error, status - {status} |"
                f" message - '{message}' on url - {url}"
            )
            raise GitHubError(
                status_code=status,
                message=f"GitHub API error, detailed: '{message}'"
            )

        remaining = int(response.headers.get("X-RateLimit-Remaining", 0))
        reset_time = int(
            response.headers.get("X-RateLimit-Reset", time.time())
        )

        await self._redis.set(
            "github_rate_remaining",
            remaining,
            ex=reset_time - int(time.time())
        )
        await self._redis.set(
            "github_rate_reset",
            reset_time,
            ex=reset_time - int(time.time())
        )

        return content

    async def get_files_info(
        self, client: AsyncClient,
        url: str,
        parent_dir: Optional[str] = None
    ) -> dict[str, str]:
        rate_limit_message = await self._ensure_rate_limit()
        if rate_limit_message is not None:
            return {"detail": rate_limit_message}

        cache_key = f"files_info:{url}:{parent_dir}"
        cached_content = await self._redis.get(cache_key)

        if cached_content:
            logger.info(f"Cache hit for {cache_key}")
            return eval(cached_content)

        content = await self._get_github_response_content(
            client=client,
            url=url
        )

        files_info = await self._find_files_info(
            client=client,
            content=content,
            parent_dir=parent_dir
        )
        await self._redis.set(cache_key, str(files_info))

        return files_info

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

    async def _get_file_content(
        self, client: AsyncClient,
        item_data: dict
    ) -> str:
        cache_key = f"file_content:{item_data['url']}"
        cached_content = await self._redis.get(cache_key)

        if cached_content:
            return cached_content

        file_data = await self._get_github_response_content(
            client=client,
            url=item_data["url"]
        )

        try:
            content = base64.b64decode(file_data["content"]).decode("utf-8")
        except UnicodeDecodeError:
            content = file_data["name"]

        await self._redis.set(cache_key, content)
        return content


class GroqAIService(GroqAIServiceInterface):
    def __init__(self, groq_api: Groq):
        self._groq_api = groq_api

    def get_bot_response(
        self, assignment_description: str,
        candidate_level: str,
        files_info: dict[str, str]
    ) -> str:
        system_prompt = f"""
        You are a professional Code Reviewer, tasked with reviewing code 
        quality for a {candidate_level} developer. Users will provide you with:
        1. An **assignment description** outlining the task requirements.
        2. A dictionary containing the **content of files** in the format:
           - `dict[filename: content, filename: content, ...]`.

        Your job is to analyze the provided code and assignment description, 
        then deliver a detailed, structured review.

        Your response must follow this exact format:
        1. **Downsides**:
           - List and describe specific downsides or issues with the project 
           (e.g., poor structure, lack of comments, security risks).
        2. **Rating**:
           - Provide an overall rating for the code, considering the expected 
           level of a {candidate_level} developer (e.g., "Rating: 3/5").
        3. **Thoughts**:
           - Share your overall thoughts and suggestions on the repository, 
           focusing on areas for improvement and strengths.

        Be constructive and provide actionable feedback to help the developer 
        improve. Ensure your feedback is specific and considers the provided 
        code and its context.
        """

        user_prompt = f"""
        1. Assigment description - {assignment_description}
        2. Content of files - {files_info}
        """

        try:
            completion = self._groq_api.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ]
            )
        except APIStatusError as exc:
            status = exc.status_code
            message = exc.body["error"]["message"]
            logger.error(
                f"ChatBotAPI response error, status - {status} |"
                f" message - '{message}'"
            )
            raise ChatBotError(
                status_code=status,
                message=message
            )

        return completion.choices[0].message.content
