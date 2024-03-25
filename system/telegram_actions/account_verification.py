import os
import os.path
import platform
import sqlite3
import time
import urllib.request

import getmac
from loguru import logger
from rich import print
from telethon.errors import *

from system.account_actions.checking_spam.account_verification import working_with_accounts
from system.account_actions.creating.account_registration import telegram_connects
from system.error.telegram_errors import telegram_phone_number_banned_error
from system.proxy.checking_proxy import checking_the_proxy_for_work
from system.telegram_actions.telegram_actions import account_name
from system.telegram_actions.telegram_actions import renaming_a_session
from system.telegram_actions.telegram_actions import writing_names_found_files_to_the_db


def deleting_files_by_dictionary(db_handler) -> None:
    """Удаление файлов по словарю"""

    logger.info(f"{platform.uname()}, "
                f"{getmac.get_mac_address()}, "
                f"{urllib.request.urlopen('https://ident.me').read().decode('utf8')}")

    checking_the_proxy_for_work(db_handler)  # Проверка proxy
    writing_names_found_files_to_the_db(db_handler)  # Сканируем папку с аккаунтами на наличие сессий
    error_sessions = account_verification(db_handler)
    for row in error_sessions:
        try:
            print(f"Удаляем не валидный аккаунт {''.join(row)}.session")
            os.remove(f"user_settings/accounts/{''.join(row)}.session")
        except PermissionError:
            continue
    writing_names_found_files_to_the_db(db_handler)  # Сканируем папку с аккаунтами на наличие сессий


def account_verification(db_handler):
    """Проверка аккаунтов"""
    error_sessions = []  # Создаем словарь, для удаления битых файлов session
    print("[medium_purple3] Проверка аккаунтов!")
    records: list = db_handler.open_and_read_data("config")
    for row in records:
        try:
            client = telegram_connects(db_handler, session=f"user_settings/accounts/{row[2]}")
            try:
                if not client.is_user_authorized():  # Если аккаунт не авторизирован, то удаляем сессию
                    telegram_phone_number_banned_error(client=client, phone=row[2], db_handler=db_handler)  # Удаляем номер телефона с базы данных
                time.sleep(1)
                try:
                    # Показываем имя аккаунта с которым будем взаимодействовать
                    first_name, last_name, phone = account_name(client, name_account="me")
                    # Выводим результат полученного имени и номера телефона
                    print(f"[medium_purple3][!] Account connect {first_name} {last_name} {phone}")
                    renaming_a_session(client, row[2], phone)  # Переименование session файла
                except ConnectionError:
                    continue
            except AuthKeyDuplicatedError:  # На данный момент аккаунт запущен под другим ip
                print(f"На данный момент аккаунт {row[2]} запущен под другим ip")
                # Отключаемся от аккаунта, что бы session файл не был занят другим процессом
                client.disconnect()
                working_with_accounts(account_folder=f"user_settings/accounts/{row[2]}.session",
                                      new_account_folder=f"user_settings/accounts/invalid_account/{row[2]}.session")
            except (PhoneNumberBannedError, UserDeactivatedBanError):
                telegram_phone_number_banned_error(client, row[2], db_handler)  # Удаляем номер телефона с базы данных
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
