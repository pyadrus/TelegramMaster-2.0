import time

from telethon import functions

from system.error.telegram_errors import record_account_actions
from system.notification.notification import app_notifications
from system.sqlite_working_tools.sqlite_working_tools import add_columns_to_table, DatabaseHandler
from telethon.tl.functions.channels import GetFullChannelRequest  # Не удалять
from system.telegram_actions.telegram_actions import connect_to_telegram_account_and_output_name

creating_a_table = "CREATE TABLE IF NOT EXISTS groups_and_channels(id, title, about, link, members_count, parsing_time)"
writing_data_to_a_table = "INSERT INTO groups_and_channels (id, title, about, link, members_count, parsing_time) VALUES (?, ?, ?, ?, ?, ?)"


def parsing_of_groups_to_which_the_account_is_subscribed() -> None:
    """Parsing групп / каналов на которые подписан аккаунт и сохраняем в файл software_database.db"""
    add_columns_to_table()
    event: str = "Parsing групп / каналов на которые подписан аккаунт"  # Событие, которое записываем в базу данных
    app_notifications(notification_text=event)  # Выводим уведомление
    # Открываем базу данных для работы с аккаунтами user_settings/software_database.db
    db_handler = DatabaseHandler()
    records: list = db_handler.open_and_read_data("config")
    for row in records:
        # Подключение к Telegram и вывод имя аккаунта в консоль / терминал
        client, phone = connect_to_telegram_account_and_output_name(row)
        description_action = "Parsing: groups and channels"
        actions = "Parsing групп / каналов"
        record_account_actions(phone, description_action, event, actions)
        forming_a_list_of_groups(client)
        client.disconnect()  # Разрываем соединение telegram
    db_handler.delete_duplicates(table_name="groups_and_channels", column_name="id")  # Чистка дубликатов в базе данных


def forming_a_list_of_groups(client) -> None:
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
            # Получение количества участников в группе или канале
            if hasattr(result.full_chat, "participants_count"):
                members_count = result.full_chat.participants_count
            else:
                members_count = 0
            # Запишите время синтаксического анализа
            parsing_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            print(dialog_id, chs_title, chat_about, f"https://t.me/{username}", members_count, parsing_time)
            entities = [dialog_id, chs_title, chat_about, f"https://t.me/{username}", members_count, parsing_time]
            db_handler = DatabaseHandler()
            db_handler.write_data_to_db(creating_a_table, writing_data_to_a_table, entities)
        except TypeError:
            continue  # Записываем ошибку в software_database.db и продолжаем работу


if __name__ == "__main__":
    parsing_of_groups_to_which_the_account_is_subscribed()
