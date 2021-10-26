""" db function for admin account """
from datetime import datetime
from datetime import timedelta
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple

from sqlalchemy.sql.expression import false

from ..data import TIME_ZONE
from ..hegai_db import Admin
from ..hegai_db import User
from ..hegai_db import UserAction
from ._utils import local_session


class Mixin:
    """ admin """

    admins: List[Any]

    @local_session
    def get_admins(self, session) -> Dict[int, Tuple[str, dict]]:
        """ list of admin ids """

        admins = [i[0] for i in session.query(Admin.id).all()]
        return admins

    @local_session
    def set_user(self, session, admin_id: int, chat_id: int) -> Tuple[bool, str]:
        """ drop user from all tables """

        user = session.query(User).filter(User.chat_id == chat_id).first()
        if not user:
            return (True, f"User with id: {chat_id} not exist")

        admin = session.query(User).filter(User.chat_id == admin_id).first()

        try:
            admin.university_id = user.university_id
            admin.user_data = user.user_data
            session.commit()
        except Exception as error:
            session.rollback()
            return (True, f"Failed with:\n\n{error}")
        return (False, f"Set profile of user with chat_id: {chat_id}")

    @local_session
    def drop_user_cascade(self, session, chat_id: int) -> Tuple[bool, str]:
        """ drop user from all tables """

        if chat_id in self.admins.keys():
            return (True, f"User with id: {chat_id} is Admin")

        user = session.query(User).filter(User.chat_id == chat_id).first()

        if not user:
            return (True, f"User with id: {chat_id} not exist")

        raws = 0
        try:
            del_action = (
                session.query(UserAction)
                .filter(UserAction.chat_id == chat_id)
                .delete(synchronize_session=False)
            )
            del_user = (
                session.query(User)
                .filter(User.chat_id == chat_id)
                .delete(synchronize_session=False)
            )
            session.commit()
            raws += del_action + del_user
        except Exception as error:
            session.rollback()
            return (True, f"Failed with:\n\n{error}")
        return (False, f"Deleted user with id: {chat_id}\n{raws} raws affected")

    @local_session
    def get_statistics(self, session):
        """ compiles total statistics for admin toolbar """

        current_time = datetime.now(tz=TIME_ZONE)
        day_ago = current_time - timedelta(days=1)
        week_ago = current_time - timedelta(days=7)
        month_ago = current_time - timedelta(days=30)

        new_day_users = (
            session.query(User).filter(User.time_registered > day_ago).count()
        )
        new_week_users = (
            session.query(User).filter(User.time_registered > week_ago).count()
        )
        new_month_users = (
            session.query(User).filter(User.time_registered > month_ago).count()
        )

        day_actions = session.query(UserAction).filter(
            UserAction.time_clicked > day_ago
        )
        week_actions = session.query(UserAction).filter(
            UserAction.time_clicked > week_ago
        )
        month_actions = session.query(UserAction).filter(
            UserAction.time_clicked > month_ago
        )

        day_users = (
            day_actions.distinct(UserAction.chat_id)
            .group_by(UserAction.id, UserAction.chat_id)
            .count()
        )
        week_users = (
            week_actions.distinct(UserAction.chat_id)
            .group_by(UserAction.id, UserAction.chat_id)
            .count()
        )
        month_users = (
            month_actions.distinct(UserAction.chat_id)
            .group_by(UserAction.id, UserAction.chat_id)
            .count()
        )

        total_users = session.query(User)
        total_users = total_users.count()

        not_banned = session.query(User).filter(User.is_banned == false()).count()

        statistics = {
            "new_users": [new_day_users, new_week_users, new_month_users],
            "actions": [
                day_actions.count(),
                week_actions.count(),
                month_actions.count(),
            ],
            "active_users": [day_users, week_users, month_users],
            "banned": [not_banned, total_users],
        }

        return statistics
