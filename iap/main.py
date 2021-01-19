import base64
import json

ONE_TIME_PRODUCT_PURCHASED = 1


def on_one_time_product_notification(event, context):
    """This endpoint handles messages published by RTDN (specifically OneTimeProductNotification for now).
    RTDN only works with subscription changes or PENDING purchases, you will not receive messages about one time
    purchases in most cases (see https://developer.android.com/google/play/billing/getting-ready#configure-rtdn).
    To learn about available messages, see https://developer.android.com/google/play/billing/rtdn-reference.
    """
    print(
        f"This Function was triggered by messageId {context.event_id} published at {context.timestamp}"
    )
    _on_one_time_product_notification(event)


def _on_one_time_product_notification(event):
    if "data" in event:
        data = base64.b64decode(event["data"]).decode("utf-8")
        data = json.loads(data)
        print(f"Received RTDN publish {data}")
        if "testNotification" in data:
            bot_send_message(data)
        elif "oneTimeProductNotification" in data:
            if (
                data["oneTimeProductNotification"]["notificationType"]
                == ONE_TIME_PRODUCT_PURCHASED
            ):
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
