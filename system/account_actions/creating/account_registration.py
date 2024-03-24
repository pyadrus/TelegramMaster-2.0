from loguru import logger
from telethon import TelegramClient
from telethon import functions
from telethon.errors import AuthKeyUnregisteredError

from system.auxiliary_functions.global_variables import api_id_data, api_hash_data
from system.proxy.checking_proxy import reading_proxy_data_from_the_database


def change_profile_descriptions(client):
    """Смена описания профиля"""
    user_input: str = input('Введите описание профиля, не более 70 символов: ')
    try:
        result = client(functions.account.UpdateProfileRequest(about=user_input))
        logger.info(f'{result}\nПрофиль успешно обновлен!')
        client.disconnect()
    except AuthKeyUnregisteredError:
        logger.error("Ошибка соединения с профилем")


def telegram_connects(db_handler, session) -> TelegramClient:
    """Подключение к Telegram с помощью proxy
    :param db_handler: База данных
    :param session: Сессия Telegram
    """
    proxy = reading_proxy_data_from_the_database(db_handler)  # Proxy IPV6 - НЕ РАБОТАЮТ
    client = TelegramClient(session=session, api_id=api_id_data, api_hash=api_hash_data,
                            system_version="4.16.30-vxCUSTOM", proxy=proxy)
    logger.info(f"Подключение аккаунта: session, {api_id_data}, {api_hash_data}")
    client.connect()  # Подсоединяемся к Telegram

    return client  # Возвращаем клиент


def change_bio_profile(db_handler):
    """Изменение описания профиля"""
    user_input: str = input('Введите название файла, без session: ')
    client = telegram_connects(db_handler, session=f"user_settings/accounts/bio_accounts/{user_input}")
    change_profile_descriptions(client)
