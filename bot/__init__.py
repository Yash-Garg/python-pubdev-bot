import logging
import os

import telegram.ext as tg
from dotenv import load_dotenv

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

load_dotenv('config.env')

LOGGER = logging.getLogger(__name__)

try:
    BOT_TOKEN = os.environ['BOT_TOKEN']
except KeyError as e:
    LOGGER.error(e)
    exit(1)

updater = tg.Updater(token=BOT_TOKEN, use_context=True)
bot = updater.bot
dispatcher = updater.dispatcher
