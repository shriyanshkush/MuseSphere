from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import require_admin
from app.database.session import get_db
from app.models.entities import Event, User
from app.repositories.domain import EventRepository
from app.schemas.dtos import EventIn, EventRead

router = APIRouter(prefix="/events", tags=["Live Events & Workshops"])


@router.post(
    "",
    response_model=EventRead,
    status_code=status.HTTP_201_CREATED,
    summary="Schedule a new live event or workshop (Admin only)",
    description="Registers a new live museum event, lecture, or guided tour with commencement timestamp, attendance capacity, and entry pricing. Requires Admin privileges.",
    response_description="Created event metadata with assigned ID.",
    responses={
        401: {"description": "Authentication required."},
        403: {"description": "Admin access needed to schedule events."}
    }
)
async def create(
    data: EventIn,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> Event:
    """Create new scheduled event."""
    new_event = Event(**data.model_dump())
    return await EventRepository(db).add(new_event)


@router.get(
    "",
    response_model=List[EventRead],
    summary="List upcoming museum events and tours",
    description="Returns all scheduled live events, workshops, curator talks, and guided tours open for visitor registration.",
    response_description="Array of event records."
)
async def list_items(db: AsyncSession = Depends(get_db)) -> List[Event]:
    """Retrieve catalog of live events."""
    return await EventRepository(db).list(limit=100, offset=0)


@router.put(
    "/{item_id}",
    response_model=EventRead,
    summary="Update event schedule or details (Admin only)",
    description="Modifies event title, description, commencement time, capacity, or ticket price. Requires Admin role.",
    response_description="Updated event object.",
    responses={
        403: {"description": "Admin access required."},
        404: {"description": "Event ID not found."}
    }
)
async def update(
    item_id: int,
    data: EventIn,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> Event:
    """Update event attributes."""
    item = await EventRepository(db).get(item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found."
        )
    for k, v in data.model_dump().items():
        setattr(item, k, v)
    await db.commit()
    await db.refresh(item)
    return item


@router.delete(
    "/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cancel and remove an event (Admin only)",
    description="Permanently deletes a scheduled event from the museum calendar. Requires Admin role.",
    responses={
        403: {"description": "Admin access required."},
        404: {"description": "Event ID not found."}
    }
)
async def delete(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> None:
    """Delete event record."""
    repo = EventRepository(db)
    item = await repo.get(item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found."
        )
    await repo.delete(item)
