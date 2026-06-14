from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_admin
from app.models.user import User
from app.schemas.users import UserRead
from app.services.users import list_users

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserRead], dependencies=[Depends(require_admin)])
def users(db: Session = Depends(get_db)) -> list[User]:
    return list_users(db)
