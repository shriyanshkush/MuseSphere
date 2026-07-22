from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import require_admin
from app.database.session import get_db
from app.models.entities import Exhibition, User
from app.repositories.domain import ExhibitionRepository
from app.schemas.dtos import ExhibitionIn, ExhibitionRead

router = APIRouter(prefix="/exhibitions", tags=["Exhibitions Catalog"])


@router.post(
    "",
    response_model=ExhibitionRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new museum exhibition (Admin only)",
    description="Adds a new curated exhibition to the museum catalog with category tag, timings, location, and popularity score. Requires Admin privileges.",
    response_description="Newly created exhibition metadata with ID.",
    responses={
        401: {"description": "Authentication required."},
        403: {"description": "Admin role required to create catalog entries."}
    }
)
async def create(
    data: ExhibitionIn,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> Exhibition:
    """Create exhibition record in database."""
    new_exhibit = Exhibition(**data.model_dump())
    return await ExhibitionRepository(db).add(new_exhibit)


@router.get(
    "",
    response_model=List[ExhibitionRead],
    summary="List active museum exhibitions",
    description="Returns a paginated list of current museum exhibitions, galleries, and special displays available for booking and exploration.",
    response_description="Array of exhibition records."
)
async def list_items(
    limit: int = Query(20, ge=1, le=100, description="Maximum results to return"),
    offset: int = Query(0, ge=0, description="Pagination starting offset"),
    db: AsyncSession = Depends(get_db),
) -> List[Exhibition]:
    """Retrieve paginated catalog of exhibitions."""
    return await ExhibitionRepository(db).list(limit, offset)


@router.get(
    "/{item_id}",
    response_model=ExhibitionRead,
    summary="Retrieve specific exhibition details",
    description="Fetches detailed description, location, timings, and popularity rating for a single exhibition ID.",
    response_description="Exhibition entity record.",
    responses={
        404: {"description": "Exhibition ID not found."}
    }
)
async def get_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
) -> Exhibition:
    """Get single exhibition by ID."""
    item = await ExhibitionRepository(db).get(item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exhibition not found."
        )
    return item


@router.put(
    "/{item_id}",
    response_model=ExhibitionRead,
    summary="Update exhibition details (Admin only)",
    description="Modifies existing exhibition title, category, timings, or location. Requires Admin role.",
    response_description="Updated exhibition record.",
    responses={
        403: {"description": "Admin access required."},
        404: {"description": "Exhibition ID not found."}
    }
)
async def update(
    item_id: int,
    data: ExhibitionIn,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> Exhibition:
    """Update exhibition attributes."""
    item = await ExhibitionRepository(db).get(item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exhibition not found."
        )
    for key, value in data.model_dump().items():
        setattr(item, key, value)
    await db.commit()
    await db.refresh(item)
    return item


@router.delete(
    "/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an exhibition (Admin only)",
    description="Permanently removes an exhibition entry from the museum catalog. Requires Admin role.",
    responses={
        403: {"description": "Admin access required."},
        404: {"description": "Exhibition ID not found."}
    }
)
async def delete(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> None:
    """Delete exhibition record."""
    repo = ExhibitionRepository(db)
    item = await repo.get(item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exhibition not found."
        )
    await repo.delete(item)
