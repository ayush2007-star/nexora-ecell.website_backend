from pydantic import BaseModel

class Certificate(BaseModel):
    team_name: str
    certificate_id: str
    issued: bool = False
