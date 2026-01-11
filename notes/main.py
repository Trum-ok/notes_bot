import asyncio
from contextlib import suppress
from typing import TypeAlias

from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from notes.jobs import CreateNoteJob
from notes.notion.wrapper import NotionWrapper, setup_notion_connection
from notes.settings import (
    DEV,
    NOTION_SECRET,
    QUEUE_MAXSIZE,
    WEBHOOK_PATH,
    WEBHOOK_PORT,
    WEBHOOK_PUBLIC_URL,
    WEBHOOK_SECRET,
    WORKERS_COUNT,
    global_logger,
)
from notes.telegram.bot import bot, dp
from notes.workers import notion_worker

CreateNoteQueue: TypeAlias = asyncio.Queue[CreateNoteJob]


async def start_workers(
    notion: NotionWrapper,
) -> tuple[CreateNoteQueue, list[asyncio.Task]]:
    queue: CreateNoteQueue = asyncio.Queue(maxsize=QUEUE_MAXSIZE)

    workers = [
        asyncio.create_task(notion_worker(worker_id=i, queue=queue, notion=notion))
        for i in range(WORKERS_COUNT)
    ]

    dp["notion"] = notion
    dp["queue"] = queue
    dp["workers"] = workers
    return queue, workers


async def stop_workers(
    notion: NotionWrapper, queue: CreateNoteQueue, workers: list[asyncio.Task]
) -> None:
    global_logger.info("Stopping bot...")
    with suppress(asyncio.TimeoutError):
        await asyncio.wait_for(queue.join(), timeout=30)

    global_logger.info("Canceling tasks...")
    for task in workers:
        task.cancel()
    await asyncio.gather(*workers, return_exceptions=True)

    await notion.client.close()
    global_logger.info("Exiting app...")


async def run_polling(notion) -> None:
    queue, workers = await start_workers(notion)

    global_logger.info("Starting bot in polling mode...")
    await bot.delete_webhook(drop_pending_updates=True)

    try:
        await dp.start_polling(bot, handle_signals=True)
    finally:
        await stop_workers(notion, queue, workers)


async def run_webhook(notion) -> None:
    queue, workers = await start_workers(notion)

    if not WEBHOOK_PUBLIC_URL:
        raise Exception("WEBHOOK_PUBLIC_URL must be set")

    public_url = WEBHOOK_PUBLIC_URL.rstrip("/")

    async def on_startup(app: web.Application) -> None:
        global_logger.info("Starting bot in webhook mode...")
        await bot.set_webhook(
            url=f"{public_url}/{WEBHOOK_PATH}",
            secret_token=WEBHOOK_SECRET,
            drop_pending_updates=True,
        )

    async def on_shutdown(app: web.Application) -> None:
        global_logger.info("Deleting webhook...")
        await bot.delete_webhook(drop_pending_updates=False)

    app = web.Application()
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=WEBHOOK_SECRET,
    ).register(app, path=WEBHOOK_PATH)

    setup_application(app, dp, bot=bot)

    try:
        web.run_app(app, host="0.0.0.0", port=WEBHOOK_PORT)
    finally:
        await stop_workers(notion, queue, workers)


async def main() -> None:
    global_logger.info("Setting up notion connection...")
    notion = await setup_notion_connection(token=NOTION_SECRET)  # type: ignore[invalid-argument-type]
    global_logger.info("Notion connection setup complete")

    if DEV is False:
        await run_polling(notion)
    else:
        await run_webhook(notion)


if __name__ == "__main__":
    asyncio.run(main())
