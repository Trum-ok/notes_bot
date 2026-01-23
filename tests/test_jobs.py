import pytest
from pydantic import ValidationError

from notes.jobs import CreateNoteJob, Job


class TestJob:
    def test_job_is_base_model(self) -> None:
        job = Job()
        assert job is not None

    def test_job_can_be_subclassed(self) -> None:
        assert issubclass(CreateNoteJob, Job)


class TestCreateNoteJob:
    def test_create_note_job_valid(self) -> None:
        job = CreateNoteJob(
            database_id="db-123",
            text="My note",
            user_id=456,
            result_id="result-789",
        )
        assert job.database_id == "db-123"
        assert job.text == "My note"
        assert job.user_id == 456
        assert job.result_id == "result-789"

    def test_create_note_job_missing_required_field(self) -> None:
        with pytest.raises(ValidationError):
            CreateNoteJob(
                database_id="db-123",
                text="My note",
                user_id=456,
                # missing result_id
            )

    def test_create_note_job_serialization(self) -> None:
        job = CreateNoteJob(
            database_id="db-123",
            text="Test",
            user_id=1,
            result_id="r-1",
        )
        data = job.model_dump()
        assert data == {
            "database_id": "db-123",
            "text": "Test",
            "user_id": 1,
            "result_id": "r-1",
        }

    def test_create_note_job_from_dict(self) -> None:
        data = {
            "database_id": "db-abc",
            "text": "Note from dict",
            "user_id": 999,
            "result_id": "res-abc",
        }
        job = CreateNoteJob.model_validate(data)
        assert job.database_id == "db-abc"
        assert job.text == "Note from dict"
