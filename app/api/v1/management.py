from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from app.core.responses import ApiResponse
from app.core.security import hash_password
from app.dependencies.auth import admin_required, management_required
from app.database.collections import get_collections
from app.repositories.user_repository import UserRepository
from app.utils.id_generator import (
    generate_user_id,
    generate_management_update_id,
)

router = APIRouter(
    prefix="/api/v1/management",
    tags=["Management"],
)


class CreateManagementSchema(BaseModel):
    fullName: str
    email: str
    password: str
    phone: Optional[str] = ""
    department: Optional[str] = "Event Management"
    designation: Optional[str] = "Management Staff"
    isActive: bool = True


class UpdateManagementSchema(BaseModel):
    fullName: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    isActive: Optional[bool] = None


class WorkUpdateSchema(BaseModel):
    title: str = Field(..., min_length=2, max_length=150)
    description: str = Field(..., min_length=2, max_length=3000)
    status: str = "In Progress"
    priority: str = "Normal"


async def _log_activity(user, action, description):
    try:
        collections = get_collections()
        logs = collections.get("activity_logs")

        if logs is not None:
            await logs.insert_one({
                "userId": user.get("userId"),
                "role": user.get("role"),
                "action": action,
                "module": "Management",
                "description": description,
                "createdAt": datetime.now(timezone.utc),
            })
    except Exception:
        pass


# =========================================================
# ADMIN - MANAGEMENT ACCOUNT CRUD
# =========================================================

@router.get("/admin/accounts")
async def get_management_accounts(
    user=Depends(admin_required),
):
    collections = get_collections()
    users = collections.get("users")

    if users is None:
        return ApiResponse.error(
            "Users collection unavailable.",
            status_code=500,
        )

    cursor = users.find(
        {"role": "management"},
        {"_id": 0, "password": 0},
    ).sort("createdAt", -1)

    accounts = await cursor.to_list(length=None)

    return ApiResponse.success(
        message="Management accounts retrieved successfully.",
        data=accounts,
    )


@router.post(
    "/admin/accounts",
    status_code=status.HTTP_201_CREATED,
)
async def create_management_account(
    payload: CreateManagementSchema,
    user=Depends(admin_required),
):
    email = payload.email.strip().lower()

    if "@" not in email:
        return ApiResponse.error(
            "Please provide a valid email address."
        )

    if len(payload.password) < 6:
        return ApiResponse.error(
            "Password must be at least 6 characters."
        )

    existing = await UserRepository.find_by_email(email)

    if existing:
        return ApiResponse.error(
            f"Email '{email}' is already registered."
        )

    now = datetime.now(timezone.utc)

    user_id = await generate_user_id()

    document = {
        "userId": user_id,
        "fullName": payload.fullName.strip(),
        "email": email,
        "password": hash_password(payload.password),
        "phone": payload.phone or "",
        "department": payload.department or "Event Management",
        "designation": payload.designation or "Management Staff",
        "role": "management",
        "status": "Approved",
        "isApproved": True,
        "isActive": payload.isActive,
        "approvedBy": user.get("userId", "ADMIN"),
        "approvedAt": now,
        "createdAt": now,
        "updatedAt": now,
    }

    await UserRepository.create(document)

    await _log_activity(
        user,
        "MANAGEMENT_ACCOUNT_CREATED",
        f"Created management account {email}.",
    )

    document.pop("password", None)

    return ApiResponse.success(
        message="Management account created successfully.",
        data=document,
        status_code=status.HTTP_201_CREATED,
    )


@router.put("/admin/accounts/{user_id}")
async def update_management_account(
    user_id: str,
    payload: UpdateManagementSchema,
    user=Depends(admin_required),
):
    account = await UserRepository.find_by_user_id(user_id)

    if not account or account.get("role") != "management":
        return ApiResponse.error(
            "Management account not found.",
            status_code=404,
        )

    data = payload.model_dump(exclude_none=True)

    if "email" in data:
        email = data["email"].strip().lower()

        existing = await UserRepository.find_by_email(email)

        if existing and existing.get("userId") != user_id:
            return ApiResponse.error(
                "Email is already in use."
            )

        data["email"] = email

    if "password" in data:
        if len(data["password"]) < 6:
            return ApiResponse.error(
                "Password must be at least 6 characters."
            )

        data["password"] = hash_password(data["password"])

    data["updatedAt"] = datetime.now(timezone.utc)

    await UserRepository.update(user_id, data)

    updated = await UserRepository.find_by_user_id(user_id)

    if updated:
        updated.pop("password", None)

    await _log_activity(
        user,
        "MANAGEMENT_ACCOUNT_UPDATED",
        f"Updated management account {user_id}.",
    )

    return ApiResponse.success(
        message="Management account updated successfully.",
        data=updated,
    )


