from abc import abstractmethod, ABC

from httpx import AsyncClient

from code_guru.schemas import CodeReviewRequest, CodeReviewResponse


class CodeReviewServiceInterface(ABC):
    @abstractmethod
    async def review(
        self, code_review_request: CodeReviewRequest
    ) -> CodeReviewResponse:
        pass


class GitHubServiceInterface(ABC):
    @abstractmethod
    def get_api_url_from_usual_url(self, usual_url: str) -> str:
        pass

    @abstractmethod
    async def get_files_info(
        self, client: AsyncClient,
        url: str
    ) -> dict[str, str]:
        pass


class GroqAIServiceInterface(ABC):
    @abstractmethod
    def get_bot_response(
        self, assignment_description: str,
        candidate_level: str,
        files_info: dict[str, str]
    ) -> str:
        pass
