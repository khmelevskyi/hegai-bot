""" class to track broadcusting process """
import time
from typing import Optional

from ...utils import jinja_env


class PushStatus:
    """ push process tracking class """

    def __init__(self):
        self._push_is_active: bool = False
        self.start_time: float = 0.0
        self.total_receivers: int = 0
        self.successful_send: int = 0
        self.error_send: int = 0

    @property
    def push_is_active(self) -> bool:
        """ private push_is_active """
        return self._push_is_active

    @push_is_active.setter
    def push_is_active(self, value: bool):
        """ change state and count time """
        if value:
            # count time after push activation
            self.start_time = time.time()
        self._push_is_active = value

    @property
    def sended_percent(self) -> float:
        """ % of successfully send msgs """

        total_sended = self.successful_send + self.error_send
        sended_per = (total_sended / self.total_receivers) * 100
        rounded_time = round(sended_per, 2)
        return rounded_time

    @property
    def errror_persent(self) -> float:
        """ % of error send msgs """

        total_sended = self.successful_send + self.error_send + 0.01
        errors_relation = (self.error_send / total_sended) * 100
        rounded_time = round(errors_relation, 2)
        return rounded_time

    @property
    def time_passed(self) -> str:
        """ time from push started """

        time_psd = time.time() - self.start_time
        return PushStatus.render_time(time_psd)

    @property
    def time_left(self) -> str:
        """ approximate time left to finish push """

        passed = time.time() - self.start_time
        sended_percent = self.sended_percent if self.sended_percent else 0.01
        send_speed = passed / sended_percent
        time_lft = send_speed * (100 - sended_percent)
        return PushStatus.render_time(time_lft)

    @staticmethod
    def render_time(seconds: float) -> str:
        """ render time """

        seconds = round(seconds, 2)
        if seconds > 60:
            return f"{round(seconds / 60, 1)} minutes"
        return f"{seconds} seconds"

    def flush(self):
        """ reset values """

        self.push_is_active = False
        self.total_receivers = 0
        self.error_send = 0
        self.successful_send = 0
        self.start_time = 0.0

    def render(self, db_changes: Optional[dict] = None) -> str:
        """ create text msg """

        if not self.push_is_active:
            return "Пуш не активен"

        push_data = {
            "sended_percent": self.sended_percent,
            "successful_send": self.successful_send,
            "error_send": self.error_send,
            "total_receivers": self.total_receivers,
            "errror_persent": self.errror_persent,
            "time_passed": self.time_passed,
            "time_left": self.time_left,
            "db_changes": db_changes,
        }
        push_status_template = jinja_env.get_template("push_status.txt")
        push_status_render = push_status_template.render(pd=push_data)
        return push_status_render
