# -*- coding: utf-8 -*-
from rich import print
from system.notification.notification import app_notifications
from system.sqlite_working_tools.sqlite_working_tools import open_the_db_and_read_the_data
from system.telegram_actions.telegram_actions import connect_to_telegram_account_and_output_name


def unsubscribe_all() -> None:
    """Отписываемся от групп, каналов, личных сообщений"""
    # Открываем базу данных для работы с аккаунтами setting_user/software_database.db
    records: list = open_the_db_and_read_the_data(name_database_table="config")
    print(f"[bold red]Всего accounts: {len(records)}")
    for row in records:
        # Подключение к Telegram и вывод имя аккаунта в консоль / терминал
        client, phone = connect_to_telegram_account_and_output_name(row)
        for dialog in client.iter_dialogs():
            print(f"[green]{dialog.name}, {dialog.id}")
            client.delete_dialog(dialog)
            client.disconnect()
    app_notifications(notification_text="Список почистили!")  # Выводим уведомление


if __name__ == "__main__":
    unsubscribe_all()
