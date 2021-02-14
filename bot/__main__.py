from telegram.ext import CommandHandler, run_async
from bot import dispatcher, updater, LOGGER
from .modules import pub


def start(update, context):
    context.bot.send_message(update.effective_chat.id,
                             "Hello there! I'm a bot, nice meeting you.")


def main():
    start_handler = CommandHandler('start', start, run_async=True)
    dispatcher.add_handler(start_handler)
    updater.start_polling()
    LOGGER.info("Bot Started!")


main()
