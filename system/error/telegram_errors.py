import datetime
import os
import sys
import time

from rich import print
from telethon.errors import ChatAdminRequiredError, ChannelPrivateError, FloodWaitError

from system.sqlite_working_tools.sqlite_working_tools import delete_row_db
from system.sqlite_working_tools.sqlite_working_tools import write_data_to_db

"""Действия с username"""


def record_account_actions(phone_number, action_description, event, action_result) -> None:
    """Записывает действия аккаунта в базу данных
    phone_number - номер телефона аккаунта,
    action_description - описание действия,
    event - действие, которое производится,
    action_result - результат выполнения действия."""
    print(f"[red][!] {action_result}")
    creating_a_table = """CREATE TABLE IF NOT EXISTS account_actions 
                          (phone, date, description_action, event, actions)"""
    writing_data_to_a_table = """INSERT INTO  account_actions 
                                 (phone, date, description_action, event, actions) VALUES (?, ?, ?, ?, ?)"""
    date = datetime.datetime.now()  # Получаем текущую дату
    entities = [phone_number, str(date), action_description, event, action_result]  # Формируем словарь
    write_data_to_db(creating_a_table, writing_data_to_a_table, entities)  # Запись данных в базу данных


"""Действия с аккаунтами"""
def delete_file(file):
    """Удаление файла"""
    try:
        os.remove(f"{file}")
    except FileNotFoundError:
        print(f"[red][!] Файл {file} не найден!")

def telegram_phone_number_banned_error(client, phone):
    """Аккаунт banned, удаляем banned аккаунт"""
    client.disconnect()  # Разрываем соединение Telegram, для удаления session файла
    delete_row_db(table="config", column="phone", value=phone)
    # try:
    #     os.remove(f"setting_user/accounts/{phone}.session")  # Находим и удаляем сессию
    # except FileNotFoundError:
    #     print(f"[green]Файл {phone}.session был ранее удален")  # Если номер не найден, то выводим сообщение
    delete_file(file=f"user_settings/accounts/{phone}.session")

def handle_exceptions_pars(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ChatAdminRequiredError:
            # Если для parsing нужны права администратора в чате
            phone, groups_wr = args[2], args[1]
            event: str = f"Parsing: {groups_wr}"
            description_action = f"channel / group: {groups_wr}"
            actions: str = "Требуются права администратора."
            record_account_actions(phone, description_action, event, actions)
            return  # Прерываем работу и меняем аккаунт
        except ChannelPrivateError:
            # Если указанный канал является приватным, или вам запретили подписываться.
            phone, groups_wr = args[2], args[1]
            event: str = f"Parsing: {groups_wr}"
            description_action = f"channel / group: {groups_wr}"
            actions: str = "Указанный канал является приватным, или вам запретили подписываться."
            record_account_actions(phone, description_action, event, actions)
            # Удаляем отработанную группу или канал
            delete_row_db(table="writing_group_links", column="writing_group_links", value=groups_wr)
            return  # Прерываем работу и меняем аккаунт
        except AttributeError:  # Если произошла ошибка во время parsing
            print("Парсинг закончен!")
        except KeyError:  # Если произошла ошибка, связанная с ключом словаря
            sys.exit(1)
        except FloodWaitError as e:  # Если возникла ошибка FloodWaitError
            print(f'Flood! wait for {str(datetime.timedelta(seconds=e.seconds))}')
            time.sleep(e.seconds)

    return wrapper
