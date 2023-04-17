from telethon import functions

from system.error.telegram_errors import recording_actions_in_the_db
from system.notification.notification import app_notifications
from system.sqlite_working_tools.sqlite_working_tools import delete_duplicates
from system.sqlite_working_tools.sqlite_working_tools import open_the_db_and_read_the_data
from system.sqlite_working_tools.sqlite_working_tools import writing_data_to_the_db
from telethon.tl.functions.channels import GetFullChannelRequest  # Не удалять

from system.telegram_actions.telegram_actions import connect_to_telegram_account_and_output_name

creating_a_table = "CREATE TABLE IF NOT EXISTS groups_and_channels(id, title, about, link)"
writing_data_to_a_table = "INSERT INTO groups_and_channels (id, title, about, link) VALUES (?, ?, ?, ?)"


def parsing_of_groups_to_which_the_account_is_subscribed() -> None:
    """Parsing групп / каналов на которые подписан аккаунт и сохраняем в файл software_database.db"""
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
        for dialog in client.iter_dialogs():
            try:
                dialog_id = dialog.id
                ch = client.get_entity(dialog_id)
                result = client(functions.channels.GetFullChannelRequest(channel=ch))
                chs = client.get_entity(result.full_chat)
                chat_about = result.full_chat.about
                chs_title = chs.title
                username = chs.username
                entities = [dialog_id, chs_title, chat_about, f"https://t.me/{username}"]
                print(entities)
                writing_data_to_the_db(creating_a_table, writing_data_to_a_table, entities)
            except TypeError:
                continue  # Записываем ошибку в software_database.db и продолжаем работу
        client.disconnect()  # Разрываем соединение telegram
    # Чистка дубликатов в базе данных
    delete_duplicates(table_name="groups_and_channels", column_name="id")


if __name__ == "__main__":
    parsing_of_groups_to_which_the_account_is_subscribed()
