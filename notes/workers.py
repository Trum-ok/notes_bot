import asyncio

from notes.jobs import CreateNoteJob
from notes.notion.wrapper import NotionWrapper
from notes.settings import global_logger


async def notion_worker(
    worker_id: int, queue: asyncio.Queue[CreateNoteJob], notion: NotionWrapper
) -> None:
    global_logger.info("Worker %s started", worker_id)

    while True:
        job = await queue.get()
        try:
            await notion.create_note(database_id=job.database_id, note=job.text)
        except asyncio.CancelledError:
            raise
        finally:
            queue.task_done()