@router.delete("/admin/accounts/{user_id}")
async def delete_management_account(
    user_id: str,
    user=Depends(admin_required),
):
    account = await UserRepository.find_by_user_id(user_id)

    if not account or account.get("role") != "management":
        return ApiResponse.error(
            "Management account not found.",
            status_code=404,
        )

    await UserRepository.delete(user_id)

    await _log_activity(
        user,
        "MANAGEMENT_ACCOUNT_DELETED",
        f"Deleted management account {user_id}.",
    )

    return ApiResponse.success(
        message="Management account deleted successfully.",
        data=None,
    )


# =========================================================
# ADMIN - VIEW MANAGEMENT WORK UPDATES
# =========================================================

@router.get("/admin/updates")
async def get_all_updates(
    user=Depends(admin_required),
):
    collections = get_collections()
    updates = collections.get("management_updates")

    if updates is None:
        return ApiResponse.success(
            message="No management updates available.",
            data=[],
        )

    cursor = updates.find(
        {},
        {"_id": 0},
    ).sort("createdAt", -1)

    data = await cursor.to_list(length=None)

    return ApiResponse.success(
        message="Management work updates retrieved successfully.",
        data=data,
    )


# =========================================================
# MANAGEMENT - OWN PORTAL
# =========================================================

@router.get("/me")
async def management_profile(
    user=Depends(management_required),
):
    account = await UserRepository.find_by_user_id(
        user.get("userId")
    )

    if not account:
        return ApiResponse.error(
            "Management account not found.",
            status_code=404,
        )

    account.pop("password", None)

    return ApiResponse.success(
        message="Management profile retrieved successfully.",
        data=account,
    )


@router.get("/updates")
async def get_my_updates(
    user=Depends(management_required),
):
    collections = get_collections()
    updates = collections.get("management_updates")

    if updates is None:
        return ApiResponse.success(
            message="No updates found.",
            data=[],
        )

    cursor = updates.find(
        {
            "userId": user.get("userId"),
        },
        {"_id": 0},
    ).sort("createdAt", -1)

    data = await cursor.to_list(length=None)

    return ApiResponse.success(
        message="Your work updates retrieved successfully.",
        data=data,
    )


@router.post("/updates")
async def create_work_update(
    payload: WorkUpdateSchema,
    user=Depends(management_required),
):
    allowed_status = [
        "Pending",
        "In Progress",
        "Completed",
        "Blocked",
    ]

    allowed_priority = [
        "Low",
        "Normal",
        "High",
        "Urgent",
    ]

    if payload.status not in allowed_status:
        return ApiResponse.error(
            "Invalid update status."
        )

    if payload.priority not in allowed_priority:
        return ApiResponse.error(
            "Invalid priority."
        )

    collections = get_collections()
    updates = collections.get("management_updates")

    if updates is None:
        return ApiResponse.error(
            "Management updates collection unavailable.",
            status_code=500,
        )

    now = datetime.now(timezone.utc)

    document = {
        "updateId": await generate_management_update_id(),
        "userId": user.get("userId"),
        "userName": user.get("fullName"),
        "userEmail": user.get("email"),
        "title": payload.title.strip(),
        "description": payload.description.strip(),
        "status": payload.status,
        "priority": payload.priority,
        "createdAt": now,
        "updatedAt": now,
    }

    await updates.insert_one(document)

    await _log_activity(
        user,
        "MANAGEMENT_WORK_UPDATE",
        f"{payload.title} - {payload.status}",
    )

    return ApiResponse.success(
        message="Work update submitted successfully.",
        data=document,
        status_code=status.HTTP_201_CREATED,
    )