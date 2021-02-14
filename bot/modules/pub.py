import requests

from bot import LOGGER, dispatcher
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, CallbackQuery
from telegram.ext import CommandHandler, run_async, CallbackQueryHandler


base_url = 'https://pub.dev/api/'

headers = {"content-Type": "application/json"}

result_keyboard = []


def fetch_results(q: str):
    search_url = base_url + "search?q=" + q
    response = requests.get(search_url, headers=headers)
    data = response.json()
    templist = []
    finalList = []
    keyboard = []
    if len(data['packages']) == 0:
        return "err"
    else:
        pkgdata = data['packages']
        for i in range(len(pkgdata)):
            templist.append(pkgdata[i]['package'])
        finalList = templist[0:5]
        for i in range(len(finalList)):
            keyboard = keyboard + \
                [[InlineKeyboardButton(
                    finalList[i], callback_data="callback_{}".format(finalList[i]))]]
        return InlineKeyboardMarkup(keyboard)


def fetch_pkg(k: str):
    pkgurl = base_url + "packages/" + k
    resp = requests.get(pkgurl, headers=headers)
    data = resp.json()
    pkginfo = data['latest']['pubspec']
    return pkginfo


def search_pubdev(update, context):
    all_queries = update.message.text.split(" ")
    query = " ".join(all_queries[1:])
    LOGGER.info(f"Searching: {query}")
    global result_keyboard
    result_keyboard = fetch_results(query)
    if result_keyboard == 'err':
        context.bot.sendMessage(chat_id=update.effective_chat.id,
                                text="No packages available for your search query!",
                                reply_to_message_id=update.message.message_id)
    else:
        context.bot.sendMessage(chat_id=update.effective_chat.id,
                                text="*Available packages for your search query :*",
                                reply_to_message_id=update.message.message_id,
                                reply_markup=result_keyboard,
                                parse_mode=ParseMode.MARKDOWN_V2)


def answerCallback(update, context):
    query = update.callback_query
    finalQuery = str(query.data).replace("callback_", "")
    data = fetch_pkg(finalQuery)

    version = data['version']
    description = data['description'].rstrip()
    pubdev_url = "https://pub.dev/packages/" + data['name']
    github_url = data['homepage']

    msg_string = f"""*Package name :* `{finalQuery}`\n*Latest version :* `{version}`
                    \n*Description :* `{description}`\n\n*Pubspec :* `{finalQuery} ^{version}`
                """
    CallbackQuery.answer(query)
    keyboard = [
        [InlineKeyboardButton("Github", url=github_url),
         InlineKeyboardButton("Pub.dev", url=pubdev_url),
         InlineKeyboardButton("Back", callback_data="back"),
         ]
    ]
    query.edit_message_text(
        text=msg_string,
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


def answerBackQuery(update, context):
    query = update.callback_query
    CallbackQuery.answer(query)
    query.edit_message_text(
        text="*Available packages for your search query :*",
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=result_keyboard
    )


pub_handler = CommandHandler('pub', search_pubdev, run_async=True)
callback_query_handler = CallbackQueryHandler(
    answerCallback, pattern=f'{"callback_"}', run_async=True)
back_query_handler = CallbackQueryHandler(
    answerBackQuery, pattern=f'{"back"}', run_async=True)
dispatcher.add_handler(pub_handler)
dispatcher.add_handler(callback_query_handler)
dispatcher.add_handler(back_query_handler)
