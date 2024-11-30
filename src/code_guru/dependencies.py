from redis.asyncio import Redis
from fastapi import Depends

from code_guru.interfaces import (
    CodeReviewServiceInterface,
    GitHubServiceInterface,
)
from code_guru.services import CodeReviewService, GitHubService
from database.base import redis


def get_redis() -> Redis:
    return redis


def get_git_hub_service(
    redis: Redis = Depends(get_redis)
) -> GitHubServiceInterface:
    return GitHubService(redis=redis)


def get_code_review_service(
    git_hub_service: GitHubServiceInterface = Depends(get_git_hub_service)
) -> CodeReviewServiceInterface:
    return CodeReviewService(git_hub_service=git_hub_service)
