import asyncio
from uuid import uuid4

from aiogram import Router
from aiogram.types import (
    ChosenInlineResult,
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
)
from cachetools import TTLCache

from notes.jobs import CreateNoteJob
from notes.settings import NOTION_DB_ID
from notes.telegram.middlewares import InlineLoggingMiddleware
from notes.telegram.utils import enqueue_job

_INLINE_CACHE = TTLCache(maxsize=10_000, ttl=300)

inline_router = Router(name=__name__)
inline_router.inline_query.middleware(InlineLoggingMiddleware())


@inline_router.inline_query()
async def inline_save_note(query: InlineQuery) -> None:
    note = (query.query or "").strip()
    if not note:
        await query.answer(results=[], cache_time=0, is_personal=True)
        return

    result_id = str(uuid4())
    _INLINE_CACHE[result_id] = note

    result = InlineQueryResultArticle(
        id=result_id,
        title="💾 Сохранить заметку",
        description=note[:100],
        input_message_content=InputTextMessageContent(message_text=f"💾: {note}"),
    )

    await query.answer(
        results=[result],
        cache_time=0,
        is_personal=True,
    )


@inline_router.chosen_inline_result()
async def on_chosen(result: ChosenInlineResult, queue: asyncio.Queue) -> None:
    note = _INLINE_CACHE.pop(result.result_id, None)
    if not note:
        return

    job = CreateNoteJob(
        database_id=NOTION_DB_ID,  # type: ignore[invalid-argument-type]
        text=note,
        user_id=result.from_user.id,
        result_id=result.result_id,
    )

    meta = f"user_id={result.from_user.id} result_id={result.result_id}"

    ok = enqueue_job(job=job, queue=queue, meta=meta)

    if not ok:
        _INLINE_CACHE[result.result_id] = note
