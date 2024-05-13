import datetime
import os
from loguru import logger
from rich import print


def record_account_actions(phone_number, action_description, event, action_result, db_handler) -> None:
    """Записывает действия аккаунта в базу данных
    :arg phone_number: номер телефона аккаунта
    :arg action_description: описание действия
    :arg event: действие, которое производится
    :arg action_result: результат выполнения действия.
    :arg db_handler: База данных для записи действий аккаунта в базу данных"""
    logger.error(f"[!] {action_result}")
    date = datetime.datetime.now()  # Получаем текущую дату
    entities = [phone_number, str(date), action_description, event, action_result]  # Формируем словарь
    db_handler.write_data_to_db(
        """CREATE TABLE IF NOT EXISTS account_actions (phone, date, description_action, event, actions)""",
        """INSERT INTO  account_actions (phone, date, description_action, event, actions) VALUES (?, ?, ?, ?, ?)""",
        entities)  # Запись данных в базу данных


def delete_files(file) -> None:
    """Удаление файлов"""
    try:
        os.remove(f"{file}")
    except FileNotFoundError:
        print(f"[red][!] Файл {file} не найден!")


def telegram_phone_number_banned_error(client, phone, db_handler) -> None:
    """Аккаунт banned, удаляем banned аккаунт"""
    client.disconnect()  # Разрываем соединение Telegram, для удаления session файла
    db_handler.delete_row_db(table="config", column="phone", value=phone)
    delete_files(file=f"user_settings/accounts/{phone}.session")
