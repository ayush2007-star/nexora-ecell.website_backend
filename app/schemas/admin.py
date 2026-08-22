from pydantic import BaseModel


class ApproveRegistrationSchema(BaseModel):
    remarks: str | None = None


class RejectRegistrationSchema(BaseModel):
    remarks: str


class DashboardStatsResponse(BaseModel):
    totalRegistrations: int
    pendingRegistrations: int
    approvedRegistrations: int
    rejectedRegistrations: int
    totalProjects: int
    totalColleges: int
    totalStudents: int


class CreateMentorSchema(BaseModel):
    fullName: str
    email: str
    password: str
    mentorIndex: int = 1
    specialization: str | None = "Startup Mentor / Jury"
    phone: str | None = "9876543210"


class UpdateMentorSchema(BaseModel):
    fullName: str | None = None
    email: str | None = None
    password: str | None = None
    mentorIndex: int | None = None
    specialization: str | None = None
    phone: str | None = None
    isActive: bool | None = None