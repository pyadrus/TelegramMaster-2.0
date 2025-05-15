# -*- coding: utf-8 -*-
import flet as ft

from src.core.configs import path_send_message_folder_answering_machine_message, path_folder_with_messages, limits
from src.core.sqlite_working_tools import db_handler
from src.core.utils import find_filess
from src.gui.menu import show_notification


class CheckingProgram:
    """⛔ Проверка программы от пользователя"""

    def __init__(self):
        self.account_extension = "session"  # Расширение файла аккаунта
        self.file_extension = "json"

    @staticmethod
    async def check_before_sending_messages_via_chats(page: ft.Page):
        """
        ⛔ Проверка наличия сформированного списка с чатами для рассылки по чатам.
        ⛔ Проверка папки с сообщениями на наличие заготовленных сообщений.
        """
        if len(await db_handler.select_records_with_limit(table_name="writing_group_links", limit=limits)) == 0:
            await show_notification(page, "⛔ Не сформирован список для рассылки по чатам")

    @staticmethod
    async def check_before_inviting(page: ft.Page):
        """
        ⛔ Проверка наличия пользователя в списке участников, наличия аккаунта, наличия ссылки в базе данных
        :param page: Страница интерфейса Flet для отображения элементов управления.
        """
        if len(await db_handler.select_records_with_limit(table_name="members", limit=limits)) == 0:
            await show_notification(page, "⛔ В таблице members нет пользователей для инвайтинга")
        if len(await db_handler.select_records_with_limit(table_name="links_inviting", limit=limits)) == 0:
            await show_notification(page, "⛔ Не записана группа для инвайтинга")

    async def checking_sending_messages_via_chats_with_answering_machine(self, page: ft.Page):
        """
        ⛔ Проверка наличия аккаунта в папке с аккаунтами (Рассылка сообщений по чатам с автоответчиком)
        :param page: Страница интерфейса Flet для отображения элементов управления.
        """
        if not await find_filess(directory_path=path_folder_with_messages, extension=self.file_extension):
            await show_notification(page, f"⛔ Нет заготовленных сообщений в папке {path_folder_with_messages}")
        if not await find_filess(directory_path=path_send_message_folder_answering_machine_message,
                                 extension=self.file_extension):
            await show_notification(page,
                                    f"⛔ Нет заготовленных сообщений для автоответчика в папке {path_send_message_folder_answering_machine_message}")
        if len(await db_handler.select_records_with_limit(table_name="writing_group_links", limit=limits)) == 0:
            await show_notification(page, "⛔ Не сформирован список для рассылки по чатам")
