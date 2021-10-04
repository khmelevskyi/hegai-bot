""" db for regsistation workflow """
from telegram import Chat

from ..hegai_db import User
from ._utils import local_session


class Mixin:
    """ registration """

    @local_session
    def add_user(self, session, chat: Chat) -> User:
        """
        Create user record if not exist, otherwise update username
        """
        chat_id = chat.id
        username = chat.username
        first_name = chat.first_name

        user = session.query(User).get(chat_id)
        if user:
            if user.username != username:
                user.username = username
                session.commit()
            if user.is_banned is True:
                user.is_banned = False
                session.commit()
            return user

        new_user = User(
            chat_id=chat_id,
            # notion_id=None,
            # conversation_open=None,
            is_banned=False,
            # region=None,
            username=username,
            full_name=first_name,
        )
        session.add(new_user)
        session.commit()
        return new_user

    @local_session
    def user_is_registered(self, session, chat_id: int) -> bool:
        """
        Create user record if not exist, otherwise update username
        """
        user = session.query(User).get(chat_id)
        if user:
            return True
        return False

    @local_session
    def add_user_data(self, session, chat: Chat, university_id: int, data: dict):
        """ save user settings for api request """

        chat_id = chat.id
        user = session.query(User).get(chat_id)
        if not user:
            user = self.add_user(chat)
        user.university_id = university_id
        user.user_data = data
        session.commit()
