# -*- coding: utf-8 -*-
import datetime

import flet as ft
from loguru import logger

list_view = ft.ListView(expand=10, spacing=1, padding=2, auto_scroll=True)


class AppLogger:

    def __init__(self, page: ft.Page):
        self.page = page
        self.list_view = ft.ListView(expand=10, spacing=1, padding=2, auto_scroll=True)

    async def start_time(self):
        start = datetime.datetime.now()  # фиксируем и выводим время старта работы кода
        await self.log_and_display('▶️ Время старта: ' + str(start))
        return start

    async def end_time(self, start):
        finish = datetime.datetime.now()  # фиксируем и выводим время окончания работы кода
        await self.log_and_display('⏹️ Время окончания: ' + str(finish))
        await self.log_and_display('⏱️ Время работы: ' + str(finish - start))

    async def log_and_display(self, message: str, level: str = "info"):
        """
        Выводит сообщение в GUI и записывает лог с указанным уровнем с помощью loguru.

        :param message: Текст сообщения для отображения и записи в лог
        :param level: Уровень логирования ("info" или "error"), по умолчанию "info"
        """
        if level.lower() == "error":
            logger.error(message)
        else:
            self.list_view.controls.append(ft.Text(message))
        self.page.update()


