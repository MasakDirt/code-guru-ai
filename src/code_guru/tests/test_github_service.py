import base64
import time

import pytest
from unittest.mock import AsyncMock
from httpx import Response
from code_guru.services import GitHubService, GitHubError


@pytest.fixture
def redis_mock():
    return AsyncMock()


@pytest.fixture
def client_mock():
    return AsyncMock()


@pytest.fixture
def github_service(redis_mock):
    return GitHubService(redis=redis_mock)


@pytest.mark.asyncio
async def test_get_api_url_from_usual_url(github_service):
    usual_url = "https://github.com/user/repo.git"
    expected_url = "https://api.github.com/repos/user/repo/contents/"

    result = github_service.get_api_url_from_usual_url(usual_url)

    assert result == expected_url


@pytest.mark.asyncio
async def test_ensure_rate_limit_no_limit_exceeded(github_service, redis_mock):
    redis_mock.get.side_effect = lambda key: {
        "github_rate_remaining": "10",
        "github_rate_reset": "0"
    }.get(key)

    message = await github_service._ensure_rate_limit()

    assert message is None


@pytest.mark.asyncio
async def test_ensure_rate_limit_limit_exceeded(github_service, redis_mock):
    redis_mock.get.side_effect = lambda key: {
        "github_rate_remaining": "0",
        "github_rate_reset": str(int(time.time()) + 60)
    }.get(key)

    message = await github_service._ensure_rate_limit()
    assert message.startswith("Rate limit exceeded.")


@pytest.mark.asyncio
async def test_get_github_response_content_success(
    github_service,
    client_mock,
    redis_mock
):
    url = "https://api.github.com/repos/user/repo/contents/"
    response_data = {"status": 200, "content": {"key": "value"}}
    client_mock.get.return_value = Response(200, json=response_data)

    result = await github_service._get_github_response_content(
        client=client_mock,
        url=url
    )

    assert result["content"] == response_data["content"]


@pytest.mark.asyncio
async def test_get_github_response_content_error(github_service, client_mock):
    url = "https://api.github.com/repos/user/repo/contents/"
    response_data = {"status": 403, "message": "Forbidden"}
    client_mock.get.return_value = Response(403, json=response_data)

    with pytest.raises(GitHubError):
        await github_service._get_github_response_content(
            client=client_mock,
            url=url
        )


@pytest.mark.asyncio
async def test_get_files_info_cache_hit(github_service, redis_mock):
    url = "https://api.github.com/repos/user/repo/contents/"

    redis_mock.get.side_effect = lambda key: {
        "github_rate_remaining": "10",
        "github_rate_reset": str(int(time.time()) + 60),
        f"files_info:{url}:None": str({"file1": "content1"})
    }.get(key)

    result = await github_service.get_files_info(client=AsyncMock(), url=url)
    assert result == {"file1": "content1"}


@pytest.mark.asyncio
async def test_get_files_info_no_cache(
    github_service, client_mock, redis_mock
):
    url = "https://api.github.com/repos/user/repo/contents/"
    redis_mock.get.return_value = None
    client_mock.get.return_value = Response(
        200, json=[
            {
                "type": "file",
                "name": "file1",
                "url": "file_url"
            }
        ]
    )
    github_service._get_file_content = AsyncMock(return_value="content1")

    result = await github_service.get_files_info(client=client_mock, url=url)

    assert result == {"file1": "content1"}


@pytest.mark.asyncio
async def test_get_file_content_cache_hit(github_service, redis_mock):
    file_url = "https://api.github.com/repos/user/repo/contents/file1"
    redis_mock.get.return_value = "cached_content"

    result = await github_service._get_file_content(
        client=AsyncMock(),
        item_data={"url": file_url}
    )

    assert result == "cached_content"


@pytest.mark.asyncio
async def test_get_file_content_no_cache(
    github_service,
    client_mock,
    redis_mock
):
    file_url = "https://api.github.com/repos/user/repo/contents/file1"
    file_data = {"content": base64.b64encode(b"file_content").decode("utf-8")}
    redis_mock.get.return_value = None
    client_mock.get.return_value = Response(200, json=file_data)

    result = await github_service._get_file_content(
        client=client_mock,
        item_data={"url": file_url}
    )

    assert result == "file_content"
