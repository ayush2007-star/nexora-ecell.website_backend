from pydantic import BaseModel

class ProjectCreate(BaseModel):
    title: str
    summary: str
