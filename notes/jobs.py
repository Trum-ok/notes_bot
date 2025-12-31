from pydantic import BaseModel


class Job(BaseModel):
    pass


class CreateNoteJob(Job):
    database_id: str
    text: str
    user_id: int
    result_id: str
