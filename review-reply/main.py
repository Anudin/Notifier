from flask.wrappers import Request, Response
import telegram
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, Dispatcher, CallbackContext, CallbackQueryHandler
from shared import bot
from functools import partial

# TODO Use Updater for local development / testing

# See https://github.com/python-telegram-bot/python-telegram-bot/wiki/Webhooks#custom-solution

initialized = False
decode_update = None
dispatcher = None
review_notifier_send = None


def on_review_reply(request: Request):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
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
