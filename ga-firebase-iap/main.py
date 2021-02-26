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
    price = event["params"]["price"]["doubleValue"]
    value_in_usd = event["valueInUsd"]
    currency = event["params"]["currency"]["stringValue"]
    bot_send_message(f"Fat stacks coming in 💸\n{price} {currency} (or {value_in_usd}$)")


def bot_send_message(message):
    import json
    import telegram
    from telegram.error import TelegramError

    with open("secrets.json") as f:
        secrets = json.load(f)
        try:
            bot = telegram.Bot(token=secrets["token"])
            bot.sendMessage(chat_id=secrets["chatId"], text=message)
        except TelegramError as e:
            print(f"Failed to send Telegram message { e }")
