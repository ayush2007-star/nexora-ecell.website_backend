from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, field_validator

# ==========================================
# Leader Information
# ==========================================

class LeaderInfo(BaseModel):

    fullName: str = Field(..., min_length=3, max_length=100)

    email: EmailStr

    phone: str = Field(..., pattern=r"^[6-9]\d{9}$")

    college: str

    department: str

    year: str

    rollNumber: str

# ==========================================
# Project
# ==========================================

class ProjectInfo(BaseModel):

    projectName: str = Field(..., min_length=3)

    domain: str

    description: str = Field(..., min_length=20)

    stage: str

# ==========================================
# Team Member
# ==========================================

class TeamMember(BaseModel):

    memberName: str

    memberEmail: EmailStr

    memberPhone: str = Field(
        ...,
        pattern=r"^[6-9]\d{9}$"
    )

# ==========================================
# Verification
# ==========================================

class Verification(BaseModel):

    eurekaTeamId: str

    referralCodeUsed: Optional[str] = None

    pitchDeckUrl: Optional[str] = None

# ==========================================
# Registration
# ==========================================

class RegistrationSchema(BaseModel):

    leaderInfo: LeaderInfo

    projectInfo: ProjectInfo

    eCellVerification: Verification

    teamMembers: List[TeamMember] = []

    @field_validator("teamMembers")
    @classmethod
    def validate_team_members(cls, members):

        if len(members) > 2:
            raise ValueError(
                "Maximum 2 additional members allowed."
            )

        return members
