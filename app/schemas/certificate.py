from pydantic import BaseModel

class CertificateCreate(BaseModel):
    team_name: str
    certificate_id: str
