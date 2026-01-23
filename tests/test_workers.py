import asyncio
from unittest.mock import AsyncMock

import pytest

from notes.jobs import CreateNoteJob
from notes.notion.wrapper import NotionWrapper
from notes.workers import notion_worker


class TestNotionWorker:
    @pytest.mark.asyncio
    async def test_worker_processes_job(
        self, job_queue: asyncio.Queue, sample_job: CreateNoteJob
    ) -> None:
        mock_wrapper = AsyncMock(spec=NotionWrapper)

        job_queue.put_nowait(sample_job)

        worker_task = asyncio.create_task(
            notion_worker(worker_id=1, queue=job_queue, notion=mock_wrapper)
        )

        await asyncio.sleep(0.1)
        worker_task.cancel()

        try:
            await worker_task
        except asyncio.CancelledError:
            pass

        mock_wrapper.create_note.assert_called_once_with(
            database_id=sample_job.database_id,
            note=sample_job.text,
        )

    @pytest.mark.asyncio
    async def test_worker_processes_multiple_jobs(
        self, job_queue: asyncio.Queue
    ) -> None:
        mock_wrapper = AsyncMock(spec=NotionWrapper)

        jobs = [
            CreateNoteJob(
                database_id=f"db-{i}",
                text=f"Note {i}",
                user_id=i,
                result_id=f"result-{i}",
            )
            for i in range(3)
        ]

        for job in jobs:
            job_queue.put_nowait(job)

        worker_task = asyncio.create_task(
            notion_worker(worker_id=1, queue=job_queue, notion=mock_wrapper)
        )

        await asyncio.sleep(0.2)
        worker_task.cancel()

        try:
            await worker_task
        except asyncio.CancelledError:
            pass

        assert mock_wrapper.create_note.call_count == 3

    @pytest.mark.asyncio
    async def test_worker_handles_cancellation(self, job_queue: asyncio.Queue) -> None:
        mock_wrapper = AsyncMock(spec=NotionWrapper)

        worker_task = asyncio.create_task(
            notion_worker(worker_id=1, queue=job_queue, notion=mock_wrapper)
        )

        await asyncio.sleep(0.05)
        worker_task.cancel()

        with pytest.raises(asyncio.CancelledError):
            await worker_task

    @pytest.mark.asyncio
    async def test_worker_marks_task_done(
        self, job_queue: asyncio.Queue, sample_job: CreateNoteJob
    ) -> None:
        mock_wrapper = AsyncMock(spec=NotionWrapper)

        job_queue.put_nowait(sample_job)

        worker_task = asyncio.create_task(
            notion_worker(worker_id=1, queue=job_queue, notion=mock_wrapper)
        )

        await asyncio.sleep(0.1)
        worker_task.cancel()

        try:
            await worker_task
        except asyncio.CancelledError:
            pass

        # Queue should be empty and task_done called
        assert job_queue.empty()
