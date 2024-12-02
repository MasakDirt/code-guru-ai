import pytest

from src.code_guru.validators import (
    validate_candidate_level,
    validate_github_repo_url,
)


CANDIDATE_LEVELS = {"junior", "mid", "senior", "lead"}


@pytest.mark.parametrize(
    "candidate_level",
    ["junior", "mid", "senior", "lead"]
)
def test_validate_candidate_level_valid(candidate_level, monkeypatch):
    monkeypatch.setattr(
        "src.code_guru.validators.CANDIDATE_LEVELS",
        CANDIDATE_LEVELS
    )
    validate_candidate_level(candidate_level)


@pytest.mark.parametrize(
    "candidate_level",
    ["intern", "expert", "juniors", "mid-level"]
)
def test_validate_candidate_level_invalid(candidate_level, monkeypatch):
    monkeypatch.setattr(
        "src.code_guru.validators.CANDIDATE_LEVELS",
        CANDIDATE_LEVELS
    )

    with pytest.raises(ValueError) as exc_info:
        validate_candidate_level(candidate_level)
    assert (
               f"Candidate level must be one of those - "
               f"{', '.join(CANDIDATE_LEVELS)}"
           ) in str(exc_info.value)


@pytest.mark.parametrize(
    "github_repo_url",
    [
        "https://github.com/user/repo.git",
        "https://github.com/some-user/some-repo.git",
    ]
)
def test_validate_github_repo_url_valid(github_repo_url):
    validate_github_repo_url(github_repo_url)


@pytest.mark.parametrize(
    "github_repo_url",
    [
        "https://github.com/user/repo",
        "https://github.com/user/repo/",
        "http://github.com/user/repo.git",
        "https://gitlab.com/user/repo.git",
        "https://github.com/user",
    ]
)
def test_validate_github_repo_url_invalid(github_repo_url):
    with pytest.raises(ValueError) as exc_info:
        validate_github_repo_url(github_repo_url)
    assert "Invalid GitHub URL!" in str(exc_info.value)
