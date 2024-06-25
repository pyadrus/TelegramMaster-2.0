# -*- coding: utf-8 -*-
import os
import os.path

from loguru import logger
# from telethon.errors import *
from telethon.tl.functions.users import GetFullUserRequest

from system.auxiliary_functions.auxiliary_functions import find_files
from system.auxiliary_functions.global_variables import ConfigReader

configs_reader = ConfigReader()
api_id_data, api_hash_data = configs_reader.get_api_id_data_api_hash_data()


def working_with_accounts(account_folder, new_account_folder) -> None:
    """Работа с аккаунтами"""
    try:  # Переносим файлы в нужную папку
        os.replace(account_folder, new_account_folder)
    except FileNotFoundError:  # Если в папке нет нужной папки, то создаем ее
        os.makedirs(new_account_folder)
        os.replace(account_folder, new_account_folder)


"""Получаем имя аккаунта (переписать на асинхронку)"""


def account_name(client, name_account):
    """Показываем имя аккаунта с которого будем взаимодействовать"""
    try:
        full = client(GetFullUserRequest(name_account))
        for user in full.users:
            first_name = user.first_name if user.first_name else ""
            last_name = user.last_name if user.last_name else ""
            phone = user.phone if user.phone else ""
            return first_name, last_name, phone
    except TypeNotFoundError as e:
        print(f"TypeNotFoundError: {e}")


async def writing_names_found_files_to_the_db(db_handler) -> None:
    """Запись названий найденных файлов в базу данных"""
    await db_handler.cleaning_db(name_database_table="config")  # Call the method on the instance
    records = find_files(directory_path="user_settings/accounts", extension="session")
    for entities in records:
        logger.info(f"Записываем данные аккаунта {entities} в базу данных")
        await db_handler.write_data_to_db(creating_a_table="CREATE TABLE IF NOT EXISTS config(phone)",
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
