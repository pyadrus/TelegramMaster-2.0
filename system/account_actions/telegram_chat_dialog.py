# -*- coding: utf-8 -*-
import datetime
import random
import time

from loguru import logger
from telethon.errors import ChannelPrivateError, PeerFloodError, FloodWaitError, UserBannedInChannelError, \
    ChatWriteForbiddenError

from system.auxiliary_functions.auxiliary_functions import record_and_interrupt, read_json_file, all_find_files, \
    find_files
from system.auxiliary_functions.global_variables import ConfigReader
from system.sqlite_working_tools.sqlite_working_tools import DatabaseHandler

configs_reader = ConfigReader()
time_sending_messages_1, time_sending_messages_2 = configs_reader.get_time_sending_messages()
time_subscription_1, time_subscription_2 = configs_reader.get_time_subscription()
time_inviting_1, time_inviting_2 = configs_reader.get_time_inviting()


async def connecting_tg_account_creating_list_groups(db_handler):
    """Подключение к аккаунту телеграмм и формирование списка групп"""
    # Открываем базу данных для работы с аккаунтами user_settings/software_database.db
    records: list = await db_handler.open_and_read_data("config")  # Открываем базу данных
    logger.info(f"Всего accounts: {len(records)}")
    for row in records:
        # Подключение к Telegram и вывод имя аккаунта в консоль / терминал
        client = await telegram_connect_and_output_name(row, db_handler)
        records: list = await db_handler.open_and_read_data("writing_group_links")  # Открываем базу данных
        logger.info(f"Всего групп: {len(records)}")

    return client, records


async def sending_files_via_chats(db_handler) -> None:
    """Рассылка файлов по чатам"""
    # Спрашиваем у пользователя, через какое время будем отправлять сообщения
    entities = all_find_files(directory_path="user_settings/files_to_send")
    client, records = await connecting_tg_account_creating_list_groups(db_handler)
    for groups in records:  # Поочередно выводим записанные группы
        await subscribe_to_group_or_channel(client, groups[0])
        try:
            for file in entities:
                await client.send_file(groups[0], f"user_settings/files_to_send/{file}")
                # Работу записываем в лог файл, для удобства слежения, за изменениями
                logger.error(f"""Рассылка сообщений в группу: {groups[0]}. Сообщение в группу {groups[0]} написано!""")
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


async def sending_messages_files_via_chats() -> None:
    """Рассылка сообщений + файлов по чатам"""
    db_handler = DatabaseHandler()  # Открываем базу с аккаунтами и с выставленными лимитами
    client, records = await connecting_tg_account_creating_list_groups(db_handler)
    for groups in records:  # Поочередно выводим записанные группы
        logger.info(f"Всего групп: {len(records)}")
        await subscribe_to_group_or_channel(client, groups[0])
        try:
            entities = find_files(directory_path="user_settings/message", extension="json")
            data = select_and_read_random_file(entities)  # Выбираем случайное сообщение из файла
            entitiess = all_find_files(directory_path="user_settings/files_to_send")
            for file in entitiess:
                file_path = f"user_settings/files_to_send/{file}"
                await client.send_file(groups[0], file_path, caption=data)
                # Работу записываем в лог файл, для удобства слежения, за изменениями
                logger.error(f"""Рассылка сообщений в группу: {groups[0]}. Файл {file} отправлен в группу {groups[0]}.""")
                time.sleep(time_sending_messages_1)
        except ChannelPrivateError:
            logger.error(f"""Рассылка сообщений + файлов в группу: {groups[0]}. Указанный канал / группа  {groups[0]} 
                             является приватным, или вам запретили подписываться.""")
        except PeerFloodError:
            record_and_interrupt(time_subscription_1, time_subscription_2)
            break  # Прерываем работу и меняем аккаунт
        except FloodWaitError as e:
            logger.error(f"""Рассылка сообщений в группу: {groups[0]}. Flood! wait for {str(datetime.timedelta(seconds=e.seconds))}""")
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


def select_and_read_random_file(entities):
    if entities:  # Проверяем, что список не пустой, если он не пустой
        # Выбираем рандомный файл для чтения
        random_file = random.choice(entities)  # Выбираем случайный файл для чтения из списка файлов
        logger.info(f"Выбран файл для чтения: {random_file[0]}.json")
        data = read_json_file(filename=f"user_settings/message/{random_file[0]}.json")
    return data  # Возвращаем данные из файла


async def sending_messages_via_chats_times(entities) -> None:
    """Массовая рассылка в чаты"""
    db_handler = DatabaseHandler()  # Открываем базу с аккаунтами и с выставленными лимитами
    client, records = await connecting_tg_account_creating_list_groups(db_handler)
    for groups in records:  # Поочередно выводим записанные группы
        logger.info(f"Группа: {groups}")
        await subscribe_to_group_or_channel(client, groups[0])
        data = select_and_read_random_file(entities)  # Выбираем случайное сообщение из файла
        try:
            await client.send_message(entity=groups[0], message=data)  # Рассылаем сообщение по чатам
            selected_shift_time = random.randrange(time_sending_messages_1, time_sending_messages_2)
            time_in_seconds = selected_shift_time * 60
            time.sleep(time_in_seconds)  # Спим секунд секунду
            logger.error(f"""Рассылка сообщений в группу: {groups[0]}. Сообщение в группу {groups[0]} написано!""")
        except ChannelPrivateError:
            logger.error(f"""Рассылка сообщений в группу: {groups[0]}. Указанный канал / группа  {groups[0]} является 
                             приватным, или вам запретили подписываться.""")
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
        except (TypeError, UnboundLocalError):
            continue  # Записываем ошибку в software_database.db и продолжаем работу
        except ChatWriteForbiddenError:
            record_and_interrupt(time_subscription_1, time_subscription_2)
            break  # Прерываем работу и меняем аккаунт


if __name__ == "__main__":
    sending_messages_files_via_chats()  # Отправляем сообщения через чаты
