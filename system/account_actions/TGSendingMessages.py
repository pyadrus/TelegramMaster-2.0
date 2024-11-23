# -*- coding: utf-8 -*-
import asyncio
import datetime
import random
import sys

from loguru import logger
from telethon import events
from telethon.errors import (ChannelPrivateError, PeerFloodError, FloodWaitError, UserBannedInChannelError,
                             ChatWriteForbiddenError, UserNotMutualContactError, UserIdInvalidError,
                             UsernameNotOccupiedError, UsernameInvalidError)
from telethon.tl.functions.channels import JoinChannelRequest

from system.account_actions.TGConnect import TGConnect
from system.account_actions.TGLimits import SettingLimits
from system.account_actions.TGSubUnsub import SubscribeUnsubscribeTelegram
from system.auxiliary_functions.auxiliary_functions import (find_files, all_find_files, record_inviting_results,
                                                            find_filess)
from system.auxiliary_functions.auxiliary_functions import read_json_file
from system.auxiliary_functions.auxiliary_functions import record_and_interrupt
from system.auxiliary_functions.config import ConfigReader, path_send_message_folder
from system.sqlite_working_tools.sqlite_working_tools import DatabaseHandler

time_sending_messages_1, time_sending_messages_2 = ConfigReader().get_time_sending_messages()
time_subscription_1, time_subscription_2 = ConfigReader().get_time_subscription()


