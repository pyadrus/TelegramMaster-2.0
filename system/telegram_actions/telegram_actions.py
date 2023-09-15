import os
import os.path
import sqlite3
import time

from rich import print
from telethon import TelegramClient
from telethon.errors import *
from telethon.tl.functions.users import GetFullUserRequest

from system.error.telegram_errors import telegram_phone_number_banned_error
from system.proxy.checking_proxy import checking_the_proxy_for_work
from system.proxy.checking_proxy import reading_proxy_data_from_the_database
from system.setting.setting import reading_the_id_and_hash, reading_device_type
from system.sqlite_working_tools.sqlite_working_tools import cleaning_db
from system.sqlite_working_tools.sqlite_working_tools import open_the_db_and_read_the_data
from system.sqlite_working_tools.sqlite_working_tools import write_data_to_db


def connect_to_telegram_account_and_output_name(row):
    """Подключаемся телеграмм аккаунту и выводим имя"""
    phone, api_id, api_hash = get_from_the_list_phone_api_id_api_hash(row)  # Получаем со списка phone, api_id, api_hash
    proxy = reading_proxy_data_from_the_database()  # Proxy IPV6 - НЕ РАБОТАЮТ
    client = TelegramClient(f"user_settings/accounts/{phone}", api_id, api_hash, proxy=proxy)
    client.connect()  # Подсоединяемся к Telegram
    # Выводим командой print: имя, фамилию, номер телефона аккаунта
    first_name, last_name, phone = account_name(client, name_account="me")
    # Выводим результат полученного имени и номера телефона
    print(f"[bold red][!] Account connect {first_name} {last_name} {phone}")
    return client, phone


def account_name(client, name_account):
    """Показываем имя аккаунта с которого будем взаимодействовать"""
    full = client(GetFullUserRequest(name_account))
    for user in full.users:
        first_name = user.first_name if user.first_name else ""
        last_name = user.last_name if user.last_name else ""
        phone = user.phone if user.phone else ""
        return first_name, last_name, phone


def get_from_the_list_phone_api_id_api_hash(row):
    """Получаем со списка phone, api_id, api_hash"""
    users = {'id': int(row[0]), 'hash': row[1], 'phone': row[2]}
    # Вытягиваем данные из кортежа, для подстановки в функцию
    phone = users['phone']
    api_id = users['id']
    api_hash = users['hash']
    return phone, api_id, api_hash


def we_get_username_user_id_access_hash(rows):
    """Получаем username, user_id, access_hash"""
    user = {'username': rows[0]}
    # Вытягиваем данные из кортежа, для подстановки в функцию
    username = user["username"]
    return username, user


def writing_names_found_files_to_the_db() -> None:
    """Запись названий найденных файлов в базу данных """
    creating_a_table = "CREATE TABLE IF NOT EXISTS config(id, hash, phone)"
    writing_data_to_a_table = "INSERT INTO config (id, hash, phone) VALUES (?, ?, ?)"
    cleaning_db(name_database_table="config")  # Чистим базу данных с аккаунтами
    records = connecting_account_sessions()
    for entities in records:
        print(f"Записываем данные аккаунта {entities} в базу данных")
        write_data_to_db(creating_a_table, writing_data_to_a_table, entities)


def connecting_account_sessions():
    """Подключение сессий аккаунтов"""
    entities = []  # Создаем словарь
    """
    Функция listdir() модуля os возвращает список, содержащий имена файлов и директорий в каталоге, заданном путем 
    path user_settings/accounts
    """
    for x in os.listdir(path='user_settings/accounts'):
        """
        Функция str.endswith() возвращает True, если строка заканчивается заданным суффиксом (.session), 
        в противном случае возвращает False.
        """
        if x.endswith('.session'):
            """
            os.path.splitext(path) - разбивает путь на пару (root, ext), где ext начинается с точки и содержит не 
            более одной точки.
            """
            file = os.path.splitext(x)[0]
            print(f"Найденные аккаунты: {file}.session")  # Выводим имена найденных аккаунтов
            api_id_data, api_hash_data = reading_the_id_and_hash()  # Файл с настройками
            entities.append([api_id_data, api_hash_data, file])
    return entities


