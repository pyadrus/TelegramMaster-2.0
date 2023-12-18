import sqlite3

from telethon import functions
from loguru import logger
from system.sqlite_working_tools.sqlite_working_tools import DatabaseHandler
from system.telegram_actions.telegram_actions import connect_to_telegram_account_and_output_name
import PySimpleGUI as sg


def get_account_list():
    db_handler = DatabaseHandler()
    records = db_handler.open_and_read_data("config")
    return records


def select_from_config_by_phone(phone_value):
    # Подключение к базе данных
    conn = sqlite3.connect("user_settings/software_database.db")
    cursor = conn.cursor()
    # Выбор данных из таблицы config по заданному номеру телефона
    cursor.execute('''SELECT id, hash, phone FROM config WHERE phone = ?''', (phone_value,))
    result = cursor.fetchall()  # Получение результатов запроса
    conn.close()  # Закрытие соединения
    return result


def create_gui(account_list):
    layout = [
        [sg.Text("Выберите Telegram аккаунт в котором будут создаваться группы (чаты):")],
        *[[sg.Checkbox(account, key=account)] for account in account_list],
        [sg.Button("Готово", key="Готово")]]
    window = sg.Window("Telegram_SMM_BOT", layout, finalize=True)
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break
        elif event == "Готово":
            selected_phone = [phone for phone, selected in values.items() if selected][0]
            logger.info(selected_phone)
            window.close()
            result = select_from_config_by_phone(selected_phone)
            logger.info(result)
            try:
                for row in result:
                    # Подключение к Telegram и вывод имя аккаунта в консоль / терминал
                    client, phone = connect_to_telegram_account_and_output_name(row)
                    # Replace 'username' with the username or user ID of the user you want to add to the group
                    result = client(functions.channels.CreateChannelRequest(title='My awesome title',
                                                                            about='Description for your group',
                                                                            megagroup=True))
                    print(result.stringify())
            except Exception as e:
                logger.error(e)

    window.close()


def get_from(row):
    """Получаем со списка phone, api_id, api_hash"""
    users = {"id": int(row[0]), "hash": row[1], "phone": row[2]}
    # Вытягиваем данные из кортежа, для подстановки в функцию
    phone = users["phone"]
    return phone


def creating_groups_and_chats():
    """Создание групп (чатов) в автоматическом режиме"""
    accounts = get_account_list()
    # Extracting phone numbers from the accounts list
    phones = [get_from(rows) for rows in accounts]
    # Passing the entire accounts list to create_gui
    create_gui(phones)


if __name__ == "__main__":
    creating_groups_and_chats()
