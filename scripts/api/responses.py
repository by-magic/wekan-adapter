import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field


def to_lower_camel(string: str) -> str:
    components = string.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


class InlineToken(BaseModel, alias_generator=to_lower_camel):
    id: str
    token: str
    token_expires: datetime.datetime


class InlineApiError(BaseModel, alias_generator=to_lower_camel):
    error: str
    reason: str


class InlineBoard(BaseModel, alias_generator=to_lower_camel):
    id: str = Field(alias='_id')
    title: str


class InlineList(BaseModel, alias_generator=to_lower_camel):
    id: str = Field(alias='_id')
    title: str


class InlineCustomField(BaseModel, alias_generator=to_lower_camel):
    id: str = Field(alias='_id')
    name: str
    type: str


class InlineCard(BaseModel, alias_generator=to_lower_camel):
    id: str = Field(alias='_id')
    title: Optional[str]
    description: Optional[str]
    assignees: Optional[List[str]]
    received_at: Optional[datetime.datetime]
    start_at: Optional[datetime.datetime]
    end_at: Optional[datetime.datetime]
    due_at: Optional[datetime.datetime]


class CustomFieldValue(BaseModel, alias_generator=to_lower_camel):
    id: str = Field(alias='_id')
    value: Any


class Card(InlineCard, alias_generator=to_lower_camel):
    created_at: datetime.datetime
    date_last_activity: datetime.datetime
    board_id: str
    list_id: str
    assignees: List[str]
    spent_time: Optional[int]
    custom_fields: List[CustomFieldValue]


class InlineComment(BaseModel, alias_generator=to_lower_camel):
    id: str = Field(alias='_id')
    author_id: str
    comment: str


class Comment(BaseModel, alias_generator=to_lower_camel):
    id: str = Field(alias='_id')
    board_id: str
    card_id: str
    created_at: datetime.datetime
    user_id: str


class InlineUser(BaseModel, alias_generator=to_lower_camel):
    id: str = Field(alias='_id')
    username: str


class UserEmail(BaseModel, alias_generator=to_lower_camel):
    address: str
    verified: bool


class UserProfile(BaseModel, alias_generator=to_lower_camel):
    fullname: Optional[str]


class User(BaseModel, alias_generator=to_lower_camel):
    id: Optional[str] = Field(alias='_id')
    username: Optional[str]
    created_at: Optional[datetime.datetime]
    profile: Optional[UserProfile]
    emails: Optional[List[UserEmail]]
