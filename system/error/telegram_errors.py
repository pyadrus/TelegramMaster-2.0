# -*- coding: utf-8 -*-
import os

from loguru import logger


def delete_files(file) -> None:
    """Удаление файлов"""
    try:
        os.remove(f"{file}")
    except FileNotFoundError:
        logger.info(f"[red][!] Файл {file} не найден!")


def telegram_phone_number_banned_error(client, phone, db_handler) -> None:
    """Аккаунт banned, удаляем banned аккаунт"""
    client.disconnect()  # Разрываем соединение Telegram, для удаления session файла
    db_handler.delete_row_db(table="config", column="phone", value=phone)
    delete_files(file=f"user_settings/accounts/{phone}.session")
