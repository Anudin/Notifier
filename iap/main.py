import base64
import json


# https://developer.android.com/google/play/billing/rtdn-reference#one-time
def on_one_time_product_notification(event, context):
    print(
        f"This Function was triggered by messageId {context.event_id} published at {context.timestamp}"
    )
    _on_one_time_product_notification(event)


def _on_one_time_product_notification(event):
    if "data" in event:
        data = base64.b64decode(event["data"]).decode("utf-8")
        data = json.loads(data)
        print(f"The publish data was decoded as {data}")
        if "testNotification" in data:
            bot_send_message(data)
        elif "oneTimeProductNotification" in data:
            if data["oneTimeProductNotification"]["notificationType"] == 1:
                bot_send_message(data["oneTimeProductNotification"]["sku"])


def bot_send_message(message):
    import telegram
    from telegram.error import TelegramError

    with open("secrets.json") as f:
        secrets = json.load(f)
        try:
            bot = telegram.Bot(token=secrets["TELEGRAM_TOKEN"])
            bot.sendMessage(chat_id=secrets["TELEGRAM_CHAT_ID"], text=message)
        except TelegramError as e:
            print(f"Failed to send Telegram message { e }")
