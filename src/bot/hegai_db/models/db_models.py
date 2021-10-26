""" database models """
from datetime import datetime
from enum import Enum
from typing import Any

import pytz
from sqlalchemy import BigInteger
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import MetaData
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

meta = MetaData(  # automatically name constraints to simplify migrations
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
)
# Any saves from mypy checks of a dynamic class
Base: Any = declarative_base(metadata=meta)


def local_time() -> datetime:
    """ time in Ukraine """
    kiev_tz = pytz.timezone("Europe/Kiev")
    current_time = datetime.now(tz=kiev_tz)
    return current_time


class Region(Base):
    """ region model """

    __tablename__ = "region"

    id = Column(Integer, primary_key=True)
    name = Column(String)

    def __repr__(self):
        return "<Region(id='{}', name='{}')>".format(self.id, self.name)


class Contacts(Base):
    """ contacts model """

    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True)
    user_one = Column(Integer, ForeignKey("user.id"))
    user_two = Column(Integer, ForeignKey("user.id"))

    user_one_name = relationship(
        "User", backref="contacts_one", foreign_keys=[user_one]
    )
    user_two_name = relationship(
        "User", backref="contacts_two", foreign_keys=[user_two]
    )

    def __repr__(self):
        return "<Contacts(id='{}', user_one='{}', user_two='{}')>".format(
            self.id, self.user_one, self.user_two
        )


class UserTag(Base):
    """ user tag model """

    __tablename__ = "user_tag"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    tag_id = Column(Integer, ForeignKey("tag.id"))

    user = relationship("User", backref="user_tag_user", foreign_keys=[user_id])
    tag = relationship("Tag", backref="user_tag", foreign_keys=[tag_id])

    def __repr__(self):
        return "<UserTag(id='{}', user_id='{}', tag_id='{}')>".format(
            self.id, self.user_id, self.tag_id
        )


class Tag(Base):
    """ tag model """

    __tablename__ = "tag"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    notion_id = Column(String)
    status = Column(String)

    def __repr__(self):
        return "<Tag(id='{}', name='{}', notion_id='{}', status='{}')>".format(
            self.id, self.name, self.notion_id, self.status
        )


class ConversationRequest(Base):
    """ conversation request model """

    __tablename__ = "conversation_request"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    user_found = Column(Integer, ForeignKey("user.id"))
    tags = Column(JSONB)
    active = Column(Boolean)
    time_posted = Column(DateTime)
    time_processed = Column(DateTime)

    user_name = relationship(
        "User", backref="conversation_request_user", foreign_keys=[user_id]
    )
    user_found_name = relationship(
        "User", backref="conversation_request_user_found", foreign_keys=[user_found]
    )

    def __repr__(self):
        return "<ConversationRequest(id='{}', user_id='{}', user_found='{}', tags='{}', active='{}')>".format(
            self.id, self.user_id, self.user_found, self.tags, self.active
        )


class Feedback(Base):
    """ feedback model """

    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True)
    request_id = Column(Integer, ForeignKey("conversation_request.id"))
    conversation_occured = Column(Boolean)
    rate = Column(Integer)
    comment = Column(String)

    request = relationship(
        "ConversationRequest", backref="feedback", foreign_keys=[request_id]
    )

    def __repr__(self):
        return "<Feedback(id='{}', request_id='{}', conversation_occured='{}', rate='{}')>".format(
            self.id, self.request_id, self.conversation_occured, self.rate
        )


class User(Base):
    """ user model """

    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    chat_id = Column(BigInteger)
    notion_id = Column(String)
    conversation_open = Column(Boolean)
    is_banned = Column(Boolean)
    region = Column(Integer, ForeignKey("region.id"))
    username = Column(String(35))  # Telegram allows username no longer then 32
    full_name = Column(String)  # first name is unlimited
    time_registered = Column(DateTime(timezone=True), default=local_time)

    region_name = relationship("Region", backref="user", foreign_keys=[region])

    def __repr__(self):
        return "<User(chat_id='{}', username='{}', is_banned='{}', conversation_open='{}')>".format(
            self.chat_id, self.username, self.is_banned, self.conversation_open
        )


class Admin(Base):
    """ admin model """

    __tablename__ = "admin"

    id = Column(Integer, ForeignKey("user.id"), primary_key=True)

    user = relationship("User", backref="admin", foreign_keys=[id])

    def __repr__(self):
        return "<Admin(chat_id='{}')>".format(self.id)


class Permission(Enum):
    """ helper class to define json keys for role permissions """

    STAT: str = "statistics"
    AD: str = "advertising"
    PARSE: str = "parsing"
    PUSH: str = "push"
    DROP: str = "drop_user"
    SET: str = "set_user"


class UserAction(Base):
    """ user_action model """

    __tablename__ = "user_action"

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("user.id"))
    action = Column(Integer, ForeignKey("action.id"))
    time_clicked = Column(DateTime(timezone=True), default=local_time)

    user = relationship("User", backref="user_action", foreign_keys=[user_id])
    action_name = relationship(
        "Action", backref="user_action_name", foreign_keys=[action]
    )

    def __repr__(self):
        return "<Action(id='{}', chat_id='{}', action='{}', time='{}')>".format(
            self.id, self.user_id, self.action, self.time_clicked
        )


class Action(Base):
    """ action model """

    __tablename__ = "action"

    id = Column(Integer, primary_key=True)
    name = Column(String)

    # static defenition for insertion safety
    now = "now"
    today = "today"
    tomorrow = "tomorrow"
    week = "week"
    next_week = "next_week"
    ban = "ban"
    profile = "profile"
    share = "share"

    def __repr__(self):
        return "<ActionType(id='{}', name='{}')>".format(self.id, self.name)
