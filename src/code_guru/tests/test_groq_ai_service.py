from unittest.mock import MagicMock

import pytest
from groq import APIStatusError

from src.code_guru.exceptions import ChatBotError
from src.code_guru.services import GroqAIService


@pytest.fixture
def groq_api_mock():
    groq_mock = MagicMock()
    groq_mock.chat.completions.create.return_value = MagicMock(
        choices=[
            MagicMock(message=MagicMock(content="Mocked Review Response"))]
    )
    return groq_mock


@pytest.fixture
def groq_service(groq_api_mock):
    return GroqAIService(groq_api=groq_api_mock)


def test_get_bot_response_success(groq_service, groq_api_mock):
    assignment_description = "Implement a REST API for a library system."
    candidate_level = "Junior"
    files_info = {"file1.py": "print('Hello World')"}

    response = groq_service.get_bot_response(
        assignment_description=assignment_description,
        candidate_level=candidate_level,
        files_info=files_info
    )

    assert response == "Mocked Review Response"
    groq_api_mock.chat.completions.create.assert_called_once()


def test_get_bot_response_api_error(groq_service, groq_api_mock):
    message = "Internal Server Error"

    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.json.return_value = {"error": {"message": message}}

    groq_api_mock.chat.completions.create.side_effect = APIStatusError(
        response=mock_response,
        body={"error": {"message": message}},
        message="Internal Server Error"
    )

    assignment_description = "Implement a REST API for a library system."
    candidate_level = "junior"
    files_info = {"file1.py": "print('Hello World')"}

    with pytest.raises(ChatBotError) as exc_info:
        groq_service.get_bot_response(
            assignment_description=assignment_description,
            candidate_level=candidate_level,
            files_info=files_info
        )

    assert exc_info.value.status_code == 500
    assert exc_info.value.message == message
