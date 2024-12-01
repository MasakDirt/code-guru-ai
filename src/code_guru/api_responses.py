import time
from logging import Logger

from httpx import AsyncClient

from code_guru.exceptions import GitHubError
from settings import GITHUB_API_TOKEN

