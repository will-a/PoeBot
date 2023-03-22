import re
import sys
import yaml
import logging
from discord import Client, Message


logging.basicConfig(level=logging.INFO)

client = Client()
required_config_fields = ['discord_token', 'build_code_paths']
config_dict = {}


def read_config(config_file_name: str) -> None:
    try:
        with open(config_file_name, 'r', encoding='utf-8') as config_file:
            config_dict_raw = yaml.load(config_file, Loader=yaml.Loader)
            if any(field not in config_dict_raw for field in required_config_fields):
                logging.error("Discord token not found in config.")
            global config_dict
            config_dict = config_dict_raw
    except FileNotFoundError as fnf_error:
        logging.error(fnf_error.strerror)
        sys.exit(1)


@client.event
async def on_ready():
    logging.info("Logged in as %s", client.user)


@client.event
async def on_message(message: Message):
    if message.author == client.user:
        return  # ignore bot's messages

    if not len(message.content):
        return

    if message.content[0] == '!':  # message is a command
        logging.info(message.content[1:].split(' '))
        match message.content[1:].split(' '):
            case ['pob', url]:
                await message.channel.send(f"Your URL is {url}")
            case ['pob', *_]:
                await message.channel.send("Did you mean `!pob <url>`?")
            case _:
                await message.channel.send("Command unrecognized.")


def main():
    config_dict = read_config('config.yaml')
    client.run(config_dict.get('discord_token'))


if __name__ == '__main__':
    main()
