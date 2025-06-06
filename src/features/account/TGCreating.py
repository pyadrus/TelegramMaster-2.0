# -*- coding: utf-8 -*-
import os
import os.path
import shutil

import flet as ft
from loguru import logger
from telethon import functions

from src.core.configs import (BUTTON_HEIGHT, line_width_button,
                              path_accounts_folder)
from src.core.utils import find_filess
from src.features.account.TGConnect import TGConnect
from src.gui.gui import end_time, list_view, log_and_display, start_time
from src.locales.translations_loader import translations


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
        selected_sessions = []  # Список для хранения выбранных session файлов
        selected_files = ft.Text(value=translations["ru"]["notifications"]["files_not_selected"], selectable=True)
        page.controls.append(list_view)  # добавляем ListView на страницу для отображения логов 📝
        page.update()  # обновляем страницу, чтобы сразу показать ListView 🔄

        async def add_items(_):
            """
            🚀 Запускает процесс создания групп и отображает статус в интерфейсе.
            """
            start = await start_time(page)
            page.update()

            if not selected_sessions:
                await log_and_display(translations["ru"]["errors"]["files_not_selected_warning"], page)
                session_files = await find_filess(directory_path=path_accounts_folder, extension='session')
                if not session_files:
                    await log_and_display(translations["ru"]["errors"]["no_session_files"], page)
                    page.update()
                    return
            else:
                session_files = selected_sessions
                await log_and_display(translations["ru"]["notifications"]["start_creating"], page)
            try:
                for session_name in session_files:
                    # Извлекаем только имя файла без расширения
                    session_name = os.path.splitext(os.path.basename(session_name))[0]
                    client = await self.tg_connect.get_telegram_client(page, session_name,
                                                                       account_directory=path_accounts_folder)
                    await client(functions.channels.CreateChannelRequest(title='My awesome title',
                                                                         about='Description for your group',
                                                                         megagroup=True))
                    await log_and_display(translations["ru"]["notifications"]["notification_creating"], page)
            except TypeError:
                pass
            except Exception as error:
                logger.exception(error)
            await end_time(start, page)

        async def btn_click(e: ft.FilePickerResultEvent) -> None:
            if e.files:
                selected_sessions.clear()
                for file in e.files:
                    file_name = file.name
                    file_path = file.path
                    if file_name.endswith(".session"):
                        target_folder = path_accounts_folder
                        target_path = os.path.join(target_folder, file_name)
                        if not os.path.exists(target_path) or file_path != os.path.abspath(target_path):
                            os.makedirs(target_folder, exist_ok=True)
                            shutil.copy(file_path, target_path)
                        selected_sessions.append(target_path)
                    else:
                        selected_files.value = f"Файл {file_name} не является session файлом. Выберите только .session файлы."
                        selected_files.update()
                        return
                selected_files.value = f"Выбраны session файлы: {', '.join([os.path.basename(s) for s in selected_sessions])}"
                selected_files.update()
            else:
                selected_files.value = "Выбор файлов отменен"
                selected_files.update()

            page.update()

        # Кнопка выбора session файлов
        pick_files_dialog = ft.FilePicker(on_result=btn_click)
        page.overlay.append(pick_files_dialog)

        # Добавляем элементы интерфейса на страницу
        page.views.append(ft.View("/creating_groups_and_chats_menu",
                                  [ft.AppBar(title=ft.Text(translations["ru"]["menu"]["main"]),
                                             bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST),
                                   ft.Text(spans=[ft.TextSpan(translations["ru"]["menu"]["create_groups"], ft.TextStyle(
                                       size=20, weight=ft.FontWeight.BOLD,
                                       foreground=ft.Paint(gradient=ft.PaintLinearGradient((0, 20), (150, 20),
                                                                                           [ft.Colors.PINK,
                                                                                            ft.Colors.PURPLE])), ), ), ]),
                                   list_view, selected_files,
                                   ft.ElevatedButton(width=line_width_button, height=BUTTON_HEIGHT,
                                                     text=translations["ru"]["create_groups_menu"][
                                                         "choose_session_files"],
                                                     on_click=lambda _: pick_files_dialog.pick_files(
                                                         allow_multiple=True)),
                                   ft.ElevatedButton(width=line_width_button, height=BUTTON_HEIGHT,
                                                     text=translations["ru"]["buttons"]["start"], on_click=add_items),
                                   ft.ElevatedButton(width=line_width_button, height=BUTTON_HEIGHT,
                                                     text=translations["ru"]["buttons"]["back"],
                                                     on_click=lambda _: page.go("/"))]))
        page.update()
