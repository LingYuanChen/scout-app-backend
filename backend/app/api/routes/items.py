from typing import Any
from uuid import UUID

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app import crud
from app.api.deps import CurrentUser, EventDep, SessionDep
from app.db import Attendance, Event, Item, PackingItem
from app.schemas import (
    ItemCreate,
    ItemPublic,
    ItemsPublic,
    ItemUpdate,
    Message,
    PackingItemCreate,
    PackingItemPublic,
    PackingItemsPublic,
)

router = APIRouter(prefix="/items", tags=["items"])


@router.get("/", response_model=ItemsPublic)
def read_items(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve items catalog.
    Only teachers and superusers can access this endpoint.
    """
    if not current_user.is_superuser and current_user.role != "teacher":
        raise HTTPException(
            status_code=403, detail="Only teachers can access the items catalog"
        )

    count_statement = select(func.count()).select_from(Item)
    count = session.exec(count_statement).one()
    statement = select(Item).offset(skip).limit(limit)
    items = session.exec(statement).all()
    return ItemsPublic(data=items, count=count)


@router.get("/{id}", response_model=ItemPublic)
def read_item(session: SessionDep, current_user: CurrentUser, id: UUID) -> Any:
    """
    Get item by ID.
    """
    item = session.get(Item, id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return item


@router.post("/", response_model=ItemPublic)
def create_item(
    *, session: SessionDep, current_user: CurrentUser, item_in: ItemCreate
) -> Any:
    """
    Create new item in catalog.
    Only teachers and superusers can create items.
    """
    if not current_user.is_superuser and current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can create items")

    item = Item.model_validate(item_in, update={"owner_id": current_user.id})
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@router.put("/{id}", response_model=ItemPublic)
def update_item(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: UUID,
    item_in: ItemUpdate,
) -> Any:
    """
    Update an item.
    Only the teacher who created the item or superusers can update it.
    """
    item = session.get(Item, id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    if not current_user.is_superuser and (
        current_user.role != "teacher" or item.owner_id != current_user.id
    ):
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions",
        )

    update_dict = item_in.model_dump(exclude_unset=True)
    item.sqlmodel_update(update_dict)
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@router.delete("/{id}")
def delete_item(session: SessionDep, current_user: CurrentUser, id: UUID) -> Message:
    """
    Delete an item.
    Only the teacher who created the item or superusers can delete it.
    """
    item = session.get(Item, id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    if not current_user.is_superuser and (
        current_user.role != "teacher" or item.owner_id != current_user.id
    ):
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions",
        )

    session.delete(item)
    session.commit()
    return Message(message="Item deleted successfully")


@router.post("/{event_id}/packing", response_model=PackingItemPublic)
def add_packing_item(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    event: EventDep,
    packing_item_in: PackingItemCreate,
) -> Any:
    """
    Add an item to event's packing list.
    """
    if not current_user.is_superuser and event.created_by_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    item = session.get(Item, packing_item_in.item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    packing_item = crud.create_packing_item(
        session=session,
        event_id=event.id,
        item_id=item.id,
        packing_item_in=packing_item_in,
    )
    return packing_item


@router.get("/event/{event_id}/packing", response_model=PackingItemsPublic)
def list_packing_items(
    *,
    session: SessionDep,
    event_id: UUID,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    List all packing items for an event.
    """
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    items, count = crud.get_event_packing_items(
        session=session, event_id=event_id, skip=skip, limit=limit
    )
    return PackingItemsPublic(data=items, count=count)


# For students to view items in an event they're attending
@router.get("/event/{event_id}", response_model=PackingItemsPublic)
def get_event_items(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    event_id: UUID,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Get all items required for an event.
    Students must be attending the event to see its packing list.
    """
    # Check if user is attending the event
    attendance = session.exec(
        select(Attendance).where(
            Attendance.user_id == current_user.id, Attendance.event_id == event_id
        )
    ).first()

    if not attendance:
        raise HTTPException(
            status_code=403, detail="Must be attending the event to view packing list"
        )

    # Get packing items for the event
    statement = (
        select(PackingItem)
        .where(PackingItem.event_id == event_id)
        .offset(skip)
        .limit(limit)
    )
    items = session.exec(statement).all()
    count = len(items)

    return PackingItemsPublic(data=items, count=count)
