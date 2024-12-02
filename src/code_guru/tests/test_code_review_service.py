import pytest
from unittest.mock import AsyncMock, MagicMock
from src.code_guru.services import CodeReviewService
from src.code_guru.schemas import CodeReviewRequest, CodeReviewResponse


@pytest.fixture
def git_hub_service_mock():
    mock = MagicMock()
    mock.get_api_url_from_usual_url.return_value = (
        "https://api.github.com/repos/user/repo/contents/"
    )
    mock.get_files_info = AsyncMock(
        return_value={"file1.py": "print('Hello World')"}
    )
    return mock


@pytest.fixture
def groq_service_mock():
    mock = MagicMock()
    mock.get_bot_response.return_value = "Mocked Review Response"
    return mock


@pytest.fixture
def code_review_service(git_hub_service_mock, groq_service_mock):
    return CodeReviewService(
        git_hub_service=git_hub_service_mock,
        groq_ai_service=groq_service_mock
    )


@pytest.mark.asyncio
async def test_review_success(
    code_review_service,
    git_hub_service_mock,
    groq_service_mock
):
    url = "https://github.com/user/repo.git"
    candidate_level = "Junior"
    assignment_description = "Implement a REST API for a library system."

    request = CodeReviewRequest(
        github_repo_url=url,
        assignment_description=assignment_description,
        candidate_level=candidate_level
    )

    response = await code_review_service.review(code_review_request=request)

    assert isinstance(response, CodeReviewResponse)
    assert response.filenames == ["file1.py"]
    assert response.review_result == "Mocked Review Response"
    git_hub_service_mock.get_api_url_from_usual_url.assert_called_once_with(
        url
    )
    git_hub_service_mock.get_files_info.assert_called_once()
    groq_service_mock.get_bot_response.assert_called_once_with(
        assignment_description=assignment_description,
        candidate_level=candidate_level,
        files_info={"file1.py": "print('Hello World')"}
    )
