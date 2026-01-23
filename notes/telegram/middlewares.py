from collections.abc import Awaitable, Callable
from typing import Any, cast

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User

from notes.settings import logger_tg
from notes.telegram.errors import WhitelistDenyError
from notes.utils import clear_log_context, set_log_context


class ErrorMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        try:
            return await handler(event, data)
        except Exception as exc:
            raw_user = data.get("event_from_user")

            if isinstance(raw_user, User):
                user: User | None = raw_user
            else:
                user = None

            logger_tg.exception(
                "HANDLER ERROR | event=%s | user_id=%s | username=%s | err=%s",
                type(event).__name__,
                user.id if user else None,
                user.username if user else None,
                exc,
            )
            raise


class WhitelistMiddleware(BaseMiddleware):
    def __init__(self, allowed_user_ids: set[int] | None) -> None:
        self.whitelist = allowed_user_ids

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        raw_user = data.get("event_from_user")

        if raw_user is None:
            return await handler(event, data)

        user = cast(User, raw_user)

        if not self.whitelist:
            return await handler(event, data)

        if user.id in self.whitelist:
            return await handler(event, data)

        raise WhitelistDenyError


class LogContextMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        raw_user = data.get("event_from_user")
        user_id = raw_user.id if isinstance(raw_user, User) else None
        update_id = getattr(event, "update_id", None)

        set_log_context(user_id=user_id, update_id=update_id)
        try:
            return await handler(event, data)
        finally:
            clear_log_context()
