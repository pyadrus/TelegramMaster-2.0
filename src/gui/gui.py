# -*- coding: utf-8 -*-
import datetime

from src.gui.menu import log_and_display


async def start_time(list_view, page):
    start = datetime.datetime.now()  # фиксируем и выводим время старта работы кода
    await log_and_display('▶️ Время старта: ' + str(start), list_view, page)
    return start


async def end_time(start, list_view, page):
    finish = datetime.datetime.now()  # фиксируем и выводим время окончания работы кода
    await log_and_display('Время окончания: ' + str(finish), list_view, page)
    await log_and_display('Время работы: ' + str(finish - start), list_view, page)
