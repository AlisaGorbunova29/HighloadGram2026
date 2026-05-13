from datetime import datetime
from pydantic import BaseModel


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ChannelBase(BaseModel):
    name: str


class ChannelCreate(ChannelBase):
    admin_id: int


class ChannelResponse(ChannelBase):
    id: int
    admin_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class TagBase(BaseModel):
    name: str


class TagCreate(TagBase):
    channel_id: int | None = None


class TagResponse(TagBase):
    id: int
    channel_id: int

    model_config = {"from_attributes": True}


class MessageBase(BaseModel):
    content: str
    primary_tag_id: int | None = None


class MessageCreate(MessageBase):
    channel_id: int
    sender_id: int


class MessageResponse(MessageBase):
    id: int
    channel_id: int
    sender_id: int
    sender_name: str | None = None
    created_at: datetime
    primary_tag_name: str | None = None

    model_config = {"from_attributes": True}
