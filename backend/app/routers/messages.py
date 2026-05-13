from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_master_session, get_replica_session
from app.models import Channel, Message, Tag, User
from app.schemas import MessageCreate, MessageResponse
from app.clickhouse_client import ch_client

router = APIRouter()


@router.post("/", response_model=MessageResponse)
async def create_message(msg: MessageCreate, session: AsyncSession = Depends(get_master_session)):
    channel = await session.get(Channel, msg.channel_id)
    if not channel or channel.admin_id != msg.sender_id:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Only channel admin can post messages")

    db_msg = Message(
        channel_id=msg.channel_id,
        sender_id=msg.sender_id,
        content=msg.content,
        primary_tag_id=msg.primary_tag_id,
    )
    session.add(db_msg)
    await session.commit()
    await session.refresh(db_msg)

    await ch_client.insert_messages([{
        "message_id": db_msg.id,
        "channel_id": db_msg.channel_id,
        "tag_id": db_msg.primary_tag_id or 0,
        "user_id": db_msg.sender_id,
        "created_at": db_msg.created_at,
    }])

    return db_msg


@router.get("/channel/{channel_id}", response_model=list[MessageResponse])
async def list_messages(
    channel_id: int,
    tag_id: int | None = Query(None),
    limit: int = Query(20, le=100),
    cursor: str | None = Query(None),
    session: AsyncSession = Depends(get_replica_session),
):
    query = select(Message).where(Message.channel_id == channel_id)

    if tag_id:
        query = query.where(Message.primary_tag_id == tag_id)

    if cursor:
        cursor_dt = datetime.fromisoformat(cursor)
        query = query.where(Message.created_at < cursor_dt)

    query = query.order_by(desc(Message.created_at)).limit(limit)
    result = await session.execute(query)
    messages = result.scalars().all()

    tag_ids = [m.primary_tag_id for m in messages if m.primary_tag_id]
    tags = {}
    if tag_ids:
        tag_result = await session.execute(select(Tag).where(Tag.id.in_(tag_ids)))
        for t in tag_result.scalars():
            tags[t.id] = t.name

    sender_ids = [m.sender_id for m in messages]
    senders = {}
    if sender_ids:
        user_result = await session.execute(select(User).where(User.id.in_(sender_ids)))
        for u in user_result.scalars():
            senders[u.id] = u.username

    response = []
    for m in messages:
        response.append(MessageResponse(
            id=m.id,
            channel_id=m.channel_id,
            sender_id=m.sender_id,
            sender_name=senders.get(m.sender_id),
            content=m.content,
            primary_tag_id=m.primary_tag_id,
            primary_tag_name=tags.get(m.primary_tag_id),
            created_at=m.created_at,
        ))
    return response
