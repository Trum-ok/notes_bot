import asyncio

from notes.jobs import CreateNoteJob
from notes.notion.wrapper import setup_notion_connection
from notes.settings import NOTION_SECRET, QUEUE_MAXSIZE, WORKERS_COUNT, global_logger
from notes.telegram.bot import bot, dp
from notes.workers import notion_worker


async def main() -> None:
    global_logger.info("Setting up notion connection...")
    notion = await setup_notion_connection(token=NOTION_SECRET)  # type: ignore[invalid-argument-type]
    global_logger.info("Notion connection setup complete")

    queue: asyncio.Queue[CreateNoteJob] = asyncio.Queue(maxsize=QUEUE_MAXSIZE)

    workers = [
        asyncio.create_task(notion_worker(worker_id=i, queue=queue, notion=notion))
        for i in range(WORKERS_COUNT)
    ]

    global_logger.info("Starting bot...")
    await bot.delete_webhook(drop_pending_updates=True)

    dp["notion"] = notion
    dp["queue"] = queue
    dp["workers"] = workers

    try:
        await dp.start_polling(bot, handle_signals=True)
    finally:
        global_logger.info("Stopping bot...")
        await asyncio.wait_for(queue.join(), timeout=30)

        global_logger.info("Canceling tasks...")
        for task in workers:
            task.cancel()
        await asyncio.gather(*workers, return_exceptions=True)
        global_logger.info("All tasks cancelled")

        await notion.client.close()
        global_logger.info("Exiting app...")


if __name__ == "__main__":
    asyncio.run(main())
