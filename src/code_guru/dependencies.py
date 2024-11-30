from fastapi import Depends

from code_guru.interfaces import (
    CodeReviewServiceInterface,
    GitHubServiceInterface,
)
from code_guru.services import CodeReviewService, GitHubService


def get_git_hub_service() -> GitHubServiceInterface:
    return GitHubService()


def get_code_review_service(
    git_hub_service: GitHubServiceInterface = Depends(get_git_hub_service)
) -> CodeReviewServiceInterface:
    return CodeReviewService(git_hub_service=git_hub_service)
