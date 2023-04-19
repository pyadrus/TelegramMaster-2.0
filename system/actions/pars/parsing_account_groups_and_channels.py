from telethon import functions
from system.error.telegram_errors import recording_actions_in_the_db
from system.notification.notification import app_notifications
from system.sqlite_working_tools.sqlite_working_tools import delete_duplicates
from system.sqlite_working_tools.sqlite_working_tools import open_the_db_and_read_the_data
from system.sqlite_working_tools.sqlite_working_tools import writing_data_to_the_db
from telethon.tl.functions.channels import GetFullChannelRequest  # Не удалять
from system.telegram_actions.telegram_actions import connect_to_telegram_account_and_output_name
import time
import sqlite3

creating_a_table = "CREATE TABLE IF NOT EXISTS groups_and_channels(id, title, about, link, members_count, parsing_time)"
writing_data_to_a_table = "INSERT INTO groups_and_channels (id, title, about, link, members_count, parsing_time) VALUES (?, ?, ?, ?, ?, ?)"


def parsing_of_groups_to_which_the_account_is_subscribed() -> None:
    """Parsing групп / каналов на которые подписан аккаунт и сохраняем в файл software_database.db"""
    add_columns_to_table()
    event: str = "Parsing групп / каналов на которые подписан аккаунт"  # Событие, которое записываем в базу данных
    # Выводим уведомление, если операционная система windows 7, то выводим уведомление в консоль
    app_notifications(notification_text=event)
    # Открываем базу данных для работы с аккаунтами setting_user/software_database.db
    records: list = open_the_db_and_read_the_data(name_database_table="config")
    for row in records:
        # Подключение к Telegram и вывод имя аккаунта в консоль / терминал
        client, phone = connect_to_telegram_account_and_output_name(row)
        description_action = "Parsing: groups and channels"
        actions = "Parsing групп / каналов"
        recording_actions_in_the_db(phone, description_action, event, actions)
        forming_a_list_of_groups(client)
        client.disconnect()  # Разрываем соединение telegram
    # Чистка дубликатов в базе данных
    delete_duplicates(table_name="groups_and_channels", column_name="id")


def forming_a_list_of_groups(client):
    """Формируем список групп"""
    for dialog in client.iter_dialogs():
        try:
            dialog_id = dialog.id
            ch = client.get_entity(dialog_id)
            result = client(functions.channels.GetFullChannelRequest(channel=ch))
            chs = client.get_entity(result.full_chat)
            chat_about = result.full_chat.about
            chs_title = chs.title
            username = chs.username
            # Get the number of members in the group or channel
            if hasattr(result.full_chat, "participants_count"):
                members_count = result.full_chat.participants_count
            else:
                members_count = 0
            # Record the parsing time
            parsing_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            print(dialog_id, chs_title, chat_about, f"https://t.me/{username}", members_count, parsing_time)
            entities = [dialog_id, chs_title, chat_about, f"https://t.me/{username}", members_count, parsing_time]
            writing_data_to_the_db(creating_a_table, writing_data_to_a_table, entities)
        except TypeError:
            continue  # Записываем ошибку в software_database.db и продолжаем работу


def add_columns_to_table():
    """Добавляем новые колонки в базу данных"""
    conn = sqlite3.connect("setting_user/software_database.db")
    c = conn.cursor()
    try:
        # Add the members_count column
        c.execute("ALTER TABLE groups_and_channels ADD COLUMN members_count INTEGER")
        # Add the parsing_time column
        c.execute("ALTER TABLE groups_and_channels ADD COLUMN parsing_time TEXT")
        conn.commit()
    except sqlite3.OperationalError:
        print("Columns already exist")
    finally:
        conn.close()


if __name__ == "__main__":
    parsing_of_groups_to_which_the_account_is_subscribed()
