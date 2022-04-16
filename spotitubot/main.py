import logging
import os
from typing import List

from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, executor, types

from re import search
from requests import get
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from urllib.parse import urlparse
from ytmusicapi import YTMusic

load_dotenv()  # take environment variables from .env.

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

logger = logging.getLogger(__name__)

# Initialize bot and dispatcher
bot = Bot(token=os.environ.get('TELEGRAM_TOKEN'))
dp = Dispatcher(bot)

agent = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36 Edg/97.0.1072.69"}

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=os.environ.get('SPOTIFY_CLIENT_ID'),
                                                           client_secret=os.environ.get('SPOTIFY_CLIENT_SECRET')))
ytmusic = YTMusic()

# todo: auto checked that name and author are correct!
# todo: github actions


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.reply("Hi! I'm Spotitubot!\n\nThe bot that search the music in spotify and youtube music, "
                        "by providing links, e.g. \n"
                        " - in: spotify link (youtube music link)\n"
                        " - out: youtube music link (spotify link)\n\n"
                        "Powered by aiogram.")


@dp.message_handler()
async def echo(message: types.Message):
    res = []
    for url in parse_links(message.entities, message.text):
        try:
            logger.info(f"{url} - Processing...")
            if 'open.spotify' in url:
                res.append(spoti_to_youtube(url))
            elif 'music.youtube' in url:
                res.append(youtube_to_spoti(url))
            else:
                res.append(f"Skipped: {url})")
            logger.info(f"{url} - Complete.")
        except Exception as e:
            res.append(e)
    await message.reply("\n".join(res))


def youtube_to_spoti(url):
    s = urlparse(url)
    id_ = s.query.split("=")[-1]
    logger.info(f"{url} - Parsed id : {id_}")
    metadata = ytmusic.get_song(str(id_))
    query = f"artist:{metadata['videoDetails']['author']} track:{metadata['videoDetails']['title']}"
    logger.info(f"{url} - Searching for {query}...")
    res = sp.search(query, limit=1, offset=0, type='track', market=None)
    if len(res['tracks']['items']) > 0:
        return res['tracks']['items'][0]['external_urls']['spotify']
    return f"Nothing found for {url}"


def spoti_to_youtube(url):
    s = urlparse(url)
    path = s.path
    if path.startswith('/'):
        path = path[1:]
    urn = 'spotify:' + path.replace('/', ':')
    logger.info(f"{url} - Searching for {urn}")
    track = sp.track(urn)
    logger.info(f"{url} - Searching for {track['name']}")
    id_ = search('"videoId":".{11}"',
                 get(f"https://music.youtube.com/search?q={track['name']}", headers=agent).content.decode(
                     "unicode_escape"))
    if id_ is None:
        return f"Nothing found for {url}"
    id_ = id_.group().split(":")[1].replace('"', "")
    return f"https://music.youtube.com/watch?v={id_}"


def parse_links(entities: List[types.MessageEntity], text: str):
    res = set()
    for entity in entities:
        if entity.type == 'text_link':
            res.add(entity.url)
        elif entity.type == 'url':
            res.add(text[entity.offset:entity.offset + entity.length])
        else:
            logger.warning('got unknown type: {}'.format(entity.type))
    return res


def main():
    executor.start_polling(dp, skip_updates=True)


if __name__ == '__main__':
    main()
