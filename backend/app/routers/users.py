from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.database import get_master_session, get_replica_session
from app.models import User
from app.schemas import UserCreate, UserResponse

router = APIRouter()


@router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate, session: AsyncSession = Depends(get_master_session)):
    result = await session.execute(select(User).where(User.username == user.username))
    existing = result.scalar_one_or_none()
    if existing:
        return existing

    db_user = User(username=user.username)
    session.add(db_user)
    try:
        await session.commit()
        await session.refresh(db_user)
    except IntegrityError:
        await session.rollback()
        result = await session.execute(select(User).where(User.username == user.username))
        db_user = result.scalar_one()
    return db_user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, session: AsyncSession = Depends(get_replica_session)):
    result = await session.execute(select(User).where(User.id == user_id))
    return result.scalar_one()
