from aiogram import Bot, Dispatcher, executor, types
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from urllib.parse import urlparse
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

logger = logging.getLogger(__name__)

# Initialize bot and dispatcher
bot = Bot(token=os.environ.get('TELEGRAM_TOKEN'))
dp = Dispatcher(bot)

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=os.environ.get('SPOTIFY_CLIENT_ID'),
                                                           client_secret=os.environ.get('SPOTIFY_CLIENT_SECRET')))


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
    "https://open.spotify.com/track/2JkgWYgWqPetRvhvekdmY6?si=11fe853db1c6438f"
    s = urlparse(message.text)
    path = s.path
    if path.startswith('/'):
        path = path[1:]
    try:
        urn = 'spotify:' + path.replace('/', ':')
        track = sp.track(urn)
        await message.reply("echo :\n{}".format(track['name']))
    except Exception as e:
        await message.reply("echo :\n{}".format(e))


def main():
    executor.start_polling(dp, skip_updates=True)


if __name__ == '__main__':
    main()
