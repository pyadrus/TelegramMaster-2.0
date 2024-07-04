# -*- coding: utf-8 -*-
import asyncio
import datetime
import random
import sys
import time

from loguru import logger
from telethon import TelegramClient, events
from telethon.errors import ChannelPrivateError, PeerFloodError, FloodWaitError, UserBannedInChannelError, \
    ChatWriteForbiddenError
from telethon.errors import UserNotMutualContactError, UserIdInvalidError, \
    UsernameNotOccupiedError, UsernameInvalidError
from telethon.tl.functions.channels import JoinChannelRequest

from system.account_actions.TGConnect import TGConnect
from system.account_actions.TGLimits import SettingLimits
from system.account_actions.TGSubUnsub import SubscribeUnsubscribeTelegram
from system.auxiliary_functions.auxiliary_functions import find_files, all_find_files
from system.auxiliary_functions.auxiliary_functions import read_json_file
from system.auxiliary_functions.auxiliary_functions import record_and_interrupt
from system.auxiliary_functions.global_variables import ConfigReader
from system.sqlite_working_tools.sqlite_working_tools import DatabaseHandler

configs_reader = ConfigReader()
time_sending_messages_1, time_sending_messages_2 = configs_reader.get_time_sending_messages()
time_subscription_1, time_subscription_2 = configs_reader.get_time_subscription()
time_inviting_1, time_inviting_2 = configs_reader.get_time_inviting()
api_id_data, api_hash_data = configs_reader.get_api_id_data_api_hash_data()
account_name_newsletter = configs_reader.account_name_newsletter()


