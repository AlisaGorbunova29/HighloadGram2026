from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_master_session, get_replica_session
from app.models import Channel, Subscription, Tag
from app.schemas import ChannelCreate, ChannelResponse, TagCreate, TagResponse

router = APIRouter()


@router.post("/", response_model=ChannelResponse)
async def create_channel(channel: ChannelCreate, session: AsyncSession = Depends(get_master_session)):
    db_channel = Channel(name=channel.name, admin_id=channel.admin_id)
    session.add(db_channel)
    await session.commit()
    await session.refresh(db_channel)
    return db_channel


@router.get("/", response_model=list[ChannelResponse])
async def list_channels(session: AsyncSession = Depends(get_replica_session)):
    result = await session.execute(select(Channel))
    return result.scalars().all()


@router.post("/{channel_id}/subscribe")
async def subscribe(channel_id: int, user_id: int, session: AsyncSession = Depends(get_master_session)):
    sub = Subscription(user_id=user_id, channel_id=channel_id)
    session.add(sub)
    await session.commit()
    return {"status": "subscribed"}


@router.post("/{channel_id}/tags", response_model=TagResponse)
async def create_tag(channel_id: int, tag: TagCreate, user_id: int, session: AsyncSession = Depends(get_master_session)):
    channel = await session.get(Channel, channel_id)
    if not channel or channel.admin_id != user_id:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Only channel admin can create tags")

    db_tag = Tag(name=tag.name, channel_id=channel_id)
    session.add(db_tag)
    await session.commit()
    await session.refresh(db_tag)
    return db_tag


@router.get("/{channel_id}/tags", response_model=list[TagResponse])
async def list_tags(channel_id: int, session: AsyncSession = Depends(get_replica_session)):
    result = await session.execute(select(Tag).where(Tag.channel_id == channel_id))
    return result.scalars().all()
