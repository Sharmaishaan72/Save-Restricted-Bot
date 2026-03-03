import os
import json

def open_config():
    """fetch the latest config , everytime , on reload_env"""
    return json.load(open("config.json",'r'))


def getenv(var): return os.environ.get(var) or open_config().get(var, None)


class Config:
    def __init__(self):
        self.reload_env()

    def reload_env(self):
        self.bot_token = getenv("TOKEN")
        self.api_hash = getenv("HASH")
        self.api_id = getenv("ID")
        self.ss = getenv("STRING")
        self.owner_ids = [
            int(owner_id)
            for owner_id in getenv("OWNER_USERIDS").split(",")
        ]

config = Config()