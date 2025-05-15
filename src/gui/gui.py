# -*- coding: utf-8 -*-
import datetime

import flet as ft
from loguru import logger

list_view = ft.ListView(expand=10, spacing=1, padding=2, auto_scroll=True)


async def start_time(page):
    start = datetime.datetime.now()  # фиксируем и выводим время старта работы кода
    await log_and_display('▶️ Время старта: ' + str(start), page)
    return start


async def end_time(start, page):
    finish = datetime.datetime.now()  # фиксируем и выводим время окончания работы кода
    await log_and_display('Время окончания: ' + str(finish), page)
    await log_and_display('Время работы: ' + str(finish - start), page)


async def log_and_display(message: str, page: ft.Page, level: str = "info"):
    """
    Выводит сообщение в GUI и записывает лог с указанным уровнем с помощью loguru.

    :param message: Текст сообщения для отображения и записи в лог
    :param page: Страница интерфейса Flet для отображения элементов управления
    :param level: Уровень логирования ("info" или "error"), по умолчанию "info"
    """
    if level.lower() == "error":
        logger.error(message)
    else:
        list_view.controls.append(ft.Text(message))
    page.update()
