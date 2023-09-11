import os
from time import time
from Config import Config
from Commands import *
from SelfMusicBot import SelfMusicBot

token_file = open("token.txt")
token = token_file.readline()
token_file.close()

config = Config()

def create_default_config():
    config_file = open("config.json", "w")
    config_file.write(config.export_json())
    config_file.close()

if not os.path.exists("config.json"):
    create_default_config()
else:
    try:
        config_file = open("config.json", "r")
        config.import_json(config_file.read())
        config_file.close()
    except Exception as ex:
        print(f"Unable to load the config: {ex}")
        os.rename("config.json", f"config_broken_{int(time() * 1000)}.json")
        create_default_config()
    
instance = SelfMusicBot(config)
instance.run(token, root_logger=True)