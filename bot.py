import re
import sys
import logging
from typing import Optional

import yaml
import requests
from discord import Client, Message, Intents


logging.basicConfig(level=logging.INFO)

client = Client(intents=Intents(message_content=True, messages=True, typing=True))
required_config_fields = ['discord_token']
build_code_paths = {
    'pobb.in': 'https://pobb.in/:id:/raw',
    'pastebin.com': 'https://pastebin.com/raw/:id:'
}

# Read config file
logging.info("Reading configs")
try:
    with open('config.yaml', 'r', encoding='utf-8') as config_file:
        config_dict = yaml.load(config_file, Loader=yaml.Loader)
        if any(field not in config_dict for field in required_config_fields):
            logging.error("Discord token not found in config.")
            sys.exit(1)
        logging.info("Successfully read configs")
except FileNotFoundError as fnf_error:
    logging.error(fnf_error.strerror)
    sys.exit(1)


def get_url_info(url: str) -> tuple:
    url_r = re.compile(r'^(http(s)?:\/\/)?(www.)?(?P<url_base>\w+\.\w+)\/(?P<paste_id>\w+)')
    url_base = url_r.search(url)
    if not url_base:
        return None, None
    return url_base.group('url_base'), url_base.group('paste_id')


def get_raw_build_code(base_url: str, paste_id: str) -> Optional[str]:
    request_url_raw = build_code_paths.get(base_url)
    if not request_url_raw:
        return None
    request_url = request_url_raw.replace(':id:', paste_id)
    logging.info(request_url)

    resp = requests.get(url=request_url)
    if resp.status_code != 200:
        return None
    return resp.text


def get_build_url(url: str) -> Optional[str]:
    base_url, paste_id = get_url_info(url)
    if not base_url:
        logging.warning("Bad URL parse")
        return None
    build_code = get_raw_build_code(base_url, paste_id)
    if not build_code:
        logging.warning("Build code not generated")
        return None
    resp = requests.post(url='https://poe.ninja/pob/api/api_post.php', data={'api_paste_code': build_code})
    if resp.status_code != 200:
        logging.warning("Could not generate POB link")
        return None
    return resp.text


@client.event
async def on_ready():
    logging.info("Logged in as %s", client.user)


@client.event
async def on_message(message: Message):
    if message.author == client.user:
        return  # ignore bot's messages

    if len(message.content) == 0:
        return

    logging.info("Received message '%s'", message.content)

    if message.content[0] == '!':  # message is a command
        logging.info(message.content[1:].split(' '))
        match message.content[1:].split(' '):
            case ['pob', url]:
                build_url = get_build_url(url)
                if not build_url:
                    await message.channel.send("Error generating build URL. @w1ll#9484")
                    return
                await message.channel.send(get_build_url(url))
            case ['pob', *_]:
                await message.channel.send("Did you mean `!pob <url>`?")
            case _:
                await message.channel.send("Command unrecognized.")


def main():
    client.run(config_dict.get('discord_token'))


if __name__ == '__main__':
    main()
