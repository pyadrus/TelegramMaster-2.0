import PySimpleGUI as sg
from loguru import logger
from telethon import functions

from system.sqlite_working_tools.sqlite_working_tools import select_from_config_by_phone
from system.telegram_actions.telegram_actions import telegram_connect_and_output_name


def get_account_list(db_handler):
    records = db_handler.open_and_read_data("config")
    return records


def create_gui(account_list, db_handler) -> None:
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
                    client, phone = telegram_connect_and_output_name(row, db_handler)
                    # Замените «имя пользователя» именем пользователя или идентификатором пользователя, которого вы хотите добавить в группу.
                    result = client(functions.channels.CreateChannelRequest(title='My awesome title',
                                                                            about='Description for your group',
                                                                            megagroup=True))
                    print(result.stringify())
            except Exception as e:
                logger.error(e)

    window.close()


def creating_groups_and_chats(db_handler) -> None:
    """Создание групп (чатов) в автоматическом режиме"""
    accounts = get_account_list(db_handler)
    phones = [rows[0] for rows in accounts]  # Извлечение номеров телефонов (rows[2]) из списка учетных записей
    create_gui(phones, db_handler)  # Передача всего списка учетных записей в create_gui
