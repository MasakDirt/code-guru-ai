from pydantic import BaseModel, field_validator

from code_guru.validators import validate_candidate_level


class CodeReviewRequest(BaseModel):
    assignment_description: str
    github_repo_url: str
    candidate_level: str

    @field_validator("candidate_level")
    @classmethod
    def validate_username_field(cls, candidate_level: str) -> str:
        validate_candidate_level(candidate_level)
        return candidate_level


class CodeReviewResponse(BaseModel):
    filenames: list[str]
    review_result: str
