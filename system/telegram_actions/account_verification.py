import os
import os.path
import sqlite3
import time

from loguru import logger
from rich import print
from telethon import TelegramClient
from telethon.errors import *

from system.error.telegram_errors import telegram_phone_number_banned_error
from system.proxy.checking_proxy import checking_the_proxy_for_work
from system.proxy.checking_proxy import reading_proxy_data_from_the_database
from system.sqlite_working_tools.sqlite_working_tools import DatabaseHandler
from system.telegram_actions.telegram_actions import account_name
from system.telegram_actions.telegram_actions import renaming_a_session
from system.telegram_actions.telegram_actions import writing_names_found_files_to_the_db

user_folder = "user_settings"
accounts_folder = "accounts"


def deleting_files_by_dictionary() -> None:
    """Удаление файлов по словарю"""
    checking_the_proxy_for_work()  # Проверка proxy
    writing_names_found_files_to_the_db()  # Сканируем папку с аккаунтами на наличие сессий
    error_sessions = account_verification()
    for row in error_sessions:
        try:
            print(f"Удаляем не валидный аккаунт {''.join(row)}.session")
            os.remove(f"{user_folder}/{accounts_folder}/{''.join(row)}.session")
        except PermissionError:
            continue
    writing_names_found_files_to_the_db()  # Сканируем папку с аккаунтами на наличие сессий


def account_verification():
    """Проверка аккаунтов"""
    error_sessions = []  # Создаем словарь, для удаления битых файлов session
    print("[medium_purple3] Проверка аккаунтов!")
    db_handler = DatabaseHandler()
    records: list = db_handler.open_and_read_data("config")
    for row in records:
        # Получаем со списка phone (row[2]), api_id (), api_hash
        proxy = reading_proxy_data_from_the_database()  # Proxy IPV6 - НЕ РАБОТАЮТ
        try:
            client = TelegramClient(f"{user_folder}/{accounts_folder}/{row[2]}", int(row[0]), row[1],
                                    system_version="4.16.30-vxCUSTOM", proxy=proxy)
            try:
                logger.info(f"Подключение аккаунта: {row[2]}, {int(row[0])}, {row[1]}")
                client.connect()  # Подсоединяемся к Telegram
                if not client.is_user_authorized():  # Если аккаунт не авторизирован, то удаляем сессию
                    telegram_phone_number_banned_error(client, row[2])  # Удаляем номер телефона с базы данных
                time.sleep(1)
                try:
                    # Показываем имя аккаунта с которым будем взаимодействовать
                    first_name, last_name, phone = account_name(client, name_account="me")
                    # Выводим результат полученного имени и номера телефона
                    print(f"[medium_purple3][!] Account connect {first_name} {last_name} {phone}")
                    renaming_a_session(client, row[2], phone)  # Переименование session файла
                except ConnectionError:
                    continue
            except AuthKeyDuplicatedError:
                # На данный момент аккаунт запущен под другим ip
                print(f"На данный момент аккаунт {row[2]} запущен под другим ip")
                # Отключаемся от аккаунта, что бы session файл не был занят другим процессом
                client.disconnect()
                try:
                    os.replace(f"{user_folder}/{accounts_folder}/{row[2]}.session",
                               f"{user_folder}/{accounts_folder}/invalid_account/{row[2]}.session")
                except FileNotFoundError:
                    # Если в папке accounts нет папки invalid_account, то создаем папку invalid_account
                    print("В папке accounts нет папки invalid_account, создаем папку invalid_account")
                    # Создаем папку invalid_account в папке accounts
                    os.makedirs("user_settings/accounts/invalid_account")
                    os.replace(f"{user_folder}/{accounts_folder}/{row[2]}.session",
                               f"{user_folder}/{accounts_folder}/invalid_account/{row[2]}.session")
            except (PhoneNumberBannedError, UserDeactivatedBanError):
                telegram_phone_number_banned_error(client, row[2])  # Удаляем номер телефона с базы данных
            except TimedOutError as e:
                logger.exception(e)
                time.sleep(2)
            except AuthKeyNotFound:  # session файл не является базой данных
                print(f"Битый файл {row[2]}.session")
                error_sessions.append([row[2]])  # Удаляем не валидную сессию
        except sqlite3.DatabaseError:  # session файл не является базой данных
            print(f"Битый файл {row[2]}.session")
            error_sessions.append([row[2]])  # Удаляем не валидную сессию
    return error_sessions


if __name__ == "__main__":
    account_verification()
