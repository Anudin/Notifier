import telegram
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, Dispatcher
from shared import bot

# TODO Use Updater for local development / testing

# See https://github.com/python-telegram-bot/python-telegram-bot/wiki/Webhooks#custom-solution

decode_update = None
dispatcher = None
review_notifier_send = None

# See https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data
def on_review_reply(request):
    """
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """
    init()
    request_json = request.get_json(force=True, silent=True)
    update = decode_update(request_json)
    dispatcher.process_update(update)
    return "ok"


# Maybe we can reuse something, see
# https://cloud.google.com/functions/docs/bestpractices/tips#use_global_variables_to_reuse_objects_in_future_invocations
def init():
    global decode_update, dispatcher, review_notifier_send

    if not review_notifier_send:
        config = bot.read_config("secrets.json")
        review_notifier_bot = telegram.Bot(token=config.token)
        decode_update = lambda json_dict: Update.de_json(json_dict, review_notifier_bot)
        dispatcher = Dispatcher(review_notifier_bot, None, workers=0)
        # TODO Register handlers
        review_notifier_send = lambda message, **kwargs: bot.send_message(
            review_notifier_bot, config.chat_id, message, **kwargs
        )
