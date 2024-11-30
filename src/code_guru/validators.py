import re

from settings import CANDIDATE_LEVELS


def validate_candidate_level(candidate_level: str) -> None:
    if candidate_level not in CANDIDATE_LEVELS:
        raise ValueError(
            f"Candidate level must be "
            f"one of those - {', '.join(CANDIDATE_LEVELS)}"
        )


def validate_github_repo_url(github_repo_url: str) -> None:
    pattern = re.compile(
        r"^https://github\.com/[^/]+/[^/]+\.git$"
    )
    if not pattern.match(github_repo_url):
        raise ValueError("Invalid GitHub URL!")
