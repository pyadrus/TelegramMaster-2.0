import time

from telethon import functions

from system.error.telegram_errors import record_account_actions
from telethon.tl.functions.channels import GetFullChannelRequest  # Не удалять
from system.telegram_actions.telegram_actions import telegram_connect_and_output_name


def parsing_groups_which_account_subscribed(db_handler) -> None:
    """Parsing групп / каналов на которые подписан аккаунт и сохраняем в файл software_database.db"""
    # app_notifications(notification_text="Parsing групп / каналов на которые подписан аккаунт")  # Выводим уведомление
    # Открываем базу данных для работы с аккаунтами user_settings/software_database.db
    records: list = db_handler.open_and_read_data("config")
    for row in records:
        # Подключение к Telegram и вывод имя аккаунта в консоль / терминал
        client, phone = telegram_connect_and_output_name(row, db_handler)
        record_account_actions("Parsing: groups and channels",
                               "Parsing групп / каналов на которые подписан аккаунт",
                               "Parsing групп / каналов", db_handler)
        forming_a_list_of_groups(client, db_handler)
        client.disconnect()  # Разрываем соединение telegram
    db_handler.delete_duplicates(table_name="groups_and_channels", column_name="id")  # Чистка дубликатов в базе данных


def forming_a_list_of_groups(client, db_handler) -> None:
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
            db_handler.write_data_to_db(creating_a_table="CREATE TABLE IF NOT EXISTS groups_and_channels(id, title, about, link, members_count, parsing_time)",
                                        writing_data_to_a_table="INSERT INTO groups_and_channels (id, title, about, link, members_count, parsing_time) VALUES (?, ?, ?, ?, ?, ?)",
                                        entities=entities)
        except TypeError:
            continue  # Записываем ошибку в software_database.db и продолжаем работу
