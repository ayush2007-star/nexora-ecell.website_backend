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