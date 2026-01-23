from unittest.mock import AsyncMock

import pytest

from notes.notion.client import NotionClient
from notes.notion.schemas import DatabaseParent, UserListResponse
from notes.notion.wrapper import NotionWrapper, setup_notion_connection


class TestNotionWrapper:
    @pytest.fixture
    def mock_client(self) -> AsyncMock:
        return AsyncMock(spec=NotionClient)

    @pytest.fixture
    def wrapper(self, mock_client: AsyncMock) -> NotionWrapper:
        return NotionWrapper(client=mock_client)

    @pytest.mark.asyncio
    async def test_get_users(
        self, wrapper: NotionWrapper, mock_client: AsyncMock
    ) -> None:
        expected_response = UserListResponse(
            object="list",
            results=[],
            has_more=False,
        )
        mock_client.get_users.return_value = expected_response

        result = await wrapper.get_users(page_size=10)

        assert result == expected_response
        mock_client.get_users.assert_called_once_with(page_size=10)

    @pytest.mark.asyncio
    async def test_create_note(
        self, wrapper: NotionWrapper, mock_client: AsyncMock
    ) -> None:
        mock_client.create_page.return_value = {"id": "page-123"}

        await wrapper.create_note(database_id="db-456", note="Test note")

        mock_client.create_page.assert_called_once()
        call_kwargs = mock_client.create_page.call_args.kwargs

        assert isinstance(call_kwargs["parent"], DatabaseParent)
        assert call_kwargs["parent"].database_id == "db-456"
        assert call_kwargs["title"] == "Test note"

    @pytest.mark.asyncio
    async def test_create_note_with_special_characters(
        self, wrapper: NotionWrapper, mock_client: AsyncMock
    ) -> None:
        mock_client.create_page.return_value = {"id": "page-123"}

        note_with_special = "Note with émojis and спец символы"
        await wrapper.create_note(database_id="db-789", note=note_with_special)

        call_kwargs = mock_client.create_page.call_args.kwargs
        assert call_kwargs["title"] == note_with_special


class TestSetupNotionConnection:
    @pytest.mark.asyncio
    async def test_setup_notion_connection_success(self, mocker) -> None:
        mock_client_class = mocker.patch("notes.notion.wrapper.NotionClient")
        mock_client_instance = AsyncMock()
        mock_client_instance.get_users.return_value = UserListResponse(
            object="list",
            results=[],
            has_more=False,
        )
        mock_client_class.return_value = mock_client_instance

        wrapper = await setup_notion_connection(token="test-token")

        assert isinstance(wrapper, NotionWrapper)
        mock_client_class.assert_called_once_with(token="test-token")
        mock_client_instance.get_users.assert_called_once_with(page_size=1)

    @pytest.mark.asyncio
    async def test_setup_notion_connection_auth_failure(self, mocker) -> None:
        from notes.notion.errors import NotionAuthError

        mock_client_class = mocker.patch("notes.notion.wrapper.NotionClient")
        mock_client_instance = AsyncMock()
        mock_client_instance.get_users.side_effect = NotionAuthError("Invalid token")
        mock_client_class.return_value = mock_client_instance

        with pytest.raises(NotionAuthError):
            await setup_notion_connection(token="invalid-token")
