from loguru import logger
from telethon import TelegramClient
from telethon import functions
from telethon.errors import AuthKeyUnregisteredError

from system.auxiliary_functions.global_variables import api_id_data, api_hash_data
from system.proxy.checking_proxy import reading_proxy_data_from_the_database


def change_profile_descriptions(client):
    """Смена описания профиля"""
    user_input = input('Введите описание профиля, не более 70 символов: ')
    try:
        result = client(functions.account.UpdateProfileRequest(about=user_input))
        logger.info(result)
        logger.info("Профиль успешно обновлен!")
        client.disconnect()
    except AuthKeyUnregisteredError:
        logger.error("Ошибка соединения с профилем")


def change_bio_profile():
    """Изменение описания профиля"""
    user_input = input('Введите название файла, без session: ')
    proxy = reading_proxy_data_from_the_database()  # Proxy IPV6 - НЕ РАБОТАЮТ
    client = TelegramClient(f"user_settings/bio_accounts/accounts/{user_input}", api_id_data, api_hash_data,
                            system_version="4.16.30-vxCUSTOM", proxy=proxy)
    client.connect()  # Подсоединяемся к Telegram
    change_profile_descriptions(client)


if __name__ == "__main__":
    change_bio_profile()