class SendTelegramMessages:
    """Отправка (текстовых) сообщений в личку Telegram пользователям из базы данных."""

    def __init__(self):
        self.db_handler = DatabaseHandler()
        self.tg_connect = TGConnect()
        self.limits_class = SettingLimits()
        self.config_reader = ConfigReader()
        self.sub_unsub_tg = SubscribeUnsubscribeTelegram()

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
                        data = self.select_and_read_random_file(entities)  # Выбираем случайное сообщение из файла
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

    async def sending_files_via_chats(self) -> None:
        """Рассылка файлов по чатам"""
        # Спрашиваем у пользователя, через какое время будем отправлять сообщения
        entities = all_find_files(directory_path="user_settings/files_to_send")
        client, records = await self.connecting_tg_account_creating_list_groups()
        for groups in records:  # Поочередно выводим записанные группы
            await self.sub_unsub_tg.subscribe_to_group_or_channel(client, groups[0])
            try:
                for file in entities:
                    await client.send_file(groups[0], f"user_settings/files_to_send/{file}")
                    # Работу записываем в лог файл, для удобства слежения, за изменениями
                    logger.error(
                        f"""Рассылка сообщений в группу: {groups[0]}. Сообщение в группу {groups[0]} написано!""")
                    time.sleep(time_sending_messages_1)
            except ChannelPrivateError:
                logger.error(f"""Рассылка сообщений в группу: {groups[0]}. Указанный канал / группа  {groups[0]} является 
                                 приватным, или вам запретили подписываться.""")
            except PeerFloodError:
                record_and_interrupt(time_subscription_1, time_subscription_2)
                break  # Прерываем работу и меняем аккаунт
            except FloodWaitError as e:
                logger.error(
                    f"""Рассылка файлов в группу: {groups[0]}. Flood! wait for {str(datetime.timedelta(seconds=e.seconds))}""")
                time.sleep(e.seconds)
            except UserBannedInChannelError:
                record_and_interrupt(time_subscription_1, time_subscription_2)
                break  # Прерываем работу и меняем аккаунт
            except ChatWriteForbiddenError:
                record_and_interrupt(time_subscription_1, time_subscription_2)
                break  # Прерываем работу и меняем аккаунт
            except (TypeError, UnboundLocalError):
                continue  # Записываем ошибку в software_database.db и продолжаем работу
            client.disconnect()  # Разрываем соединение Telegram

    async def sending_messages_files_via_chats(self) -> None:
        """Рассылка сообщений + файлов по чатам"""

        client, records = await self.connecting_tg_account_creating_list_groups()
        for groups in records:  # Поочередно выводим записанные группы
            logger.info(f"Всего групп: {len(records)}")
            await self.sub_unsub_tg.subscribe_to_group_or_channel(client, groups[0])
            try:
                entities = find_files(directory_path="user_settings/message", extension="json")
                data = self.select_and_read_random_file(entities)  # Выбираем случайное сообщение из файла
                entitiess = all_find_files(directory_path="user_settings/files_to_send")
                for file in entitiess:
                    file_path = f"user_settings/files_to_send/{file}"
                    await client.send_file(groups[0], file_path, caption=data)
                    # Работу записываем в лог файл, для удобства слежения, за изменениями
                    logger.error(
                        f"""Рассылка сообщений в группу: {groups[0]}. Файл {file} отправлен в группу {groups[0]}.""")
                    time.sleep(time_sending_messages_1)
            except ChannelPrivateError:
                logger.error(
                    f"""Рассылка сообщений + файлов в группу: {groups[0]}. Указанный канал / группа  {groups[0]} 
                                 является приватным, или вам запретили подписываться.""")
            except PeerFloodError:
                record_and_interrupt(time_subscription_1, time_subscription_2)
                break  # Прерываем работу и меняем аккаунт
            except FloodWaitError as e:
                logger.error(
                    f"""Рассылка сообщений в группу: {groups[0]}. Flood! wait for {str(datetime.timedelta(seconds=e.seconds))}""")
                time.sleep(e.seconds)
            except UserBannedInChannelError:
                record_and_interrupt(time_subscription_1, time_subscription_2)
                break  # Прерываем работу и меняем аккаунт
            except ChatWriteForbiddenError:
                record_and_interrupt(time_subscription_1, time_subscription_2)
                break  # Прерываем работу и меняем аккаунт
            except (TypeError, UnboundLocalError):
                continue  # Записываем ошибку в software_database.db и продолжаем работу
        await client.disconnect()  # Разрываем соединение Telegram

    async def select_and_read_random_file(self, entities):
        if entities:  # Проверяем, что список не пустой, если он не пустой
            # Выбираем рандомный файл для чтения
            random_file = random.choice(entities)  # Выбираем случайный файл для чтения из списка файлов
            logger.info(f"Выбран файл для чтения: {random_file[0]}.json")
            data = read_json_file(filename=f"user_settings/message/{random_file[0]}.json")
        return data  # Возвращаем данные из файла

    async def sending_messages_via_chats_times(self) -> None:
        """Массовая рассылка в чаты"""
        entities = find_files(directory_path="user_settings/accounts/send_message", extension='session')
        for file in entities:
            client = await self.connect_to_telegram(file)  # Подключение к Telegram
            records: list = await self.db_handler.open_and_read_data("writing_group_links")  # Открываем базу данных
            logger.info(f"Всего групп: {len(records)}")
            for groups in records:  # Поочередно выводим записанные группы
                logger.info(f"Группа: {groups}")
                await self.sub_unsub_tg.subscribe_to_group_or_channel(client, groups[0])
                entitiess = find_files(directory_path="user_settings/message", extension="json")
                data = await self.select_and_read_random_file(entitiess)  # Выбираем случайное сообщение из файла
                try:
                    await client.send_message(entity=groups[0], message=data)  # Рассылаем сообщение по чатам
                    selected_shift_time = random.randrange(time_sending_messages_1, time_sending_messages_2)
                    time_in_seconds = selected_shift_time * 60
                    logger.info(f'Сон {time_in_seconds}')
                    time.sleep(time_in_seconds)  # Спим секунд секунду
                    logger.error(f"""Рассылка сообщений в группу: {groups[0]}. Сообщение в группу {groups[0]} написано!""")
                except ChannelPrivateError:
                    logger.error(f"""Рассылка сообщений в группу: {groups[0]}. Указанный канал / группа  {groups[0]} является 
                                     приватным, или вам запретили подписываться.""")
                except PeerFloodError:
                    record_and_interrupt(time_subscription_1, time_subscription_2)
                    break  # Прерываем работу и меняем аккаунт
                except FloodWaitError as e:
                    logger.error(f"""Рассылка сообщений в группу: {groups[0]}. Flood! wait for {str(datetime.timedelta(seconds=e.seconds))}""")
                    time.sleep(e.seconds)
                except UserBannedInChannelError:
                    record_and_interrupt(time_subscription_1, time_subscription_2)
                    break  # Прерываем работу и меняем аккаунт
                except (TypeError, UnboundLocalError):
                    continue  # Записываем ошибку в software_database.db и продолжаем работу
                except ChatWriteForbiddenError:
                    record_and_interrupt(time_subscription_1, time_subscription_2)
                    break  # Прерываем работу и меняем аккаунт

    def mains(self):
        """Рассылка сообщений в чатам"""
        # Создаем клиент Telegram
        client = TelegramClient(f"user_settings/accounts/{account_name_newsletter}", api_id_data, api_hash_data)

        async def send_messages():
            """Отправляет сообщения в чаты"""
            while True:
                # Получаем список чатов, которым нужно отправить сообщение
                records: list = db_handler.open_and_read_data("writing_group_links")  # Открываем базу данных
                logger.info(records)
                for chat in records:
                    try:
                        entities = find_files(directory_path="user_settings/message",
                                              extension="json")  # Выбираем случайное сообщение из файла
                        logger.info(entities)  # Выводим список чатов
                        data = self.select_and_read_random_file(entities)  # Выбираем случайное сообщение из файла
                        await client.send_message(chat[0], f'{data}')
                        logger.info(f'Сообщение {data} отправлено в чат {chat[0]}')
                    except UserBannedInChannelError:
                        logger.error('Вам запрещено отправлять сообщения в супергруппах/каналах '
                                     '(вызвано запросом SendMessageRequest)')  # Выводим в лог ошибку
                logger.info('Спим 30 сек')

                selected_shift_time = random.randrange(time_sending_messages_1, time_sending_messages_2)
                time_in_seconds = selected_shift_time * 60
                logger.info(f'Спим {time_in_seconds / 60} минуты / минут...')
                await asyncio.sleep(time_in_seconds)  # Спим 1 секунду

        def select_and_read_random_filess(entities):
            if entities:  # Проверяем, что список не пустой, если он не пустой
                # Выбираем рандомный файл для чтения
                random_file = random.choice(entities)  # Выбираем случайный файл для чтения из списка файлов
                logger.info(f"Выбран файл для чтения: {random_file[0]}.json")
                data = read_json_file(filename=f"user_settings/answering_machine/{random_file[0]}.json")
            return data  # Возвращаем данные из файла

        @client.on(events.NewMessage())
        async def handle_private_messages(event):
            """Обрабатывает входящие личные сообщения"""
            if event.is_private:  # Проверяем, является ли сообщение личным
                logger.info(f'Входящее сообщение: {event.message.message}')
                entities = find_files(directory_path="user_settings/answering_machine",
                                      extension="json")  # Получаем список аккаунтов
                logger.info(entities)  # Выводим список чатов
                data = select_and_read_random_filess(entities)
                logger.info(data)
                await event.respond(f'{data}')  # Отвечаем на входящее сообщение

        async def join_chat(chat_link):
            """Присоединяется к чату"""
            await client(JoinChannelRequest(chat_link))

        async def main():
            """Главная функция"""
            await client.connect()  # Запускаем клиент Telegram
            records: list = db_handler.open_and_read_data("writing_group_links")  # Открываем базу данных
            logger.info(records)
            for chat in records:
                logger.info(f'Подписываемся на чат {chat[0]}')  # Выводим в лог имя чата, для проверки, что все работает
                await join_chat(f'{chat[0]}')  # Присоединяемся к чату
            asyncio.ensure_future(send_messages())  # Запускаем асинхронную функцию отправки сообщений по чатам
            await client.run_until_disconnected()

        client.loop.run_until_complete(main())  # Запускаем программу
