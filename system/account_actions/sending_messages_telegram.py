# -*- coding: utf-8 -*-
import sys
import time

from loguru import logger
from telethon.errors import FloodWaitError, PeerFloodError, UserNotMutualContactError, UserIdInvalidError, \
    UsernameNotOccupiedError, UsernameInvalidError, ChatWriteForbiddenError

from system.account_actions.TGConnect import TGConnect
from system.account_actions.TGLimits import SettingLimits
from system.account_actions.telegram_chat_dialog import select_and_read_random_file
from system.auxiliary_functions.auxiliary_functions import find_files, all_find_files
from system.auxiliary_functions.auxiliary_functions import record_and_interrupt
from system.auxiliary_functions.global_variables import ConfigReader
from system.sqlite_working_tools.sqlite_working_tools import DatabaseHandler


class SendTelegramMessages:
    """Отправка (текстовых) сообщений в личку Telegram пользователям из базы данных."""

    def __init__(self):
        self.db_handler = DatabaseHandler()
        self.tg_connect = TGConnect()
        self.limits_class = SettingLimits()
        self.config_reader = ConfigReader()

    async def connect_to_telegram(self, file):
        """Подключение к Telegram, используя файл session."""
        logger.info(f"{file[0]}")
        proxy = await self.tg_connect.reading_proxies_from_the_database()
        client = await self.tg_connect.connecting_to_telegram(file[0], proxy, "user_settings/accounts/send_message")
        await client.connect()
        return client

    async def send_message_from_all_accounts(self, account_limits) -> None:
        """Отправка (текстовых) сообщений в личку Telegram пользователям из базы данных."""
        time_inviting = self.config_reader.get_time_inviting()
        time_inviting_1 = time_inviting[0]
        time_inviting_2 = time_inviting[1]
        entities = find_files(directory_path="user_settings/accounts/send_message", extension='session')
        for file in entities:
            client = await self.connect_to_telegram(file)  # Подключение к Telegram
            try:
                number_usernames = await self.limits_class.get_usernames_with_limits(table_name="members",
                                                                                     account_limits=account_limits)
                # Количество аккаунтов на данный момент в работе
                logger.info(f"Всего username: {len(number_usernames)}")
                for rows in number_usernames:
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
                        logger.error(
                            f"Отправляем сообщение в личку {username}. {username} не является взаимным контактом.")
                    except (UserIdInvalidError, UsernameNotOccupiedError, ValueError, UsernameInvalidError):
                        logger.error(f"Отправляем сообщение в личку {username}. Не корректное имя {username}.")
                    except ChatWriteForbiddenError:
                        record_and_interrupt(time_inviting_1, time_inviting_2)
                        break  # Прерываем работу и меняем аккаунт
                    except (TypeError, UnboundLocalError):
                        continue  # Записываем ошибку в software_database.db и продолжаем работу
            except KeyError:  # В случае отсутствия ключа в базе данных (нет аккаунтов в базе данных).
                sys.exit(1)

    async def send_files_to_personal_chats(self, account_limits) -> None:
        """Отправка файлов в личку"""
        # Просим пользователя ввести расширение сообщения
        time_inviting = self.config_reader.get_time_inviting()
        time_inviting_1 = time_inviting[0]
        time_inviting_2 = time_inviting[1]
        entitiess = all_find_files(directory_path="user_settings/files_to_send")
        entities = find_files(directory_path="user_settings/accounts/send_message", extension='session')
        for file in entities:
            client = await self.connect_to_telegram(file)  # Подключение к Telegram
            try:
                # Открываем parsing список user_settings/software_database.db для inviting в группу
                number_usernames = await self.limits_class.get_usernames_with_limits(table_name="members",
                                                                                     account_limits=account_limits)
                # Количество аккаунтов на данный момент в работе
                logger.info(f"Всего username: {len(number_usernames)}")
                for rows in number_usernames:
                    username = rows[0]  # Получаем имя аккаунта из базы данных user_settings/software_database.db
                    logger.info(f"[!] Отправляем сообщение: {username}")
                    try:
                        user_to_add = await client.get_input_entity(username)
                        for files in entitiess:
                            await client.send_file(user_to_add, f"user_settings/files_to_send/{files}")
                            logger.info(f"""Отправляем сообщение в личку {username}. Файл {files} отправлен пользователю 
                                             {username}.""")
                    except FloodWaitError as e:
                        record_and_interrupt(time_inviting_1, time_inviting_2)
                        break  # Прерываем работу и меняем аккаунт
                    except PeerFloodError:
                        record_and_interrupt(time_inviting_1, time_inviting_2)
                        break  # Прерываем работу и меняем аккаунт
                    except UserNotMutualContactError:
                        logger.error(
                            f"Отправляем сообщение в личку {username}. {username} не является взаимным контактом.")
                    except (UserIdInvalidError, UsernameNotOccupiedError, ValueError, UsernameInvalidError):
                        logger.error(f"Отправляем сообщение в личку {username}. Не корректное имя {username}.")
                    except ChatWriteForbiddenError:
                        record_and_interrupt(time_inviting_1, time_inviting_2)
                        break  # Прерываем работу и меняем аккаунт
                    except (TypeError, UnboundLocalError):
                        continue  # Записываем ошибку в software_database.db и продолжаем работу
            except KeyError:
                sys.exit(1)
