import os
import os.path

from loguru import logger
# from rich import print
from telethon import TelegramClient
from telethon.errors import *
from telethon.tl.functions.users import GetFullUserRequest
import asyncio
from system.auxiliary_functions.auxiliary_functions import find_files
from system.auxiliary_functions.global_variables import ConfigReader
from system.proxy.checking_proxy import reading_proxy_data_from_the_database

configs_reader = ConfigReader()
api_id_data, api_hash_data = configs_reader.get_api_id_data_api_hash_data()


def working_with_accounts(account_folder, new_account_folder) -> None:
    """Работа с аккаунтами"""
    try:  # Переносим файлы в нужную папку
        os.replace(account_folder, new_account_folder)
    except FileNotFoundError:  # Если в папке нет нужной папки, то создаем ее
        os.makedirs(new_account_folder)
        os.replace(account_folder, new_account_folder)


async def telegram_connects(db_handler, session) -> TelegramClient:
    """Подключение к Telegram с помощью proxy
    :param db_handler: База данных
    :param session: Сессия Telegram
    """
    proxy = await reading_proxy_data_from_the_database(db_handler)  # Proxy IPV6 - НЕ РАБОТАЮТ
    client = TelegramClient(session, api_id=api_id_data, api_hash=api_hash_data,
                            system_version="4.16.30-vxCUSTOM", proxy=proxy)
    print(f"Подключение аккаунта: {session.split('/')[-1]}, {api_id_data}, {api_hash_data}")
    try:
        await client.connect()  # Подсоединяемся к Telegram
        return client  # Возвращаем клиент
    except AuthKeyDuplicatedError:  # На данный момент аккаунт запущен под другим ip
        print(f"На данный момент аккаунт {session.split('/')[-1]} запущен под другим ip")
        # Отключаемся от аккаунта, что бы session файл не был занят другим процессом
        await client.disconnect()
        working_with_accounts(account_folder=f"user_settings/accounts/{session.split('/')[-1]}.session",
                              new_account_folder=f"user_settings/accounts/invalid_account/{session.split('/')[-1]}.session")


async def telegram_connect_and_output_name(row, db_handler):
    """Подключаемся телеграмм аккаунту и выводим имя"""
    print(row[0])
    client = await telegram_connects(db_handler, f"user_settings/accounts/{row[0]}")
    # Выводим командой print: имя, фамилию, номер телефона аккаунта
    # first_name, last_name, phone = account_name(client, name_account="me")
    # Выводим результат полученного имени и номера телефона
    # logger.info(f"[!] Account connect {first_name} {last_name} {phone}")
    return client


"""Получаем имя аккаунта (переписать на асинхронку)"""


# def account_name(client, name_account):
#     """Показываем имя аккаунта с которого будем взаимодействовать"""
#     try:
#         full = client(GetFullUserRequest(name_account))
#         for user in full.users:
#             first_name = user.first_name if user.first_name else ""
#             last_name = user.last_name if user.last_name else ""
#             phone = user.phone if user.phone else ""
#             return first_name, last_name, phone
#     except TypeNotFoundError as e:
#         print(f"TypeNotFoundError: {e}")


def writing_names_found_files_to_the_db(db_handler) -> None:
    """Запись названий найденных файлов в базу данных"""
    db_handler.cleaning_db(name_database_table="config")  # Call the method on the instance
    records = find_files(directory_path="user_settings/accounts", extension="session")
    for entities in records:
        print(f"Записываем данные аккаунта {entities} в базу данных")
        db_handler.write_data_to_db(creating_a_table="CREATE TABLE IF NOT EXISTS config(phone)",
                                    writing_data_to_a_table="INSERT INTO config (phone) VALUES (?)",
                                    entities=entities)


def renaming_a_session(client, phone_old, phone) -> None:
    """Переименование session файлов"""
    client.disconnect()  # Отключаемся от аккаунта для освобождения session файла
    try:
        # Переименование session файла
        os.rename(f"user_settings/accounts/{phone_old}.session", f"user_settings/accounts/{phone}.session", )
    except FileExistsError:
        # Если файл существует, то удаляем дубликат
        os.remove(f"user_settings/accounts/{phone_old}.session")
