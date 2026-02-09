import asyncio

from aiogram import F, Router
from aiogram.types import Message

from notes.jobs import CreateNoteJob
from notes.settings import NOTION_DB_ID
from notes.telegram.middlewares import LogContextMiddleware
from notes.telegram.utils import enqueue_job

message_router = Router(name=__name__)
message_router.message.middleware(LogContextMiddleware())


@message_router.message(F.chat.type == "private", F.text)
async def save_private_message_as_note(message: Message, queue: asyncio.Queue) -> None:
    text = (message.text or "").strip()
    if not text:
        return

    user = message.from_user
    if user is None:
        return

    job = CreateNoteJob(
        database_id=NOTION_DB_ID,  # type: ignore[invalid-argument-type]
        text=text,
        user_id=user.id,
        result_id=f"message:{message.chat.id}:{message.message_id}",
    )

    meta = f"user_id={user.id} message_id={message.message_id}"
    enqueue_job(queue=queue, job=job, meta=meta)

    await message.reply("💾")
