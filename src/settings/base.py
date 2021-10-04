from loguru import logger
from pathlib import Path

from pydantic import validator, Field, BaseSettings

root_dir = Path(__file__).resolve().parent.parent
# if bot in docker change root dir path
root_dir = root_dir.parent if "src" in str(Path(__file__).resolve()) else root_dir


class BaseConfig(BaseSettings):
    mode: str = Field(default="prod")
    telegram_token: str
    telegram_base_url: str = Field(default="")

    @validator("mode")
    def name_must_contain_space(cls, value):
        if value not in ["prod", "dev", "local"]:
            raise ValueError("mode must be prod, dev or local.")
        return value

    class Config:
        env_file = root_dir.joinpath(".env")
        env_file_encoding = "utf-8"


base_conf = BaseConfig()

if base_conf.mode == "local":
    from settings.local import settings
elif base_conf.mode == "dev":
    from settings.development import settings
else:
    from settings.production import settings

del base_conf
