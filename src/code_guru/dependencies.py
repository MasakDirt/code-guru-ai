from fastapi import Depends
from groq import Groq
from redis.asyncio import Redis

from code_guru.interfaces import (
    CodeReviewServiceInterface,
    GitHubServiceInterface,
    GroqAIServiceInterface,
)
from code_guru.services import CodeReviewService, GitHubService, GroqAIService
from database.base import redis
from groq_ai.api import groq_api


def get_redis() -> Redis:
    return redis


def get_open_ai_api() -> Groq:
    return groq_api


def get_git_hub_service(
    redis: Redis = Depends(get_redis)
) -> GitHubServiceInterface:
    return GitHubService(redis=redis)


def get_chat_gpt_service(
    groq_api: Groq = Depends(get_open_ai_api)
) -> GroqAIServiceInterface:
    return GroqAIService(groq_api=groq_api)


def get_code_review_service(
    git_hub_service: GitHubServiceInterface = Depends(get_git_hub_service),
    groq_ai_service: GroqAIServiceInterface = Depends(get_chat_gpt_service)
) -> CodeReviewServiceInterface:
    return CodeReviewService(
        git_hub_service=git_hub_service,
        groq_ai_service=groq_ai_service
    )
