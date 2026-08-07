from enum import Enum


class RegistrationStatus(str, Enum):
    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"


class UserRole(str, Enum):
    ADMIN = "admin"
    LEADER = "leader"
    MEMBER = "member"


class NotificationType(str, Enum):
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
