from rich import print
from system.notification.notification import app_notifications
from system.sqlite_working_tools.sqlite_working_tools import DatabaseHandler
from system.telegram_actions.telegram_actions import connect_to_telegram_account_and_output_name


def unsubscribe_all() -> None:
    """Отписываемся от групп, каналов, личных сообщений"""
    # Открываем базу данных для работы с аккаунтами user_settings/software_database.db
    db_handler = DatabaseHandler()
    records: list = db_handler.open_and_read_data("config")
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
