# -*- coding: utf-8 -*-
import datetime

import flet as ft
from loguru import logger
from telethon import functions

from src.features.account.TGConnect import TGConnect
from src.core.utils import find_filess
from src.core.configs import path_creating_folder, line_width_button, BUTTON_HEIGHT
from src.core.localization import back_button, creating_groups_button
from src.gui.menu import log_and_display_info


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
        lv = ft.ListView(expand=10, spacing=1, padding=2, auto_scroll=True)
        page.controls.append(lv)  # добавляем ListView на страницу для отображения логов 📝
        page.update()  # обновляем страницу, чтобы сразу показать ListView 🔄

        async def add_items(_):
            """
            🚀 Запускает процесс создания групп и отображает статус в интерфейсе.
            """
            # Индикация начала создания групп
            await log_and_display_info(f"▶️ Начало создания групп.\n🕒 Время старта: {str(start)}", lv, page)
            page.update()  # Обновите страницу, чтобы сразу показать сообщение 🔄

            try:
                for session_name in find_filess(directory_path=path_creating_folder, extension='session'):
                    client = await self.tg_connect.get_telegram_client(page, session_name,
                                                                       account_directory=path_creating_folder)

                    response = await client(functions.channels.CreateChannelRequest(title='My awesome title',
                                                                                    about='Description for your group',
                                                                                    megagroup=True))
                    logger.info(response.stringify())

            except TypeError:  # Обработка ошибки при создании групп, если аккаунт не рабочий
                pass
            except Exception as error:
                logger.exception(f"❌ Ошибка: {error}")

            finish = datetime.datetime.now()  # фиксируем время окончания создания групп ⏰
            await log_and_display_info(
                f"🔚 Конец создания групп.\n🕒 Время окончания: {finish}.\n⏳ Время работы: {finish - start}",
                lv, page)

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
                    lv,  # отображение логов 📝
                    ft.Column(),  # резерв для приветствия или других элементов интерфейса
                    ft.ElevatedButton(width=line_width_button, height=BUTTON_HEIGHT, text=creating_groups_button,
                                      on_click=add_items),  # Кнопка "🚀 Начать создание групп"
                    ft.ElevatedButton(width=line_width_button, height=BUTTON_HEIGHT, text=back_button,
                                      on_click=back_button_clicked)  # Кнопка "⬅️ Назад"
                ],
            )
        )

        page.update()  # обновляем страницу после добавления элементов управления 🔄
