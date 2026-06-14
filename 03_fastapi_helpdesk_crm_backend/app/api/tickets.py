from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.ticket import TicketStatus
from app.models.user import User
from app.schemas.tickets import CommentCreate, CommentRead, TicketCreate, TicketRead, TicketUpdate
from app.services.tickets import (
    add_comment,
    can_access_ticket,
    create_ticket,
    get_ticket,
    list_tickets,
    update_ticket,
)

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.post("", response_model=TicketRead, status_code=status.HTTP_201_CREATED)
def create(
    payload: TicketCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TicketRead:
    return create_ticket(db, payload, current_user)


@router.get("", response_model=list[TicketRead])
def list_(
    status_filter: TicketStatus | None = Query(default=None, alias="status"),
    author_id: int | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[TicketRead]:
    return list_tickets(
        db=db,
        current_user=current_user,
        status=status_filter,
        author_id=author_id,
        limit=limit,
        offset=offset,
    )


@router.get("/{ticket_id}", response_model=TicketRead)
def read(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TicketRead:
    ticket = get_ticket(db, ticket_id)
    if ticket is None or not can_access_ticket(current_user, ticket):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    return ticket


@router.patch("/{ticket_id}", response_model=TicketRead)
def update(
    ticket_id: int,
    payload: TicketUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TicketRead:
    ticket = get_ticket(db, ticket_id)
    if ticket is None or not can_access_ticket(current_user, ticket):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    return update_ticket(db, ticket, payload, current_user)


@router.post("/{ticket_id}/comments", response_model=CommentRead, status_code=status.HTTP_201_CREATED)
def comment(
    ticket_id: int,
    payload: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CommentRead:
    ticket = get_ticket(db, ticket_id)
    if ticket is None or not can_access_ticket(current_user, ticket):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    return add_comment(db, ticket, current_user, payload.body)
