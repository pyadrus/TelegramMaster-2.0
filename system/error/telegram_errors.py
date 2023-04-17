# -*- coding: utf-8 -*-
import datetime
import os

from rich import print

from system.sqlite_working_tools.sqlite_working_tools import delete_row_db
from system.sqlite_working_tools.sqlite_working_tools import writing_data_to_the_db

"""Действия с username"""


def recording_actions_in_the_db(phone, description_action, event, actions):
    """Запись действий аккаунта в базу данных"""
    print(f"[red][!] {actions}")
    creating_a_table = "CREATE TABLE IF NOT EXISTS account_actions" \
                       "(phone, date, description_action, event, actions)"
    writing_data_to_a_table = "INSERT INTO  account_actions " \
                              "(phone, date, description_action, event, actions) " \
                              "VALUES (?, ?, ?, ?, ?)"
    date = datetime.datetime.now()
    # phone - номер телефона аккаунта,
    # str(date) - дата и время действия,
    # description_action - данные над которыми производятся действия,
    # event - действия которе производим,
    # actions - результат выполнения действий.
    entities = [phone, str(date), description_action, event, actions]
    writing_data_to_the_db(creating_a_table, writing_data_to_a_table, entities)


"""Действия с аккаунтами"""


def telegram_phone_number_banned_error(client, phone):
    """Аккаунт banned, удаляем banned аккаунт"""
    client.disconnect()  # Разрываем соединение Telegram, для удаления session файла
    delete_row_db(table="config", column="phone", value=phone)
    try:
        os.remove(f"setting_user/accounts/{phone}.session")  # Находим и удаляем сессию
    except FileNotFoundError:
        print(f"[green]Файл {phone}.session был ранее удален")  # Если номер не найден, то выводим сообщение
