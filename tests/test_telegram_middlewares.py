from unittest.mock import AsyncMock, MagicMock

import pytest

from notes.telegram.errors import WhitelistDenyError
from notes.telegram.middlewares import (
    ErrorMiddleware,
    LogContextMiddleware,
    WhitelistMiddleware,
)


class TestWhitelistMiddleware:
    @pytest.fixture
    def handler(self) -> AsyncMock:
        return AsyncMock(return_value="handler_result")

    @pytest.fixture
    def event(self) -> MagicMock:
        return MagicMock()

    @pytest.fixture
    def mock_user(self) -> MagicMock:
        user = MagicMock()
        user.id = 123456
        user.username = "testuser"
        return user

    @pytest.mark.asyncio
    async def test_whitelist_allows_user_in_list(
        self, handler: AsyncMock, event: MagicMock, mock_user: MagicMock
    ) -> None:
        middleware = WhitelistMiddleware(allowed_user_ids={123456})
        data = {"event_from_user": mock_user}

        result = await middleware(handler, event, data)

        assert result == "handler_result"
        handler.assert_called_once()

    @pytest.mark.asyncio
    async def test_whitelist_allows_when_none(
        self, handler: AsyncMock, event: MagicMock, mock_user: MagicMock
    ) -> None:
        middleware = WhitelistMiddleware(allowed_user_ids=None)
        data = {"event_from_user": mock_user}

        result = await middleware(handler, event, data)

        assert result == "handler_result"
        handler.assert_called_once()

    @pytest.mark.asyncio
    async def test_whitelist_allows_when_empty_set(
        self, handler: AsyncMock, event: MagicMock, mock_user: MagicMock
    ) -> None:
        middleware = WhitelistMiddleware(allowed_user_ids=set())
        data = {"event_from_user": mock_user}

        result = await middleware(handler, event, data)

        assert result == "handler_result"
        handler.assert_called_once()

    @pytest.mark.asyncio
    async def test_whitelist_allows_when_no_user(
        self, handler: AsyncMock, event: MagicMock
    ) -> None:
        middleware = WhitelistMiddleware(allowed_user_ids={123456})
        data = {"event_from_user": None}

        result = await middleware(handler, event, data)

        assert result == "handler_result"

    @pytest.mark.asyncio
    async def test_whitelist_denies_user_not_in_list(
        self, handler: AsyncMock, event: MagicMock, mock_user: MagicMock
    ) -> None:
        middleware = WhitelistMiddleware(allowed_user_ids={999999})
        data = {"event_from_user": mock_user}

        with pytest.raises(WhitelistDenyError):
            await middleware(handler, event, data)


class TestErrorMiddleware:
    @pytest.fixture
    def middleware(self) -> ErrorMiddleware:
        return ErrorMiddleware()

    @pytest.fixture
    def handler(self) -> AsyncMock:
        return AsyncMock(return_value="success")

    @pytest.fixture
    def event(self) -> MagicMock:
        return MagicMock()

    @pytest.mark.asyncio
    async def test_passes_through_on_success(
        self, middleware: ErrorMiddleware, handler: AsyncMock, event: MagicMock
    ) -> None:
        data = {"event_from_user": None}

        result = await middleware(handler, event, data)

        assert result == "success"

    @pytest.mark.asyncio
    async def test_logs_and_reraises_exception(
        self, middleware: ErrorMiddleware, handler: AsyncMock, event: MagicMock
    ) -> None:
        handler.side_effect = ValueError("Test error")
        data = {"event_from_user": None}

        with pytest.raises(ValueError, match="Test error"):
            await middleware(handler, event, data)

    @pytest.mark.asyncio
    async def test_logs_user_info_on_error(
        self,
        middleware: ErrorMiddleware,
        handler: AsyncMock,
        event: MagicMock,
        mock_user: MagicMock,
    ) -> None:
        handler.side_effect = RuntimeError("Handler failed")
        data = {"event_from_user": mock_user}

        with pytest.raises(RuntimeError):
            await middleware(handler, event, data)


class TestLogContextMiddleware:
    @pytest.fixture
    def middleware(self) -> LogContextMiddleware:
        return LogContextMiddleware()

    @pytest.fixture
    def handler(self) -> AsyncMock:
        return AsyncMock(return_value="result")

    @pytest.fixture
    def event(self) -> MagicMock:
        event = MagicMock()
        event.update_id = 12345
        return event

    @pytest.mark.asyncio
    async def test_sets_and_clears_context(
        self,
        middleware: LogContextMiddleware,
        handler: AsyncMock,
        event: MagicMock,
        mock_user: MagicMock,
    ) -> None:
        data = {"event_from_user": mock_user}

        result = await middleware(handler, event, data)

        assert result == "result"
        handler.assert_called_once()

    @pytest.mark.asyncio
    async def test_clears_context_on_exception(
        self,
        middleware: LogContextMiddleware,
        handler: AsyncMock,
        event: MagicMock,
    ) -> None:
        handler.side_effect = ValueError("Error")
        data = {"event_from_user": None}

        with pytest.raises(ValueError):
            await middleware(handler, event, data)

        # Context should still be cleared even after exception
