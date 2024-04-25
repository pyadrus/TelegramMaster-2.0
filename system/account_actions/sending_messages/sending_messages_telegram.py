import datetime
import sys
import time

from loguru import logger
from rich import print
from telethon.errors import *

from system.account_actions.sending_messages.telegram_chat_dialog import select_and_read_random_file
from system.auxiliary_functions.auxiliary_functions import record_and_interrupt, record_inviting_results, \
    find_files
from system.auxiliary_functions.global_variables import console, time_inviting_1
from system.notification.notification import app_notifications
from system.telegram_actions.telegram_actions import telegram_connect_and_output_name


def send_files_to_personal_chats(limits, db_handler) -> None:
    """Отправка файлов в личку"""
    # Просим пользователя ввести расширение сообщения
    link_to_the_file: str = console.input(
        "[medium_purple3][+] Введите название файла с папки user_settings/files_to_send: ")
    app_notifications(notification_text="Отправляем сообщение")  # Выводим уведомление
    # Открываем базу данных для работы с аккаунтами user_settings/software_database.db
    records: list = db_handler.open_and_read_data("config")
    for row in records:
        # Подключение к Telegram и вывод имя аккаунта в консоль / терминал
        client, phone = telegram_connect_and_output_name(row, db_handler)
        try:
            # Открываем parsing список user_settings/software_database.db для inviting в группу
            records: list = db_handler.open_the_db_and_read_the_data_lim("members", number_of_accounts=limits)
            # Количество аккаунтов на данный момент в работе
            print(f"[medium_purple3]Всего username: {len(records)}")
            for rows in records:
                username = rows[0]  # Получаем имя аккаунта из базы данных user_settings/software_database.db
                logger.info(f"[!] Отправляем сообщение: {username}")
                try:
                    user_to_add = client.get_input_entity(username)
                    client.send_file(user_to_add, f"user_settings/files_to_send/{link_to_the_file}")
                    # Записываем данные в базу данных, чистим список кого добавляли или писали сообщение
                    record_inviting_results(username, phone, f"username : {username}", "Отправляем сообщение", "Сообщение отправлено", db_handler)
                except FloodWaitError as e:
                    record_and_interrupt(f'Flood! wait for {str(datetime.timedelta(seconds=e.seconds))}', phone, f"username : {username}", "Отправляем сообщение", db_handler)
                    break  # Прерываем работу и меняем аккаунт
                except PeerFloodError:
                    record_and_interrupt("Предупреждение о Flood от telegram.", phone, f"username : {username}", "Отправляем сообщение", db_handler)
                    break  # Прерываем работу и меняем аккаунт
                except UserNotMutualContactError:
                    record_inviting_results(username, phone, f"username : {username}", "Отправляем сообщение",  "User не является взаимным контактом.", db_handler)
                except (UserIdInvalidError, UsernameNotOccupiedError, ValueError, UsernameInvalidError):
                    record_inviting_results(username, phone, f"username : {username}", "Отправляем сообщение", "Не корректное имя user", db_handler)
                except ChatWriteForbiddenError:
                    record_and_interrupt("Вам запрещено писать в супергруппу / канал.", phone, f"username : {username}", "Отправляем сообщение", db_handler)
                    break  # Прерываем работу и меняем аккаунт
                except (TypeError, UnboundLocalError):
                    continue  # Записываем ошибку в software_database.db и продолжаем работу
        except KeyError:
            sys.exit(1)
    app_notifications(notification_text="Работа окончена!")  # Выводим уведомление


def send_message_from_all_accounts(limits, db_handler) -> None:
    """
    Отправка (текстовых) сообщений в личку Telegram пользователям из базы данных.
    :arg limits: (int) количество аккаунтов, которые в данный момент находятся в работе.
    :arg db_handler: (db_handler) объект, который используется для работы с базой данных.
    """
    app_notifications(notification_text="Отправляем сообщение в личку пользователям Telegram")  # Выводим уведомление
    # Открываем базу данных для работы с аккаунтами user_settings/software_database.db
    records: list = db_handler.open_and_read_data("config")
    for row in records:
        # Подключение к Telegram и вывод имя аккаунта в консоль / терминал
        client, phone = telegram_connect_and_output_name(row, db_handler)
        try:
            records: list = db_handler.open_the_db_and_read_the_data_lim("members", number_of_accounts=limits)
            # Количество аккаунтов на данный момент в работе
            print(f"[medium_purple3]Всего username: {len(records)}")
            for rows in records:
                username = rows[0]  # Имя аккаунта пользователя в базе данных user_settings/software_database.db
                print(f"[magenta][!] Отправляем сообщение: {username}")
                try:
                    user_to_add = client.get_input_entity(username)
                    entities = find_files(directory_path="user_settings/message", extension="json")
                    logger.info(entities)
                    data = select_and_read_random_file(entities)  # Выбираем случайное сообщение из файла
                    client.send_message(user_to_add, data.format(username))
                    # Записываем данные в log файл, чистим список кого добавляли или писали сообщение
                    time.sleep(time_inviting_1)
                    record_inviting_results(username, phone, f"username : {username}",
                                            "Отправляем сообщение в личку пользователям Telegram", "Сообщение отправлено", db_handler)
                except FloodWaitError as e:
                    record_and_interrupt(f'Flood! wait for {str(datetime.timedelta(seconds=e.seconds))}', phone,
                                         f"username : {username}", "Отправляем сообщение в личку пользователям Telegram", db_handler)
                    break  # Прерываем работу и меняем аккаунт
                except PeerFloodError:
                    record_and_interrupt("Предупреждение о Flood от telegram.",
                                         phone, f"username : {username}", "Отправляем сообщение в личку пользователям Telegram", db_handler)
                    break  # Прерываем работу и меняем аккаунт
                except UserNotMutualContactError:
                    record_inviting_results(username, phone, f"username : {username}",
                                            "Отправляем сообщение в личку пользователям Telegram", "User не является взаимным контактом.", db_handler)
                except (UserIdInvalidError, UsernameNotOccupiedError, ValueError, UsernameInvalidError):
                    record_inviting_results(username, phone, f"username : {username}",
                                            "Отправляем сообщение в личку пользователям Telegram", "Не корректное имя user", db_handler)
                except ChatWriteForbiddenError:
                    record_and_interrupt("Вам запрещено писать в супергруппу / канал.",
                                         phone, f"username : {username}", "Отправляем сообщение в личку пользователям Telegram", db_handler)
                    break  # Прерываем работу и меняем аккаунт
                except (TypeError, UnboundLocalError):
                    continue  # Записываем ошибку в software_database.db и продолжаем работу
        except KeyError:  # В случае отсутствия ключа в базе данных (нет аккаунтов в базе данных).
            sys.exit(1)
    app_notifications(notification_text="Работа окончена!")  # Выводим уведомление
