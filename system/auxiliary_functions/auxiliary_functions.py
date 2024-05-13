import json
import os
import os.path
import platform
import random  # Импортируем модуль random, чтобы генерировать случайное число
import time  # Импортируем модуль time, чтобы работать с временем
from sys import platform

from loguru import logger
from rich.progress import track

from system.auxiliary_functions.global_variables import time_changing_accounts_1
from system.auxiliary_functions.global_variables import time_changing_accounts_2
from system.auxiliary_functions.global_variables import time_inviting_1
from system.auxiliary_functions.global_variables import time_inviting_2
from system.error.telegram_errors import record_account_actions
from system.menu.app_banner import banner


def read_json_file(filename):
    """Чтение данных из файла JSON.
    :param filename: Полный путь к файлу JSON.
    :return: Данные из файла JSON в виде словаря."""
    with open(filename, 'r', encoding="utf-8") as file:
        data = json.load(file)
    return data


def find_files(directory_path, extension) -> list:
    """Поиск файлов с определенным расширением в директории.
    :arg directory_path: - путь к директории
    :arg extension: - расширение файла
    :return list: - список имен найденных файлов"""

    entities = []  # Создаем словарь с именами найденных аккаунтов в папке user_settings/accounts
    for x in os.listdir(directory_path):
        if x.endswith(f".{extension}"):  # Проверяем, заканчивается ли имя файла на заданное расширение
            file = os.path.splitext(x)[0]  # Разделяем имя файла на имя без расширения и расширение
            logger.info(f"Найденные файлы: {file}.{extension}")  # Выводим имена найденных аккаунтов
            entities.append([file])  # Добавляем информацию о файле в список

    return entities  # Возвращаем список json файлов


def display_progress_bar(time_range_1, time_range_2, message) -> None:
    """Отображаем время смены аккаунта или username в виде progress bar"""
    # Генерируем случайное число в указанном диапазоне времени
    selected_shift_time = random.randrange(time_range_1, time_range_2)
    for _ in track(range(selected_shift_time),
                   description=f"[red]{message} через {selected_shift_time} секунды/секунд..."):
        time.sleep(1)


def record_inviting_results(username, phone, description_action, event, actions, db_handler) -> None:
    """Запись результатов inviting, отправка сообщений в базу данных"""
    record_account_actions(phone, description_action, event, actions, db_handler)
    db_handler.delete_row_db(table="members", column="username", value=username)
    # Смена username через случайное количество секунд
    display_progress_bar(time_inviting_1, time_inviting_2, "Переход к новому username")


def record_and_interrupt(actions, phone, description_action, event, db_handler) -> None:
    """Запись данных в базу данных и прерывание выполнения кода"""
    record_account_actions(phone, description_action, event, actions, db_handler)
    # Смена аккаунта через случайное количество секунд
    display_progress_bar(time_changing_accounts_1, time_changing_accounts_2, "Ожидайте смены аккаунта")


def clear_console_and_display_banner() -> None:
    """Чистим консоль, выводим банер"""
    if platform == 'win32':
        os.system("cls")  # Чистим консоль (для windows cls)
    else:
        os.system("clear")  # Чистим консоль (для linux clear)
    banner()  # Ставим банер программы, для красивого визуального отображения


def column_names(table) -> None:
    """Название столбцов, для меню программы"""
    table.add_column("[medium_purple3]№ функции", justify="left", style="cyan")
    table.add_column("[medium_purple3]Функция", justify="left", style="sandy_brown")


if __name__ == "__main__":
    clear_console_and_display_banner()
