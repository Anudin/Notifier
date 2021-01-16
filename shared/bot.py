from dataclasses import dataclass
from typing import Optional


# TODO chat_id should be Optional[list[str]]
@dataclass
class BotConfig:
    token: str
    chat_id: Optional[str]


def read_config(path) -> BotConfig:
    import json

    with open(path) as f:
        config = json.load(f)
        return BotConfig(config["token"], config.get("chatId"))


def send_message(bot, chat_id, message, **kwargs):
    from telegram.error import TelegramError

    try:
        bot.sendMessage(chat_id=chat_id, text=message, **kwargs)
    except TelegramError as e:
        print(f"Failed to send Telegram message { e }")
