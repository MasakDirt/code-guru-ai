from pydantic import BaseModel, field_validator

from code_guru.validators import (
    validate_candidate_level,
    validate_github_repo_url,
)


class CodeReviewRequest(BaseModel):
    assignment_description: str
    github_repo_url: str
    candidate_level: str

    @field_validator("candidate_level")
    @classmethod
    def validate_candidate_level(cls, candidate_level: str) -> str:
        validate_candidate_level(candidate_level)
        return candidate_level

    @field_validator("github_repo_url")
    @classmethod
    def validate_github_repo_url(cls, github_repo_url: str) -> str:
        validate_github_repo_url(github_repo_url)
        return github_repo_url


class CodeReviewResponse(BaseModel):
    filenames: list[str]
    review_result: str
