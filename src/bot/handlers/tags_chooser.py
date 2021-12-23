""" class to contain push data """
from typing import Dict
from typing import List

from ..db_functions import db_session
from .notion_parse import parse_tags_groups


class TagsChooser:
    """ container for data to be pushed """

    def __init__(self):
        self.user_tags_dict: Dict[str, List[str]] = {}
        self._page: int = 0
        self._page_tags = []
        self._statuses = []
        self._curr_status: str = None
        self._status_tags = []
        self._groups = parse_tags_groups()

    @property
    def statuses(self):
        """ user tags statuses """
        return self._statuses

    @statuses.setter
    def statuses(self, statuses):
        self._statuses = statuses
        self._curr_status = statuses[0]

    @property
    def curr_status(self):
        """ current status in statuses """
        return self._curr_status

    @curr_status.setter
    def curr_status(self, data: str):
        idx = self._statuses.index(self._curr_status)
        if data == "category_n":
            self._curr_status = self._statuses[idx + 1]
            print(self._curr_status)
        if data == "category_p":
            self._curr_status = self._statuses[idx - 1]
            print(self._curr_status)

    @property
    def status_tags(self):
        """ tags of one status """
        return self._status_tags

    @status_tags.setter
    def status_tags(self, curr_status: str):
        tags_by_status = db_session.get_tags_by_status(curr_status)

        grouped_tags_by_status = []
        for tag in tags_by_status:
            for group in self._groups.keys():
                if tag.name in self._groups[group]:
                    grouped_tags_by_status.append(group)
        self._status_tags = list(dict.fromkeys(grouped_tags_by_status))

    @property
    def page(self) -> int:
        """button"""
        return self._page

    @page.setter
    def page(self, data: str):
        """ create button """
        if data == "back":
            self._page = self._page - 8
        elif data == "next":
            self._page = self._page + 8
        else:
            self._page = 0

    @property
    def page_tags(self):
        """ tags of one page """
        status_tags = self._status_tags
        page = self._page
        self._page_tags = status_tags[page : page + 8]
        return self._page_tags

    def flush(self):
        """ clean function """
        self.user_tags_dict: Dict[str, List[str]] = {}
        self.page: int = 0
        self._page_tags = []
        self._statuses = []
        self._curr_status: str = None
        self._status_tags = []