class SendTelegramMessages:
    """
    Отправка (текстовых) сообщений в личку Telegram пользователям из базы данных.
    """

    def __init__(self):
        self.db_handler = DatabaseHandler()
        self.tg_connect = TGConnect()
        self.limits_class = SettingLimits()
        self.config_reader = ConfigReader()
        self.sub_unsub_tg = SubscribeUnsubscribeTelegram()

    async def send_message_from_all_accounts(self, account_limits) -> None:
        """
        Отправка (текстовых) сообщений в личку Telegram пользователям из базы данных.

        Аргументы:
        :param account_limits: Лимит на аккаунты
        """
        try:
            time_inviting = self.config_reader.get_time_inviting()
            for session_name in find_filess(directory_path=path_send_message_folder, extension='session'):
                client = await self.tg_connect.get_telegram_client(session_name,
                                                                   account_directory=path_send_message_folder)
                try:
                    for username in await self.limits_class.get_usernames_with_limits(table_name="members",
                                                                                      account_limits=account_limits):
                        # username - имя аккаунта пользователя в базе данных user_settings/software_database.db
                        logger.info(f"[!] Отправляем сообщение: {username[0]}")
                        try:
                            entities = find_files(directory_path="user_settings/message", extension="json")
                            logger.info(entities)
                            data = await self.select_and_read_random_file(entities, folder="message")
                            await client.send_message(await client.get_input_entity(username[0]),
                                                      data.format(username[0]))
                            # Записываем данные в log файл, чистим список кого добавляли или писали сообщение
                            logger.info(
                                f"Отправляем сообщение в личку {username[0]}. Сообщение отправлено пользователю {username[0]}.")
                            await record_inviting_results(time_inviting[0], time_inviting[1], username)
                        except FloodWaitError as e:
                            await record_and_interrupt(time_inviting[0], time_inviting[1])
                            break  # Прерываем работу и меняем аккаунт
                        except PeerFloodError:
                            await record_and_interrupt(time_inviting[0], time_inviting[1])
                            break  # Прерываем работу и меняем аккаунт
                        except UserNotMutualContactError:
                            logger.error(
                                f"❌ Отправляем сообщение в личку {username[0]}. {username[0]} не является взаимным контактом.")
                        except (UserIdInvalidError, UsernameNotOccupiedError, ValueError, UsernameInvalidError):
                            logger.error(
                                f"❌ Отправляем сообщение в личку {username[0]}. Не корректное имя {username[0]}.")
                        except ChatWriteForbiddenError:
                            await record_and_interrupt(time_inviting[0], time_inviting[1])
                            break  # Прерываем работу и меняем аккаунт
                        except (TypeError, UnboundLocalError):
                            continue  # Записываем ошибку в software_database.db и продолжаем работу
                except KeyError:  # В случае отсутствия ключа в базе данных (нет аккаунтов в базе данных).
                    sys.exit(1)

        except Exception as error:
            logger.exception(f"❌ Ошибка: {error}")  # Логируем возникшее исключение вместе с сообщением об ошибке.

    async def send_files_to_personal_chats(self, account_limits) -> None:
        """
        Отправка файлов в личку

        Аргументы:
        :param account_limits: Лимит на аккаунты
        """
        try:
            # Просим пользователя ввести расширение сообщения
            time_inviting = self.config_reader.get_time_inviting()
            for session_name in find_filess(directory_path=path_send_message_folder, extension='session'):
                client = await self.tg_connect.get_telegram_client(session_name,
                                                                   account_directory=path_send_message_folder)
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
                            for files in all_find_files(directory_path="user_settings/files_to_send"):
                                await client.send_file(user_to_add, f"user_settings/files_to_send/{files}")
                                logger.info(
                                    f"Отправляем сообщение в личку {username}. Файл {files} отправлен пользователю {username}.")
                                await record_inviting_results(time_inviting[0], time_inviting[1], username)
                        except FloodWaitError as e:
                            await record_and_interrupt(time_inviting[0], time_inviting[1])
                            break  # Прерываем работу и меняем аккаунт
                        except PeerFloodError:
                            await record_and_interrupt(time_inviting[0], time_inviting[1])
                            break  # Прерываем работу и меняем аккаунт
                        except UserNotMutualContactError:
                            logger.error(
                                f"❌ Отправляем сообщение в личку {username}. {username} не является взаимным контактом.")
                        except (UserIdInvalidError, UsernameNotOccupiedError, ValueError, UsernameInvalidError):
                            logger.error(f"❌ Отправляем сообщение в личку {username}. Не корректное имя {username}.")
                        except ChatWriteForbiddenError:
                            await record_and_interrupt(time_inviting[0], time_inviting[1])
                            break  # Прерываем работу и меняем аккаунт
                        except (TypeError, UnboundLocalError):
                            continue  # Записываем ошибку в software_database.db и продолжаем работу
                except KeyError:
                    sys.exit(1)
        except Exception as error:
            logger.exception(f"❌ Ошибка: {error}")  # Логируем возникшее исключение вместе с сообщением об ошибке.

    async def sending_files_via_chats(self) -> None:
        """
        Рассылка файлов по чатам (docs/Рассылка_сообщений/⛔️ Рассылка_файлов_по_чатам.html)
        """
        try:
            # Спрашиваем у пользователя, через какое время будем отправлять сообщения
            for session_name in find_filess(directory_path=path_send_message_folder, extension='session'):
                client = await self.tg_connect.get_telegram_client(session_name,
                                                                   account_directory=path_send_message_folder)
                records: list = await self.db_handler.open_and_read_data("writing_group_links")  # Открываем базу данных
                logger.info(f"Всего групп: {len(records)}")
                for groups in records:  # Поочередно выводим записанные группы
                    await self.sub_unsub_tg.subscribe_to_group_or_channel(client, groups[0])
                    try:
                        for file in all_find_files(directory_path="user_settings/files_to_send"):
                            await client.send_file(groups[0], f"user_settings/files_to_send/{file}")
                            # Работу записываем в лог файл, для удобства слежения, за изменениями
                            logger.error(
                                f"Рассылка сообщений в группу: {groups[0]}. Сообщение в группу {groups[0]} написано!")
                            await self.random_dream()  # Прерываем работу и меняем аккаунт
                    except ChannelPrivateError:
                        logger.error(
                            f"❌ Рассылка сообщений в группу: {groups[0]}. Указанный канал / группа  {groups[0]} является приватным, или вам запретили подписываться.")
                    except PeerFloodError:
                        await record_and_interrupt(time_subscription_1, time_subscription_2)
                        break  # Прерываем работу и меняем аккаунт
                    except FloodWaitError as e:
                        logger.error(
                            f"❌ Рассылка файлов в группу: {groups[0]}. Flood! wait for {str(datetime.timedelta(seconds=e.seconds))}")
                        await asyncio.sleep(e.seconds)
                    except UserBannedInChannelError:
                        await record_and_interrupt(time_subscription_1, time_subscription_2)
                        break  # Прерываем работу и меняем аккаунт
                    except ChatWriteForbiddenError:
                        await record_and_interrupt(time_subscription_1, time_subscription_2)
                        break  # Прерываем работу и меняем аккаунт
                    except (TypeError, UnboundLocalError):
                        continue  # Записываем ошибку в software_database.db и продолжаем работу
                    client.disconnect()  # Разрываем соединение Telegram
        except Exception as error:
            logger.exception(f"❌ Ошибка: {error}")  # Логируем возникшее исключение вместе с сообщением об ошибке.

    async def sending_messages_files_via_chats(self) -> None:
        """
        Рассылка сообщений + файлов по чатам
        """
        try:
            for session_name in find_filess(directory_path=path_send_message_folder, extension='session'):
                client = await self.tg_connect.get_telegram_client(session_name,
                                                                   account_directory=path_send_message_folder)
                records: list = await self.db_handler.open_and_read_data("writing_group_links")  # Открываем базу данных
                logger.info(f"Всего групп: {len(records)}")
                for groups in records:  # Поочередно выводим записанные группы
                    await self.sub_unsub_tg.subscribe_to_group_or_channel(client, groups[0])
                    entities = find_files(directory_path="user_settings/message", extension="json")
                    data = await self.select_and_read_random_file(entities, folder="message")
                    file_entities = all_find_files(directory_path="user_settings/files_to_send")
                    try:
                        for file in file_entities:
                            await client.send_file(groups[0], f"user_settings/files_to_send/{file}", caption=data)
                            # Работу записываем в лог файл, для удобства слежения, за изменениями
                            logger.error(
                                f"Рассылка сообщений в группу: {groups[0]}. Файл {file} отправлен в группу {groups[0]}.")
                            await self.random_dream()  # Прерываем работу и меняем аккаунт
                    except ChannelPrivateError:
                        logger.error(
                            f"Рассылка сообщений + файлов в группу: {groups[0]}. Указанный канал / группа {groups[0]} является приватным, или вам запретили подписываться.")
                    except PeerFloodError:
                        await record_and_interrupt(time_subscription_1, time_subscription_2)
                        break  # Прерываем работу и меняем аккаунт
                    except FloodWaitError as e:
                        logger.error(
                            f"Рассылка сообщений в группу: {groups[0]}. Flood! wait for {str(datetime.timedelta(seconds=e.seconds))}")
                        await asyncio.sleep(e.seconds)
                    except UserBannedInChannelError:
                        await record_and_interrupt(time_subscription_1, time_subscription_2)
                        break  # Прерываем работу и меняем аккаунт
                    except ChatWriteForbiddenError:
                        await record_and_interrupt(time_subscription_1, time_subscription_2)
                        break  # Прерываем работу и меняем аккаунт
                    except (TypeError, UnboundLocalError):
                        continue  # Записываем ошибку в software_database.db и продолжаем работу
                await client.disconnect()  # Разрываем соединение Telegram
        except Exception as error:
            logger.exception(f"❌ Ошибка: {error}")  # Логируем возникшее исключение вместе с сообщением об ошибке.

    @staticmethod
    async def select_and_read_random_file(entities, folder):
        """
        Выбираем рандомный файл для чтения

        Аргументы:
        :param entities: список файлов для чтения
        :param folder: папка для сохранения файлов
        """
        try:
            if entities:  # Проверяем, что список не пустой, если он не пустой
                # Выбираем рандомный файл для чтения
                random_file = random.choice(entities)  # Выбираем случайный файл для чтения из списка файлов
                logger.info(f"Выбран файл для чтения: {random_file[0]}.json")
                data = read_json_file(filename=f"user_settings/{folder}/{random_file[0]}.json")
            return data  # Возвращаем данные из файла
        except Exception as error:
            logger.exception(f"❌ Ошибка: {error}")  # Логируем возникшее исключение вместе с сообщением об ошибке.

    async def sending_messages_via_chats_times(self) -> None:
        """
        Массовая рассылка в чаты (docs/Рассылка_сообщений/⛔️ Рассылка_сообщений_по_чатам.html)
        """
        try:
            for session_name in find_filess(directory_path=path_send_message_folder, extension='session'):
                client = await self.tg_connect.get_telegram_client(session_name,
                                                                   account_directory=path_send_message_folder)
                records: list = await self.db_handler.open_and_read_data("writing_group_links")  # Открываем базу данных
                logger.info(f"Всего групп: {len(records)}")
                for groups in records:  # Поочередно выводим записанные группы
                    await self.sub_unsub_tg.subscribe_to_group_or_channel(client, groups[0])
                    data = await self.select_and_read_random_file(
                        find_files(directory_path="user_settings/message", extension="json"), folder="message")
                    try:
                        await client.send_message(entity=groups[0], message=data)  # Рассылаем сообщение по чатам
                        await self.random_dream()  # Прерываем работу и меняем аккаунт
                        logger.error(
                            f"Рассылка сообщений в группу: {groups[0]}. Сообщение в группу {groups[0]} написано!")
                    except ChannelPrivateError:
                        logger.error(
                            f"Рассылка сообщений в группу: {groups[0]}. Указанный канал / группа  {groups[0]} является приватным, или вам запретили подписываться.")
                    except PeerFloodError:
                        await record_and_interrupt(time_subscription_1, time_subscription_2)
                        break  # Прерываем работу и меняем аккаунт
                    except FloodWaitError as e:
                        logger.error(
                            f"Рассылка сообщений в группу: {groups[0]}. Flood! wait for {str(datetime.timedelta(seconds=e.seconds))}")
                        await asyncio.sleep(e.seconds)
                    except UserBannedInChannelError:
                        await record_and_interrupt(time_subscription_1, time_subscription_2)
                        break  # Прерываем работу и меняем аккаунт
                    except (TypeError, UnboundLocalError):
                        continue  # Записываем ошибку в software_database.db и продолжаем работу
                    except ChatWriteForbiddenError:
                        await record_and_interrupt(time_subscription_1, time_subscription_2)
                        break  # Прерываем работу и меняем аккаунт

        except Exception as error:
            logger.exception(f"❌ Ошибка: {error}")  # Логируем возникшее исключение вместе с сообщением об ошибке.

    @staticmethod
    async def random_dream():
        """
        Рандомный сон
        """
        try:
            time_in_seconds = random.randrange(time_sending_messages_1, time_sending_messages_2) * 60
            logger.info(f'Спим {time_in_seconds / 60} минуты / минут...')
            await asyncio.sleep(time_in_seconds)  # Спим 1 секунду
        except Exception as error:
            logger.exception(f"❌ Ошибка: {error}")  # Логируем возникшее исключение вместе с сообщением об ошибке.

    async def answering_machine(self):
        """
        Рассылка сообщений по чатам (docs/Рассылка_сообщений/Рассылка_сообщений_по_чатам_с_автоответчиком.md)
        """
        try:
            for session_name in find_filess(directory_path="user_settings/accounts/answering_machine",
                                            extension='session'):
                client = await self.tg_connect.get_telegram_client(session_name,
                                                                   account_directory="user_settings/accounts/answering_machine")

                @client.on(events.NewMessage(incoming=True))  # Обработчик личных сообщений
                async def handle_private_messages(event):
                    """Обрабатывает входящие личные сообщения"""
                    if event.is_private:  # Проверяем, является ли сообщение личным
                        logger.info(f'Входящее сообщение: {event.message.message}')
                        entities = find_files(directory_path="user_settings/answering_machine", extension="json")
                        logger.info(entities)
                        data = await self.select_and_read_random_file(entities, folder="answering_machine")
                        logger.info(data)
                        await event.respond(f'{data}')  # Отвечаем на входящее сообщение

                # Получаем список чатов, которым нужно отправить сообщение
                records: list = await self.db_handler.open_and_read_data("writing_group_links")
                logger.info(records)
                for chat in records:
                    try:
                        await client(JoinChannelRequest(chat[0]))  # Подписываемся на канал / группу
                        entities = find_files(directory_path="user_settings/message", extension="json")
                        logger.info(entities)
                        data = await self.select_and_read_random_file(entities, folder="message")
                        await client.send_message(chat[0], f'{data}')
                        logger.info(f'Сообщение {data} отправлено в чат {chat[0]}')
                    except UserBannedInChannelError:
                        logger.error(
                            'Вам запрещено отправлять сообщения в супергруппах/каналах (вызвано запросом SendMessageRequest)')
                    await self.random_dream()  # Прерываем работу и меняем аккаунт

                await client.run_until_disconnected()  # Запускаем программу и ждем отключения клиента

        except Exception as error:
            logger.exception(f"❌ Ошибка: {error}")  # Логируем возникшее исключение вместе с сообщением об ошибке.
