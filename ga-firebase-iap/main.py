def on_in_app_purchase(data, context):
    """This endpoint is triggered by Google Analytics for Firebase (specifically in_app_purchase),
    see https://cloud.google.com/functions/docs/calling/google-analytics-firebase,
    see also https://firebase.google.com/docs/functions/analytics-events
    """
    trigger_resource = context.resource
    print(f"Function triggered by the following event: {trigger_resource}")
    _on_in_app_purchase(data)


def _on_in_app_purchase(data):
    event = data["eventDim"][0]
    print(f"Function triggered with event data {event}")
    bot_send_message(f"{event.valueInUSD} {event.params}")


def bot_send_message(message):
    import json
    import telegram
    from telegram.error import TelegramError

    with open("secrets.json") as f:
        secrets = json.load(f)
        try:
            bot = telegram.Bot(token=secrets["TELEGRAM_TOKEN"])
            bot.sendMessage(chat_id=secrets["TELEGRAM_CHAT_ID"], text=message)
        except TelegramError as e:
            print(f"Failed to send Telegram message { e }")