def renaming_a_session(client, phone_old, phone):
    """Переименование session файлов"""
    client.disconnect()  # Отключаемся от аккаунта для освобождения session файла
    try:
        # Переименование session файла
        os.rename(f"user_settings/accounts/{phone_old}.session", f"user_settings/accounts/{phone}.session")
    except FileExistsError:
        # Если файл существует, то удаляем дубликат
        os.remove(f"user_settings/accounts/{phone_old}.session")


def session_converter():
    """Конвертер session"""
    error_sessions = []  # Создаем словарь, для удаления битых файлов session
    print("[bold red] Проверка аккаунтов!")
    records: list = open_the_db_and_read_the_data(name_database_table="config")
    for row in records:
        # Получаем со списка phone, api_id, api_hash
        phone_old, api_id, api_hash = get_from_the_list_phone_api_id_api_hash(row)
        proxy = reading_proxy_data_from_the_database()  # Proxy IPV6 - НЕ РАБОТАЮТ
        try:
            device_model, system_version, app_version = reading_device_type()
            client = TelegramClient(f"user_settings/accounts/{phone_old}", api_id, api_hash, proxy=proxy,
                                    device_model=device_model, system_version=system_version, app_version=app_version)
            try:
                client.connect()  # Подсоединяемся к Telegram
                # Если аккаунт не авторизирован, то удаляем сессию
                if not client.is_user_authorized():
                    telegram_phone_number_banned_error(client, phone_old)  # Удаляем номер телефона с базы данных
                time.sleep(1)
                try:
                    # Показываем имя аккаунта с которым будем взаимодействовать
                    first_name, last_name, phone = account_name(client, name_account="me")
                    # Выводим результат полученного имени и номера телефона
                    print(f"[bold red][!] Account connect {first_name} {last_name} {phone}")
                    renaming_a_session(client, phone_old, phone)  # Переименование session файла
                except ConnectionError:
                    continue
            except AuthKeyDuplicatedError:
                # На данный момент аккаунт запущен под другим ip
                print(f"На данный момент аккаунт {phone_old} запущен под другим ip")
                # Отключаемся от аккаунта, что бы session файл не был занят другим процессом
                client.disconnect()
                try:
                    os.replace(f"user_settings/accounts/{phone_old}.session",
                               f"user_settings/accounts/invalid_account/{phone_old}.session")
                except FileNotFoundError:
                    # Если в папке accounts нет папки invalid_account, то создаем папку invalid_account
                    print("В папке accounts нет папки invalid_account, создаем папку invalid_account")
                    # Создаем папку invalid_account в папке accounts
                    os.makedirs("user_settings/accounts/invalid_account")
                    os.replace(f"user_settings/accounts/{phone_old}.session",
                               f"user_settings/accounts/invalid_account/{phone_old}.session")
            except (PhoneNumberBannedError, UserDeactivatedBanError):
                # Удаляем номер телефона с базы данных
                telegram_phone_number_banned_error(client, phone_old)  # Удаляем номер телефона с базы данных
        except sqlite3.DatabaseError:
            # session файл не является базой данных
            print(f"Битый файл {phone_old}.session")
            # Удаляем не валидную сессию
            error_sessions.append([phone_old])
    return error_sessions


def deleting_files_by_dictionary():
    """Удаление файлов по словарю"""
    checking_the_proxy_for_work()  # Проверка proxy
    writing_names_found_files_to_the_db()  # Сканируем папку с аккаунтами на наличие сессий
    error_sessions = session_converter()
    for row in error_sessions:
        try:
            print(f"Удаляем не валидный аккаунт {''.join(row)}.session")
            os.remove(f"user_settings/accounts/{''.join(row)}.session")
        except PermissionError:
            continue
    writing_names_found_files_to_the_db()  # Сканируем папку с аккаунтами на наличие сессий


if __name__ == "__main__":
    reading_proxy_data_from_the_database()
    connecting_account_sessions()
    deleting_files_by_dictionary()
