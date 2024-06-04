import sys
import time

from loguru import logger
from telethon.errors import *

from system.account_actions.sending_messages.telegram_chat_dialog import select_and_read_random_file
from system.auxiliary_functions.auxiliary_functions import find_files, all_find_files
from system.auxiliary_functions.auxiliary_functions import record_and_interrupt
from system.auxiliary_functions.global_variables import ConfigReader
from system.sqlite_working_tools.sqlite_working_tools import DatabaseHandler
from system.telegram_actions.telegram_actions import telegram_connect_and_output_name

configs_reader = ConfigReader()
time_inviting_1, time_inviting_2 = configs_reader.get_time_inviting()


async def send_files_to_personal_chats(limits) -> None:
    """Отправка файлов в личку"""
    # Просим пользователя ввести расширение сообщения
    entities = all_find_files(directory_path="user_settings/files_to_send")
    # Открываем базу данных для работы с аккаунтами user_settings/software_database.db
    db_handler = DatabaseHandler()
    records: list = await db_handler.open_and_read_data("config")
    for row in records:
        # Подключение к Telegram и вывод имя аккаунта в консоль / терминал
        client = await telegram_connect_and_output_name(row, db_handler)
        try:
            # Открываем parsing список user_settings/software_database.db для inviting в группу
            records: list = await db_handler.open_the_db_and_read_the_data_lim("members",
                                                                               number_of_accounts=limits)
            # Количество аккаунтов на данный момент в работе
            logger.info(f"Всего username: {len(records)}")
            for rows in records:
                username = rows[0]  # Получаем имя аккаунта из базы данных user_settings/software_database.db
                logger.info(f"[!] Отправляем сообщение: {username}")
                try:
                    user_to_add = await client.get_input_entity(username)
                    for file in entities:
                        await client.send_file(user_to_add, f"user_settings/files_to_send/{file}")
                        logger.info(f"""Отправляем сообщение в личку {username}. Файл {file} отправлен пользователю 
                                         {username}.""")
                except FloodWaitError as e:
                    record_and_interrupt(time_inviting_1, time_inviting_2)
                    break  # Прерываем работу и меняем аккаунт
                except PeerFloodError:
                    record_and_interrupt(time_inviting_1, time_inviting_2)
                    break  # Прерываем работу и меняем аккаунт
                except UserNotMutualContactError:
                    logger.error(f"Отправляем сообщение в личку {username}. {username} не является взаимным контактом.")
                except (UserIdInvalidError, UsernameNotOccupiedError, ValueError, UsernameInvalidError):
                    logger.error(f"Отправляем сообщение в личку {username}. Не корректное имя {username}.")
                except ChatWriteForbiddenError:
                    record_and_interrupt(time_inviting_1, time_inviting_2)
                    break  # Прерываем работу и меняем аккаунт
                except (TypeError, UnboundLocalError):
                    continue  # Записываем ошибку в software_database.db и продолжаем работу
        except KeyError:
            sys.exit(1)


async def send_message_from_all_accounts(limits) -> None:
    """
    Отправка (текстовых) сообщений в личку Telegram пользователям из базы данных.
    :arg limits: (int) количество аккаунтов, которые в данный момент находятся в работе.
    """
    # Открываем базу данных для работы с аккаунтами user_settings/software_database.db
    db_handler = DatabaseHandler()
    records: list = await db_handler.open_and_read_data("config")
    for row in records:
        # Подключение к Telegram и вывод имя аккаунта в консоль / терминал
        client = await telegram_connect_and_output_name(row, db_handler)
        try:
            records: list = await db_handler.open_the_db_and_read_the_data_lim("members",
                                                                               number_of_accounts=limits)
            # Количество аккаунтов на данный момент в работе
            logger.info(f"Всего username: {len(records)}")
            for rows in records:
                username = rows[0]  # Имя аккаунта пользователя в базе данных user_settings/software_database.db
                logger.info(f"[!] Отправляем сообщение: {username}")
                try:
                    user_to_add = await client.get_input_entity(username)
                    entities = find_files(directory_path="user_settings/message", extension="json")
                    logger.info(entities)
                    data = select_and_read_random_file(entities)  # Выбираем случайное сообщение из файла
                    await client.send_message(user_to_add, data.format(username))
                    # Записываем данные в log файл, чистим список кого добавляли или писали сообщение
                    logger.error(f"""Отправляем сообщение в личку {username}. Сообщение отправлено 
                                     пользователю {username}.""")
                    time.sleep(time_inviting_1)
                except FloodWaitError as e:
                    record_and_interrupt(time_inviting_1, time_inviting_2)
                    break  # Прерываем работу и меняем аккаунт
                except PeerFloodError:
                    record_and_interrupt(time_inviting_1, time_inviting_2)
                    break  # Прерываем работу и меняем аккаунт
                except UserNotMutualContactError:
                    logger.error(f"Отправляем сообщение в личку {username}. {username} не является взаимным контактом.")
                except (UserIdInvalidError, UsernameNotOccupiedError, ValueError, UsernameInvalidError):
                    logger.error(f"Отправляем сообщение в личку {username}. Не корректное имя {username}.")
                except ChatWriteForbiddenError:
                    record_and_interrupt(time_inviting_1, time_inviting_2)
                    break  # Прерываем работу и меняем аккаунт
                except (TypeError, UnboundLocalError):
                    continue  # Записываем ошибку в software_database.db и продолжаем работу
        except KeyError:  # В случае отсутствия ключа в базе данных (нет аккаунтов в базе данных).
            sys.exit(1)
