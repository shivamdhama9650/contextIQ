from enum import StrEnum

from pydantic import BaseModel, EmailStr


class AppRole(StrEnum):
    employee = "employee"
    hr_admin = "hr_admin"
    devops_admin = "devops_admin"
    security_admin = "security_admin"
    finance_admin = "finance_admin"
    admin = "admin"


class ProfileResponse(BaseModel):
    id: str
    email: EmailStr
    full_name: str | None = None
    avatar_url: str | None = None
    role: AppRole
    department: str | None = None
    job_title: str | None = None
    is_active: bool


class ProfileRoleUpdateRequest(BaseModel):
    role: AppRole
