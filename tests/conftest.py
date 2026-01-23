import asyncio
from collections.abc import Generator
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from notes.jobs import CreateNoteJob
from notes.notion.client import NotionClient
from notes.notion.wrapper import NotionWrapper


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def job_queue() -> asyncio.Queue[CreateNoteJob]:
    return asyncio.Queue(maxsize=5)


@pytest.fixture
def sample_job() -> CreateNoteJob:
    return CreateNoteJob(
        database_id="test-db-id",
        text="Test note content",
        user_id=123456,
        result_id="test-result-id",
    )


@pytest.fixture
def mock_httpx_client() -> AsyncMock:
    client = AsyncMock(spec=httpx.AsyncClient)
    return client


@pytest.fixture
def mock_notion_client(mock_httpx_client: AsyncMock) -> NotionClient:
    client = NotionClient(token="test-token")
    client._client = mock_httpx_client
    return client


@pytest.fixture
def mock_notion_wrapper(mock_notion_client: NotionClient) -> NotionWrapper:
    return NotionWrapper(client=mock_notion_client)


@pytest.fixture
def mock_user() -> MagicMock:
    user = MagicMock()
    user.id = 123456
    user.username = "testuser"
    return user
