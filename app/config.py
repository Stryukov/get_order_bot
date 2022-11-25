import configparser
from dataclasses import dataclass


@dataclass
class Bot:
    token: str
    admin_id: int
    admin_group: str


@dataclass
class Config:
    bot: Bot


def load_config(path: str):
    cfg = configparser.ConfigParser()
    cfg.read(path)

    bot = cfg["bot"]

    return Config(
        bot=Bot(
            token=bot["token"],
            admin_id=int(bot["admin_id"]),
            admin_group=bot["admin_group"],
        )
    )
