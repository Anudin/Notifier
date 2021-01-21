from flask.wrappers import Request, Response
import telegram
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, Dispatcher, CallbackContext, CallbackQueryHandler
from shared import bot
from functools import partial

initialized = False
decode_update = None
dispatcher = None
review_notifier_send = None


def on_review_reply(request: Request):
    """HTTP Cloud Function.
    Configure this endpoint as a webhook for your telegram bot, so it will receive updates.
    See https://core.telegram.org/bots/webhooks#how-do-i-set-a-webhook-for-either-type
    Based on https://github.com/python-telegram-bot/python-telegram-bot/wiki/Webhooks#custom-solution
    """
    initialize()
    request_json = request.get_json(force=True, silent=True)
    update = decode_update(request_json)
    dispatcher.process_update(update)
    return ""


# Maybe we can reuse something, see
# https://cloud.google.com/functions/docs/bestpractices/tips#use_global_variables_to_reuse_objects_in_future_invocations
def initialize():
    global initialized
    global decode_update, dispatcher, review_notifier_send

    if not initialized:
        config = bot.read_config("secrets.json")
        review_notifier_bot = telegram.Bot(token=config.token)

        decode_update = lambda json_dict: Update.de_json(json_dict, review_notifier_bot)
        dispatcher = Dispatcher(review_notifier_bot, None, workers=0)
        dispatcher.add_handler(CallbackQueryHandler(handle_reply))
        review_notifier_send = partial(
            bot.send_message, review_notifier_bot, config.chat_id
        )
        initialized = True


def handle_reply(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    query.edit_message_text(f"Your wish is {query.data}. It shall be granted")
