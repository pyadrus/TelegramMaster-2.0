from telethon.sync import TelegramClient  # Не удалять, так как используется кодом
from system.error.telegram_errors import record_account_actions
from system.notification.notification import app_notifications

from system.telegram_actions.telegram_actions import telegram_connect_and_output_name
from thefuzz import fuzz

import os
import os.path

from loguru import logger
from rich import print
from telethon.errors import *

from system.sqlite_working_tools.sqlite_working_tools import DatabaseHandler


def check_account_for_spam() -> None:
    """Проверка аккаунта на спам через @SpamBot"""
    event: str = "Проверка аккаунтов через SpamBot"  # Событие, которое записываем в базу данных
    app_notifications(notification_text=event)  # Выводим уведомление
    # Открываем базу данных для работы с аккаунтами user_settings/software_database.db
    db_handler = DatabaseHandler()
    records: list = db_handler.open_and_read_data("config")
    for row in records:
        # Подключение к Telegram и вывод имя аккаунта в консоль / терминал
        client, phone = telegram_connect_and_output_name(row)
        try:
            client.send_message('SpamBot', '/start')  # Находим спам бот, и вводим команду /start
            message_bot = client.get_messages('SpamBot')
            for message in message_bot:
                print(f"[magenta]{phone} {message.message}")

                description_action = "Checking: checking account for SpamBot"
                actions = f"{message.message}"

                similarity_ratio_ru: int = fuzz.ratio(f"{message.message}",
                                                      "Очень жаль, что Вы с этим столкнулись. К сожалению, "
                                                      "иногда наша антиспам-система излишне сурово реагирует на "
                                                      "некоторые действия. Если Вы считаете, что Ваш аккаунт "
                                                      "ограничен по ошибке, пожалуйста, сообщите об этом нашим "
                                                      "модераторам. Пока действуют ограничения, Вы не сможете "
                                                      "писать тем, кто не сохранил Ваш номер в список контактов, "
                                                      "а также приглашать таких пользователей в группы или каналы. "
                                                      "Если пользователь написал Вам первым, Вы сможете ответить, "
                                                      "несмотря на ограничения.")
                logger.exception(similarity_ratio_ru)
                if similarity_ratio_ru >= 97:
                    print('Аккаунт в бане')
                    client.disconnect()  # Отключаемся от аккаунта, что бы session файл не был занят другим процессом
                    record_account_actions(phone, description_action, event, actions)
                    # Перенос Telegram аккаунта в папку banned, если Telegram аккаунт в бане
                    working_with_accounts(account_folder=f"user_settings/accounts/{row[2]}.session",
                                          new_account_folder=f"user_settings/accounts/banned/{row[2]}.session")
                similarity_ratio_en: int = fuzz.ratio(f"{message.message}",
                                                      "I’m very sorry that you had to contact me. Unfortunately, "
                                                      "some account_actions can trigger a harsh response from our "
                                                      "anti-spam systems. If you think your account was limited by "
                                                      "mistake, you can submit a complaint to our moderators. While "
                                                      "the account is limited, you will not be able to send messages "
                                                      "to people who do not have your number in their phone contacts "
                                                      "or add them to groups and channels. Of course, when people "
                                                      "contact you first, you can always reply to them.")
                logger.exception(similarity_ratio_en)
                if similarity_ratio_en >= 97:
                    print('Аккаунт в бане')
                    client.disconnect()  # Отключаемся от аккаунта, что бы session файл не был занят другим процессом
                    record_account_actions(phone, description_action, event, actions)
                    working_with_accounts(row)  # Перенос аккаунта в папку бан
                record_account_actions(phone, description_action, event, actions)

        except YouBlockedUserError:
            continue  # Записываем ошибку в software_database.db и продолжаем работу


def working_with_accounts(account_folder, new_account_folder) -> None:
    """Работа с аккаунтами"""
    try:  # Переносим файлы в нужную папку
        os.replace(account_folder, new_account_folder)
    except FileNotFoundError:  # Если в папке нет нужной папки, то создаем ее
        os.makedirs(new_account_folder)
        os.replace(account_folder, new_account_folder)


if __name__ == "__main__":
    check_account_for_spam()
