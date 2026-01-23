import asyncio

from notes.jobs import CreateNoteJob
from notes.telegram.utils import enqueue_job


class TestEnqueueJob:
    def test_enqueue_job_success(
        self, job_queue: asyncio.Queue, sample_job: CreateNoteJob
    ) -> None:
        result = enqueue_job(job_queue, sample_job, meta="test")
        assert result is True
        assert job_queue.qsize() == 1

    def test_enqueue_job_returns_job(
        self, job_queue: asyncio.Queue, sample_job: CreateNoteJob
    ) -> None:
        enqueue_job(job_queue, sample_job)
        queued_job = job_queue.get_nowait()
        assert queued_job == sample_job

    def test_enqueue_job_queue_full(self, sample_job: CreateNoteJob) -> None:
        small_queue: asyncio.Queue[CreateNoteJob] = asyncio.Queue(maxsize=1)

        # Fill the queue
        result1 = enqueue_job(small_queue, sample_job, meta="first")
        assert result1 is True

        # Try to add another job
        another_job = CreateNoteJob(
            database_id="db-2",
            text="Another note",
            user_id=789,
            result_id="result-2",
        )
        result2 = enqueue_job(small_queue, another_job, meta="second")
        assert result2 is False
        assert small_queue.qsize() == 1

    def test_enqueue_multiple_jobs(
        self, job_queue: asyncio.Queue, sample_job: CreateNoteJob
    ) -> None:
        for i in range(3):
            job = CreateNoteJob(
                database_id=f"db-{i}",
                text=f"Note {i}",
                user_id=i,
                result_id=f"result-{i}",
            )
            result = enqueue_job(job_queue, job)
            assert result is True

        assert job_queue.qsize() == 3
