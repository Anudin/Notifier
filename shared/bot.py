from collections import defaultdict
from dataclasses import dataclass
from typing import Optional


@dataclass
class BotConfig:
    token: str
    chat_id: Optional[str]


def read_config(path) -> BotConfig:
    import json

    with open(path) as f:
        config = json.load(f)
        config = defaultdict(None, config)
        return BotConfig(config["token"], config["chat_id"])


def send_message(bot, chat_id, message):
    from telegram.error import TelegramError

    try:
        bot.sendMessage(chat_id=chat_id, text=message)
    except TelegramError as e:
        print(f"Failed to send Telegram message { e }")
