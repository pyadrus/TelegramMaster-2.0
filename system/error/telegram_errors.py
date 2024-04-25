import datetime
import os
# import sys
# import time
from loguru import logger
from rich import print
# from telethon.errors import ChatAdminRequiredError, ChannelPrivateError, FloodWaitError

"""Действия с username"""


def record_account_actions(phone_number, action_description, event, action_result, db_handler) -> None:
    """Записывает действия аккаунта в базу данных
    :arg phone_number: номер телефона аккаунта
    :arg action_description: описание действия
    :arg event: действие, которое производится
    :arg action_result: результат выполнения действия.
    :arg db_handler: База данных для записи действий аккаунта в базу данных"""
    logger.error(f"[!] {action_result}")
    date = datetime.datetime.now()  # Получаем текущую дату
    entities = [phone_number, str(date), action_description, event, action_result]  # Формируем словарь
    db_handler.write_data_to_db("""CREATE TABLE IF NOT EXISTS account_actions (phone, date, description_action, event, actions)""", """INSERT INTO  account_actions (phone, date, description_action, event, actions) VALUES (?, ?, ?, ?, ?)""", entities)  # Запись данных в базу данных


"""Действия с аккаунтами"""


def delete_files(file) -> None:
    """Удаление файлов"""
    try:
        os.remove(f"{file}")
    except FileNotFoundError:
        print(f"[red][!] Файл {file} не найден!")


def telegram_phone_number_banned_error_bio(client, phone, db_handler) -> None:
    """Аккаунт banned, удаляем banned аккаунт"""
    client.disconnect()  # Разрываем соединение Telegram, для удаления session файла
    db_handler.delete_row_db(table="config", column="phone", value=phone)
    delete_files(file=f"user_settings/bio_accounts/accounts/{phone}.session")


def telegram_phone_number_banned_error(client, phone, db_handler) -> None:
    """Аккаунт banned, удаляем banned аккаунт"""
    client.disconnect()  # Разрываем соединение Telegram, для удаления session файла
    db_handler.delete_row_db(table="config", column="phone", value=phone)
    delete_files(file=f"user_settings/accounts/{phone}.session")


# def handle_exceptions_pars(func):
#     def wrapper(*args, **kwargs):
#         try:
#             return func(*args, **kwargs)
#         except ChatAdminRequiredError:
#             # Если для parsing нужны права администратора в чате
#             phone, groups_wr = args[2], args[1]
#             event: str = f"Parsing: {groups_wr}"
#             description_action = f"channel / group: {groups_wr}"
#             actions: str = "Требуются права администратора."
#             record_account_actions(phone, description_action, event, actions, db_handler)
#             return  # Прерываем работу и меняем аккаунт
#         except ChannelPrivateError:
#             # Если указанный канал является приватным, или вам запретили подписываться.
#             phone, groups_wr = args[2], args[1]
#             event: str = f"Parsing: {groups_wr}"
#             description_action = f"channel / group: {groups_wr}"
#             actions: str = "Указанный канал является приватным, или вам запретили подписываться."
#             record_account_actions(phone, description_action, event, actions, db_handler)
#             # Удаляем отработанную группу или канал
#             db_handler.delete_row_db(table="writing_group_links", column="writing_group_links", value=groups_wr)
#             return  # Прерываем работу и меняем аккаунт
#         except AttributeError:  # Если произошла ошибка во время parsing
#             print("Парсинг закончен!")
#         except KeyError:  # Если произошла ошибка, связанная с ключом словаря
#             sys.exit(1)
#         except FloodWaitError as e:  # Если возникла ошибка FloodWaitError
#             print(f"Flood! wait for {str(datetime.timedelta(seconds=e.seconds))}")
#             time.sleep(e.seconds)
#
#     return wrapper
