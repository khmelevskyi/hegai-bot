# -*- coding: utf-8 -*-
""" texts for massages """
import json
import os
import re

import pytz


directory_path = os.path.dirname(os.path.abspath(os.path.abspath(__file__)))
new_path = os.path.join(directory_path, "texts.json")

with open(new_path, "r", encoding="utf-8") as fp:
    text = json.load(fp)

start_keyboard = [
    [text["profile"], text["find_conv"]],
    [text["my_contacts"], text["connect_admin"]]
]

who_keyboard = [[text["student_q"], text["teacher_q"]], [text["back"]]]

days_keyboard = [
    # [text["now"]],
    [text["today"], text["tomorrow"]],
    [text["week"], text["next_week"]],
    [text["share_button"], text["profile"]],
]

URL_BUTTON_REGEX = re.compile(
    r"\s*~ ((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]"
    r"+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*"
)
TIMER_RANGE = [6, 10]
REG_TIMER = r"^(\d|\d\d):00 🕓$"
REG_HOURS = re.compile(r"[0-2][0-9]:[0-6][0-9]-[0-2][0-9]:[0-6][0-9]")  # 10:20-04:40
URL_REGEX = re.compile(
    r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|"
    r"[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
)  # 10:20-04:40


kiev_tz = os.getenv("TIME_ZONE", "Europe/Kiev")
TIME_ZONE = pytz.timezone(kiev_tz)
