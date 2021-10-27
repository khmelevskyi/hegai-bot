""" jinja tamplates env """
from jinja2 import Environment
from jinja2 import FileSystemLoader


jinja_env = Environment(loader=FileSystemLoader("templates"))
jinja_env.trim_blocks = True
jinja_env.lstrip_blocks = True
