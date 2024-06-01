import json
import os
import os.path
import platform
import random  # Импортируем модуль random, чтобы генерировать случайное число
import time  # Импортируем модуль time, чтобы работать с временем
from sys import platform

from loguru import logger

from system.auxiliary_functions.global_variables import ConfigReader
from system.error.telegram_errors import record_account_actions
from system.menu.app_banner import banner

configs_reader = ConfigReader()
time_changing_accounts_1, time_changing_accounts_2 = configs_reader.get_time_changing_accounts()
time_inviting_1, time_inviting_2 = configs_reader.get_time_inviting()


def read_json_file(filename):
    """
    Чтение данных из файла JSON.
    :param filename: Полный путь к файлу JSON.
    :return: Данные из файла JSON в виде словаря.
    """
    with open(filename, 'r', encoding="utf-8") as file:
        data = json.load(file)
    return data


def find_files(directory_path, extension) -> list:
    """
    Поиск файлов с определенным расширением в директории.
    :arg directory_path: - путь к директории
    :arg extension: - расширение файла
    :return list: - список имен найденных файлов
    """

    entities = []  # Создаем словарь с именами найденных аккаунтов в папке user_settings/accounts
    for x in os.listdir(directory_path):
        if x.endswith(f".{extension}"):  # Проверяем, заканчивается ли имя файла на заданное расширение
            file = os.path.splitext(x)[0]  # Разделяем имя файла на имя без расширения и расширение
            logger.info(f"Найденные файлы: {file}.{extension}")  # Выводим имена найденных аккаунтов
            entities.append([file])  # Добавляем информацию о файле в список

    return entities  # Возвращаем список json файлов


def record_inviting_results(time_range_1, time_range_2, username, description_action, event, actions, db_handler) -> None:
    """
    Запись результатов inviting, отправка сообщений в базу данных.
    :param time_range_1:  - диапазон времени смены аккаунта
    :param time_range_2:  - диапазон времени смены аккаунта
    :param username: - username аккаунта
    :param description_action: - описание действия
    :param event: - событие
    :param actions: - список действий
    :param db_handler: - объект класса БД
    """
    record_account_actions(description_action, event, actions, db_handler)
    db_handler.delete_row_db(table="members", column="username", value=username)
    # Смена username через случайное количество секунд
    selected_shift_time = random.randrange(time_range_1, time_range_2)
    print(f"Переход к новому username через {selected_shift_time} секунд")
    time.sleep(selected_shift_time)


def record_and_interrupt(actions, description_action, event, db_handler, time_range_1, time_range_2) -> None:
    """
    Запись данных в базу данных и прерывание выполнения кода.
    :param time_range_1:  - диапазон времени смены аккаунта
    :param time_range_2:  - диапазон времени смены аккаунта
    :param actions:  - список действий
    :param description_action:  - описание действия
    :param event:  - событие
    :param db_handler:  - объект класса БД
    """
    record_account_actions(description_action, event, actions, db_handler)
    # Смена аккаунта через случайное количество секунд
    selected_shift_time = random.randrange(time_range_1, time_range_2)
    print(f"Переход к новому username через {selected_shift_time} секунд")
    time.sleep(selected_shift_time)


def clear_console_and_display_banner() -> None:
    """Чистим консоль, выводим банер"""
    if platform == 'win32':
        os.system("cls")  # Чистим консоль (для windows cls)
    else:
        os.system("clear")  # Чистим консоль (для linux clear)
    banner()  # Ставим банер программы, для красивого визуального отображения


if __name__ == "__main__":
    clear_console_and_display_banner()
