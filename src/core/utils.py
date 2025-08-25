# -*- coding: utf-8 -*-
import asyncio
import json
import os
import os.path
import random  # Импортируем модуль random, чтобы генерировать случайное число

import flet as ft
from loguru import logger

from src.core.sqlite_working_tools import delete_row_db
from src.gui.gui import AppLogger


def read_json_file(filename):
    """
    Чтение данных из файла JSON.

    :param filename: Полный путь к файлу JSON.
    :return:         Данные из файла JSON в виде словаря.
    """
    with open(filename, 'r', encoding="utf-8") as file:
        data = json.load(file)
    return data


def all_find_files(directory_path) -> list:
    """
    Поиск файлов в директории.

    :param directory_path:  Путь к директории
    :return list:           Список имен найденных файлов
    """
    entities = []  # Создаем список с именами найденных файлов
    for x in os.listdir(directory_path):
        if os.path.isfile(os.path.join(directory_path, x)):  # Проверяем, является ли x файлом
            entities.append(x)  # Добавляем имя файла в список
    return entities  # Возвращаем список файлов


def find_filess(directory_path, extension):
    """
    Поиск файлов с определенным расширением в директории. Расширение файла должно быть указанно без точки.

    :param directory_path: Путь к директории
    :param extension: Расширение файла (указанное без точки)
    :return list: Список имен найденных файлов
    """
    entities = []  # Создаем словарь с именами найденных аккаунтов в папке user_data/accounts
    for x in os.listdir(directory_path):
        if x.endswith(f".{extension}"):  # Проверяем, заканчивается ли имя файла на заданное расширение
            file = os.path.splitext(x)[0]  # Разделяем имя файла на имя без расширения и расширение
            entities.append(file)  # Добавляем информацию о файле в список
    return entities  # Возвращаем список json файлов


async def find_files(directory_path, extension, page: ft.Page) -> list:
    """
    Поиск файлов с определенным расширением в директории. Расширение файла должно быть указанно без точки.

    :param directory_path: Путь к директории
    :param extension: Расширение файла (указанное без точки)
    :param page: Страница для отображения информации.
    :return list: Список имен найденных файлов
    """
    entities = []  # Создаем словарь с именами найденных аккаунтов в папке user_data/accounts
    for x in os.listdir(directory_path):
        if x.endswith(f".{extension}"):  # Проверяем, заканчивается ли имя файла на заданное расширение
            file = os.path.splitext(x)[0]  # Разделяем имя файла на имя без расширения и расширение
            entities.append([file])  # Добавляем информацию о файле в список

    app_logger = AppLogger(page)
    await app_logger.log_and_display(f"🔍 Найденные файлы: {entities}")

    return entities  # Возвращаем список json файлов


def working_with_accounts(account_folder, new_account_folder) -> None:
    """
    Работа с аккаунтами

    :param account_folder: Исходный путь к файлу
    :param new_account_folder: Путь к новой папке, куда нужно переместить файл
    """
    try:  # Переносим файлы в нужную папку
        os.replace(account_folder, new_account_folder)
    except FileNotFoundError:  # Если в папке нет нужной папки, то создаем ее
        try:
            os.makedirs(new_account_folder)
            os.replace(account_folder, new_account_folder)
        except FileExistsError:  # Если файл уже существует, то удаляем его
            os.remove(account_folder)
    except PermissionError as error:
        logger.error(f"❌ Ошибка: {error}")
        logger.error("❌ Не удалось перенести файлы в нужную папку")
    # except Exception as error:
    #     logger.exception(error)


async def record_inviting_results(time_range_1: int, time_range_2: int, username: str, page: ft.Page) -> None:
    """
    Запись результатов inviting, отправка сообщений в базу данных.

    :param time_range_1:  - диапазон времени смены аккаунта
    :param time_range_2:  - диапазон времени смены аккаунта
    :param username: - username аккаунта
    :param page: Страница для отображения информации.
    """
    app_logger = AppLogger(page)
    await app_logger.log_and_display(f"Удаляем с базы данных username {username}")

    # Открываем базу с аккаунтами и с выставленными лимитами
    delete_row_db(username=username)

    # Смена username через случайное количество секунд
    await record_and_interrupt(time_range_1, time_range_2, page)


async def record_and_interrupt(time_range_1, time_range_2, page: ft.Page) -> None:
    """
    Запись данных в базу данных и прерывание выполнения кода.

    :param time_range_1:  - диапазон времени смены аккаунта
    :param time_range_2:  - диапазон времени смены аккаунта
    :param page: Страница для отображения информации.
    """
    # Смена аккаунта через случайное количество секунд
    selected_shift_time = random.randrange(int(time_range_1), int(time_range_2))
    app_logger = AppLogger(page)
    await app_logger.log_and_display(f"Переход к новому username через {selected_shift_time} секунд")
    await asyncio.sleep(selected_shift_time)
