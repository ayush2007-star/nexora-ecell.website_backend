from pydantic import BaseModel

class Admin(BaseModel):
    username: str
    role: str = 'admin'
