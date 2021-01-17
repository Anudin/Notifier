from telegram import Bot
from dataclasses import dataclass
from typing import Optional


# TODO chat_id should be Optional[list[str]], adjust depending code
@dataclass
class BotConfig:
    """Static configuration data for a Telegram bot, optionally specifying a fixed list of chats to work with."""

    token: str
    chat_id: Optional[str]


def read_config(path) -> BotConfig:
    import json

    with open(path) as f:
        config = json.load(f)
        return BotConfig(config["token"], config.get("chatId"))


# TODO Check out functools.wraps
def send_message(bot: Bot, chat_id: str, message: str, config: BotConfig = None, **kwargs):
    """Fire and forget Telegram message sending. Swallows errors, optionally restricts allowed chats."""
    from telegram.error import TelegramError

    if config and chat_id != config.chat_id:
        return print(f"Tried sending a message to {chat_id}, not allowed")

    try:
        return bot.sendMessage(chat_id=chat_id, text=message, **kwargs)
    except TelegramError as e:
        return print(f"Failed to send Telegram message { e }")
