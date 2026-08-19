from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from pydantic import BaseModel

from app.core.responses import ApiResponse
from app.dependencies.auth import admin_required
from app.services.event_service import EventService


router = APIRouter(
    prefix="/api/v1/events",
    tags=["Events"],
)


class EventCreateUpdateSchema(BaseModel):
    eventId: Optional[str] = None
    title: str
    category: Optional[str] = "Hackathon"
    badge: Optional[str] = "FLAGSHIP EVENT"
    date: str
    venue: Optional[str] = "Main Innovation Auditorium & Online"
    description: str
    prizePool: Optional[str] = "₹1,00,000+"
    maxTeamSize: Optional[int] = 3
    registrationDeadline: Optional[str] = ""
    status: Optional[str] = "Live"
    bannerUrl: Optional[str] = None


@router.get("/public")
async def get_public_events():
    """
    Fetch all active public events for home page and registration dropdown.
    """
    events = await EventService.get_public_events()
    return ApiResponse.success(
        message="Events retrieved successfully.",
        data=events,
    )


@router.get("/")
async def get_all_events(admin=Depends(admin_required)):
    """
    Admin: Fetch all events including completed and drafts.
    """
    events = await EventService.get_all_events()
    return ApiResponse.success(
        message="All events retrieved successfully.",
        data=events,
    )


@router.get("/{event_id}")
async def get_event_details(event_id: str):
    """
    Fetch details of a single event.
    """
    try:
        event = await EventService.get_event_details(event_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    return ApiResponse.success(
        message="Event details retrieved.",
        data=event,
    )


@router.get("/{event_id}/registrations")
async def get_event_registrations(event_id: str, admin=Depends(admin_required)):
    """
    Admin: Get all team registrations belonging to a specific event.
    """
    registrations = await EventService.get_event_registrations(event_id)
    return ApiResponse.success(
        message=f"Registrations for event {event_id} retrieved.",
        data=registrations,
    )


@router.post("/")
async def create_event(payload: EventCreateUpdateSchema, admin=Depends(admin_required)):
    """
    Admin: Create a new event.
    """
    try:
        new_event = await EventService.create_new_event(payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return ApiResponse.success(
        message="Event created successfully.",
        data=new_event,
    )


@router.put("/{event_id}")
async def update_event(event_id: str, payload: EventCreateUpdateSchema, admin=Depends(admin_required)):
    """
    Admin: Update an existing event.
    """
    try:
        updated = await EventService.update_event(event_id, payload.model_dump(exclude_unset=True))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    return ApiResponse.success(
        message="Event updated successfully.",
        data=updated,
    )


@router.delete("/{event_id}")
async def delete_event(event_id: str, admin=Depends(admin_required)):
    """
    Admin: Delete an event.
    """
    try:
        await EventService.delete_event(event_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    return ApiResponse.success(
        message="Event deleted successfully.",
        data=None,
    )
