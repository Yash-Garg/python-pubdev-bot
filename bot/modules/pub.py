import requests
import telegram
import re

from bot import LOGGER, dispatcher
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, User, CallbackQuery, Message, Chat, Update
from telegram.ext import CommandHandler, run_async, CallbackQueryHandler


base_url = 'https://pub.dev/api/'

headers = {"content-Type": "application/json"}


def fetch_results(q: str):
    search_url = base_url + "search?q=" + q
    response = requests.get(search_url, headers=headers)
    data = response.json()
    if len(data['packages']) == 0:
        return "err"
    else:
        pkgdata = data['packages']
        return pkgdata


def fetch_pkg(k: str):
    pkgurl = base_url + "packages/" + k
    resp = requests.get(pkgurl, headers=headers)
    data = resp.json()
    pkginfo = data['latest']['pubspec']
    return pkginfo


@run_async
def search_pubdev(update, context):
    all_queries = update.message.text.split(" ")
    query = " ".join(all_queries[1:])
    templist = []
    finalList = []
    keyboard = []
    LOGGER.info(f"Searching: {query}")
    results = fetch_results(query)
    if results == 'err':
        context.bot.sendMessage(chat_id=update.effective_chat.id,
                                text="No packages available for your search query!",
                                reply_to_message_id=update.message.message_id)
    else:
        for i in range(0, len(results)):
            templist.append(results[i]['package'])
        finalList = templist[0:5]
        for i in range(len(finalList)):
            keyboard = keyboard + \
                [[InlineKeyboardButton(
                    finalList[i], callback_data="callback_{}".format(finalList[i]))]]
        context.bot.sendMessage(chat_id=update.effective_chat.id,
                                text="*Available packages for your search query :*",
                                reply_to_message_id=update.message.message_id,
                                reply_markup=InlineKeyboardMarkup(keyboard),
                                parse_mode=ParseMode.MARKDOWN_V2)


@run_async
def answerCallback(update, context):
    query = update.callback_query
    finalQuery = str(query.data).replace("callback_", "")
    data = fetch_pkg(finalQuery)

    version = data['version']
    description = data['description']
    deps = data['dependencies']
    fdeps = ", ".join(deps)
    pubdev_url = "https://pub.dev/packages/" + data['name']
    github_url = data['homepage']

    msg_string = f"""*Package name :* `{finalQuery}`\n*Latest version :* `{version}`
                    \n*Description :* `{description}`\n\n*Dependencies :* `{fdeps}`\n\n*Pubspec :* `{finalQuery} ^{version}`
                """
    CallbackQuery.answer(query)
    keyboard = [
        [InlineKeyboardButton("Github", url=github_url),
         InlineKeyboardButton("Pub.dev", url=pubdev_url),
         ]
    ]
    query.edit_message_text(
        text=msg_string,
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


pub_handler = CommandHandler('pub', search_pubdev)
callback_query_handler = CallbackQueryHandler(
    answerCallback, pattern=f"callback_")
dispatcher.add_handler(pub_handler)
dispatcher.add_handler(callback_query_handler)
