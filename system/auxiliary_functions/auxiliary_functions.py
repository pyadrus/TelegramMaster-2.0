import json
import os
import os.path
import random  # Импортируем модуль random, чтобы генерировать случайное число
import time  # Импортируем модуль time, чтобы работать с временем

from loguru import logger

from system.sqlite_working_tools.sqlite_working_tools import DatabaseHandler


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


async def record_account_actions(action_description, event, action_result, db_handler) -> None:
    """Записывает действия аккаунта в базу данных
    :arg action_description: описание действия
    :arg event: действие, которое производится
    :arg action_result: результат выполнения действия.
    :arg db_handler: База данных для записи действий аккаунта в базу данных"""
    logger.error(f"[!] {action_result}")
    # date = datetime.datetime.now()  # Получаем текущую дату
    # entities = [str(date), action_description, event, action_result]  # Формируем словарь
    # await db_handler.write_data_to_db(
    #     """CREATE TABLE IF NOT EXISTS account_actions (phone, date, description_action, event, actions)""",
    #     """INSERT INTO  account_actions (phone, date, description_action, event, actions) VALUES (?, ?, ?, ?, ?)""",
    #     entities)  # Запись данных в базу данных


async def record_inviting_results(time_range_1: int, time_range_2: int, username: str) -> None:
    """
    Запись результатов inviting, отправка сообщений в базу данных.
    :param time_range_1:  - диапазон времени смены аккаунта
    :param time_range_2:  - диапазон времени смены аккаунта
    :param username: - username аккаунта
    """
    db_handler = DatabaseHandler()  # Открываем базу с аккаунтами и с выставленными лимитами
    await db_handler.delete_row_db(table="members", column="username", value=username)
    # Смена username через случайное количество секунд
    selected_shift_time = random.randrange(int(time_range_1), int(time_range_2))
    logger.info(f"Переход к новому username через {selected_shift_time} секунд")
    time.sleep(selected_shift_time)


def record_and_interrupt(time_range_1, time_range_2) -> None:
    """
    Запись данных в базу данных и прерывание выполнения кода.
    :param time_range_1:  - диапазон времени смены аккаунта
    :param time_range_2:  - диапазон времени смены аккаунта
    """
    # Смена аккаунта через случайное количество секунд
    selected_shift_time = random.randrange(time_range_1, time_range_2)
    logger.info(f"Переход к новому username через {selected_shift_time} секунд")
    time.sleep(selected_shift_time)
