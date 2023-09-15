from rich import print
from telethon.errors import YouBlockedUserError
from telethon.sync import TelegramClient  # Не удалять, так как используется кодом
from system.error.telegram_errors import record_account_actions
from system.notification.notification import app_notifications
from system.sqlite_working_tools.sqlite_working_tools import open_the_db_and_read_the_data
from system.telegram_actions.telegram_actions import connect_to_telegram_account_and_output_name


def check_account_for_spam() -> None:
    """Проверка аккаунта на спам через @SpamBot"""
    event: str = "Проверка аккаунтов через SpamBot"  # Событие, которое записываем в базу данных
    app_notifications(notification_text=event)  # Выводим уведомление
    # Открываем базу данных для работы с аккаунтами user_settings/software_database.db
    records: list = open_the_db_and_read_the_data(name_database_table="config")
    for row in records:
        # Подключение к Telegram и вывод имя аккаунта в консоль / терминал
        client, phone = connect_to_telegram_account_and_output_name(row)
        try:
            client.send_message('SpamBot', '/start')  # Находим спам бот, и вводим команду /start
            message_bot = client.get_messages('SpamBot')
            for message in message_bot:
                print(f"[bold green]{phone} {message.message}")
                # Выводим сообщение от спама бота
                description_action = "Checking: checking account for SpamBot"
                actions = f"{message.message}"
                print(f"[green][+] {actions}")
                record_account_actions(phone, description_action, event, actions)
        except YouBlockedUserError:
            continue  # Записываем ошибку в software_database.db и продолжаем работу


if __name__ == "__main__":
    check_account_for_spam()
