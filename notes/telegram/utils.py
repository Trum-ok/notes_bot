import asyncio

from notes.jobs import Job
from notes.settings import logger_tg


def enqueue_job(queue: asyncio.Queue, job: Job, *, meta: str = "") -> bool:
    try:
        queue.put_nowait(job)
        logger_tg.info("ENQUEUED %s | job=%s", meta, job)
        return True
    except asyncio.QueueFull:
        logger_tg.warning("QUEUE FULL %s | job=%s", meta, job)
        return False
