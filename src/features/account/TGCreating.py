# -*- coding: utf-8 -*-
import datetime

import flet as ft
from loguru import logger
from telethon import functions

from src.core.configs import path_creating_folder, line_width_button, BUTTON_HEIGHT
from src.core.localization import back_button, start_button
from src.core.utils import find_filess
from src.features.account.TGConnect import TGConnect
from src.gui.menu import log_and_display


class CreatingGroupsAndChats:
    """
    Создание групп (чатов) в автоматическом режиме
    """

    def __init__(self):
        self.tg_connect = TGConnect()

    async def creating_groups_and_chats(self, page: ft.Page) -> None:
        """
        Создание групп (чатов) в автоматическом режиме

        :param page: Страница интерфейса Flet для отображения элементов управления.
        """
        start = datetime.datetime.now()  # фиксируем время начала выполнения кода ⏱️
        list_view = ft.ListView(expand=10, spacing=1, padding=2, auto_scroll=True)
        page.controls.append(list_view)  # добавляем ListView на страницу для отображения логов 📝
        page.update()  # обновляем страницу, чтобы сразу показать ListView 🔄

        async def add_items(_):
            """
            🚀 Запускает процесс создания групп и отображает статус в интерфейсе.
            """
            # Индикация начала создания групп
            await log_and_display(f"▶️ Начало создания групп.\n🕒 Время старта: {str(start)}", list_view, page)
            page.update()  # Обновите страницу, чтобы сразу показать сообщение 🔄

            try:
                for session_name in await find_filess(directory_path=path_creating_folder, extension='session',
                                                      list_view=list_view, page=page):
                    client = await self.tg_connect.get_telegram_client(page, session_name,
                                                                       account_directory=path_creating_folder,
                                                                       list_view=list_view)

                    response = await client(functions.channels.CreateChannelRequest(title='My awesome title',
                                                                                    about='Description for your group',
                                                                                    megagroup=True))
                    await log_and_display(f"{response.stringify()}", list_view, page)

            except TypeError:  # Обработка ошибки при создании групп, если аккаунт не рабочий
                pass
            except Exception as error:
                logger.exception(f"❌ Ошибка: {error}")

            finish = datetime.datetime.now()  # фиксируем время окончания создания групп ⏰
            await log_and_display(
                f"🔚 Конец создания групп.\n🕒 Время окончания: {finish}.\n⏳ Время работы: {finish - start}",
                list_view, page)

        async def back_button_clicked(_):
            """
            ⬅️ Обрабатывает нажатие кнопки "Назад", возвращая в меню создания групп.
            """
            page.go("/creating_groups_and_chats_menu")  # переходим к основному меню создания групп 🏠

        # Добавляем кнопки и другие элементы управления на страницу
        page.views.append(
            ft.View(
                "/creating_groups_and_chats_menu",
                [
                    list_view,  # отображение логов 📝
                    ft.Column(),  # резерв для приветствия или других элементов интерфейса
                    ft.ElevatedButton(width=line_width_button, height=BUTTON_HEIGHT, text=start_button,
                                      on_click=add_items),  # Кнопка "🚀 Начать создание групп"
                    ft.ElevatedButton(width=line_width_button, height=BUTTON_HEIGHT, text=back_button,
                                      on_click=back_button_clicked)  # Кнопка "⬅️ Назад"
                ],
            )
        )

        page.update()  # обновляем страницу после добавления элементов управления 🔄
