from sqlalchemy import Select, select
from sqlalchemy.orm import Session, selectinload

from app.models.comment import Comment
from app.models.ticket import Ticket, TicketStatus
from app.models.user import User, UserRole
from app.schemas.tickets import TicketCreate, TicketUpdate


def create_ticket(db: Session, payload: TicketCreate, author: User) -> Ticket:
    ticket = Ticket(
        title=payload.title,
        description=payload.description,
        author_id=author.id,
        status=TicketStatus.open.value,
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return get_ticket(db, ticket.id)


def get_ticket(db: Session, ticket_id: int) -> Ticket | None:
    return db.scalar(
        select(Ticket)
        .options(selectinload(Ticket.comments))
        .where(Ticket.id == ticket_id),
    )


def list_tickets(
    db: Session,
    current_user: User,
    status: TicketStatus | None = None,
    author_id: int | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[Ticket]:
    statement: Select[tuple[Ticket]] = select(Ticket).options(
        selectinload(Ticket.comments),
    )
    if current_user.role != UserRole.admin.value:
        statement = statement.where(Ticket.author_id == current_user.id)
    elif author_id is not None:
        statement = statement.where(Ticket.author_id == author_id)

    if status is not None:
        statement = statement.where(Ticket.status == status.value)

    statement = statement.order_by(Ticket.created_at.desc()).limit(limit).offset(offset)
    return list(db.scalars(statement).all())


def update_ticket(db: Session, ticket: Ticket, payload: TicketUpdate, actor: User) -> Ticket:
    if payload.title is not None:
        ticket.title = payload.title
    if payload.description is not None:
        ticket.description = payload.description
    if payload.status is not None and actor.role == UserRole.admin.value:
        ticket.status = payload.status.value

    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return get_ticket(db, ticket.id)


def add_comment(db: Session, ticket: Ticket, author: User, body: str) -> Comment:
    comment = Comment(ticket_id=ticket.id, author_id=author.id, body=body)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def can_access_ticket(user: User, ticket: Ticket) -> bool:
    return user.role == UserRole.admin.value or ticket.author_id == user.id
