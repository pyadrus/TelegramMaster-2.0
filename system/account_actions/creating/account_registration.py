from loguru import logger
from telethon import functions
from telethon.errors import AuthKeyUnregisteredError

from system.telegram_actions.telegram_actions import telegram_connects


def change_profile_descriptions(client):
    """Смена описания профиля"""
    user_input: str = input('Введите описание профиля, не более 70 символов: ')
    try:
        result = client(functions.account.UpdateProfileRequest(about=user_input))
        logger.info(f'{result}\nПрофиль успешно обновлен!')
        client.disconnect()
    except AuthKeyUnregisteredError:
        logger.error("Ошибка соединения с профилем")


def change_bio_profile(db_handler):
    """Изменение описания профиля"""
    user_input: str = input('Введите название файла, без session: ')
    client = telegram_connects(db_handler, session=f"user_settings/accounts/bio_accounts/{user_input}")
    change_profile_descriptions(client)
