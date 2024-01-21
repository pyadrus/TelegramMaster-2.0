# import time

# from rich import print
# from telethon.errors import YouBlockedUserError
from telethon.sync import TelegramClient  # Не удалять, так как используется кодом
from system.error.telegram_errors import record_account_actions
from system.notification.notification import app_notifications
# from system.sqlite_working_tools.sqlite_working_tools import DatabaseHandler
from system.telegram_actions.telegram_actions import connect_to_telegram_account_and_output_name
from thefuzz import fuzz
# from thefuzz import process
# from loguru import logger
import os
import os.path
# import sqlite3
import time

from loguru import logger
from rich import print
# from telethon import TelegramClient
from telethon.errors import *

# from system.error.telegram_errors import telegram_phone_number_banned_error
# from system.proxy.checking_proxy import reading_proxy_data_from_the_database, checking_the_proxy_for_work
# from system.setting.setting import reading_device_type
from system.sqlite_working_tools.sqlite_working_tools import DatabaseHandler
# from system.telegram_actions.telegram_actions import account_name
# from system.telegram_actions.telegram_actions import renaming_a_session
# from system.telegram_actions.telegram_actions import writing_names_found_files_to_the_db

user_folder = "user_settings"
accounts_folder = "accounts"


def check_account_for_spam() -> None:
    """Проверка аккаунта на спам через @SpamBot"""
    event: str = "Проверка аккаунтов через SpamBot"  # Событие, которое записываем в базу данных
    app_notifications(notification_text=event)  # Выводим уведомление
    # Открываем базу данных для работы с аккаунтами user_settings/software_database.db
    db_handler = DatabaseHandler()
    records: list = db_handler.open_and_read_data("config")
    for row in records:
        # Подключение к Telegram и вывод имя аккаунта в консоль / терминал
        client, phone = connect_to_telegram_account_and_output_name(row)
        try:
            client.send_message('SpamBot', '/start')  # Находим спам бот, и вводим команду /start
            message_bot = client.get_messages('SpamBot')
            for message in message_bot:
                print(f"[magenta]{phone} {message.message}")

                description_action = "Checking: checking account for SpamBot"
                actions = f"{message.message}"
                # print(f"[magenta][+] {actions}")  # Выводим сообщение от спама бота
                similarity_ratio_ru : int = fuzz.ratio(f"{message.message}",
                                                       "Очень жаль, что Вы с этим столкнулись. К сожалению, "
                                                          "иногда наша антиспам-система излишне сурово реагирует на "
                                                          "некоторые действия. Если Вы считаете, что Ваш аккаунт "
                                                          "ограничен по ошибке, пожалуйста, сообщите об этом нашим "
                                                          "модераторам. Пока действуют ограничения, Вы не сможете "
                                                          "писать тем, кто не сохранил Ваш номер в список контактов, "
                                                          "а также приглашать таких пользователей в группы или каналы. "
                                                          "Если пользователь написал Вам первым, Вы сможете ответить, "
                                                          "несмотря на ограничения.")
                logger.exception(similarity_ratio_ru )

                if similarity_ratio_ru >= 97:

                    print('Аккаунт в бане')
                    # Отключаемся от аккаунта, что бы session файл не был занят другим процессом
                    client.disconnect()
                    record_account_actions(phone, description_action, event, actions)

                    try:
                        os.replace(f"{user_folder}/{accounts_folder}/{row[2]}.session",
                                   f"{user_folder}/{accounts_folder}/banned/{row[2]}.session")
                    except FileNotFoundError:
                        # Если в папке accounts нет папки invalid_account, то создаем папку invalid_account
                        print("В папке accounts нет папки invalid_account, создаем папку banned")
                        # Создаем папку invalid_account в папке accounts
                        os.makedirs("user_settings/accounts/banned")
                        os.replace(f"{user_folder}/{accounts_folder}/{row[2]}.session",
                                   f"{user_folder}/{accounts_folder}/banned/{row[2]}.session")

                similarity_ratio_en: int = fuzz.ratio(f"{message.message}",
                                                      "I’m very sorry that you had to contact me. Unfortunately, "
                                                      "some actions can trigger a harsh response from our anti-spam "
                                                      "systems. If you think your account was limited by mistake, you "
                                                      "can submit a complaint to our moderators. While the account is "
                                                      "limited, you will not be able to send messages to people who "
                                                      "do not have your number in their phone contacts or add them to "
                                                      "groups and channels. Of course, when people contact you first, "
                                                      "you can always reply to them.")
                logger.exception(similarity_ratio_en)

                if similarity_ratio_en >= 97:

                    print('Аккаунт в бане')
                    # Отключаемся от аккаунта, что бы session файл не был занят другим процессом
                    client.disconnect()
                    record_account_actions(phone, description_action, event, actions)

                    try:
                        os.replace(f"{user_folder}/{accounts_folder}/{row[2]}.session",
                                   f"{user_folder}/{accounts_folder}/banned/{row[2]}.session")
                    except FileNotFoundError:
                        # Если в папке accounts нет папки invalid_account, то создаем папку invalid_account
                        print("В папке accounts нет папки invalid_account, создаем папку banned")
                        # Создаем папку invalid_account в папке accounts
                        os.makedirs("user_settings/accounts/banned")
                        os.replace(f"{user_folder}/{accounts_folder}/{row[2]}.session",
                                   f"{user_folder}/{accounts_folder}/banned/{row[2]}.session")

                # client.disconnect()
                # time.sleep(20)
                record_account_actions(phone, description_action, event, actions)
                # client.disconnect()
        except YouBlockedUserError:
            continue  # Записываем ошибку в software_database.db и продолжаем работу


if __name__ == "__main__":
    check_account_for_spam()
