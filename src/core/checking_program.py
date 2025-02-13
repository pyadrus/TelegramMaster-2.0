# -*- coding: utf-8 -*-
import flet as ft
from loguru import logger

from src.core.configs import (ConfigReader, path_send_message_folder, path_inviting_folder, path_subscription_folder,
                              path_unsubscribe_folder, path_reactions_folder, path_viewing_folder, path_parsing_folder,
                              path_bio_folder, path_contact_folder, path_creating_folder,
                              path_send_message_folder_answering_machine)
from src.core.sqlite_working_tools import db_handler
from src.core.utils import find_filess
from src.gui.menu import show_notification


class CheckingProgram:
    """⛔ Проверка программы от пользователя"""

    def __init__(self):
        self.account_extension = "session"  # Расширение файла аккаунта
        self.file_extension = "json"

    async def check_before_sending_messages_via_chats(self, page: ft.Page):
        """
        ⛔ Проверка наличия сформированного списка с чатами для рассылки по чатам.
        ⛔ Проверка наличия аккаунта в папке с аккаунтами.
        ⛔ Проверка папки с сообщениями на наличие заготовленных сообщений.
        :param page: Страница интерфейса Flet для отображения элементов управления.
        """
        if not find_filess(directory_path=path_send_message_folder, extension=self.account_extension):
            await show_notification(page, f"⛔ Нет аккаунта в папке {path_send_message_folder}")
            return None
        logger.info("⛔ Проверка папки с сообщениями на наличие заготовленных сообщений")
        if not find_filess(directory_path="user_data/message", extension=self.file_extension):
            logger.error('⛔ Нет заготовленных сообщений в папке message')
            await show_notification(page, "⛔ Нет заготовленных сообщений в папке message")
            return None
        logger.info("⛔ Проверка сформированного списка с чатами для рассылки")
        if len(await db_handler.open_db_func_lim(table_name="writing_group_links",
                                                 account_limit=ConfigReader().get_limits())) == 0:
            logger.error('⛔ Не сформирован список для рассылки по чатам')
            await show_notification(page, "⛔ Не сформирован список для рассылки по чатам")
            return None

    async def checking_sending_to_personal(self, page: ft.Page):
        """
        ⛔ Проверка наличия аккаунта в папке с аккаунтами (Отправка в личку)
        :param page: Страница интерфейса Flet для отображения элементов управления.
        """
        if not find_filess(directory_path=path_send_message_folder, extension=self.account_extension):
            await show_notification(page, f'⛔ Нет аккаунта в папке {path_send_message_folder}')
            return None
        logger.info("⛔ Проверка папки с сообщениями на наличие заготовленных сообщений")
        if not find_filess(directory_path="user_data/message", extension=self.file_extension):
            logger.error('⛔ Нет заготовленных сообщений в папке message')
            await show_notification(page, "⛔ Нет заготовленных сообщений в папке message")
            return None

    async def check_before_inviting(self, page: ft.Page):
        """
        ⛔ Проверка наличия пользователя в списке участников, наличия аккаунта, наличия ссылки в базе данных
        :param page: Страница интерфейса Flet для отображения элементов управления.
        """
        if not find_filess(directory_path=path_inviting_folder, extension=self.account_extension):
            await show_notification(page, f'⛔ Нет аккаунта в папке {path_inviting_folder}')
            return None
        if len(await db_handler.open_db_func_lim(table_name="members",
                                                 account_limit=ConfigReader().get_limits())) == 0:
            logger.error('⛔ В таблице members нет пользователей для инвайтинга')
            await show_notification(page, "⛔ В таблице members нет пользователей для инвайтинга")
            return None
        if len(await db_handler.open_db_func_lim(table_name="links_inviting",
                                                 account_limit=ConfigReader().get_limits())) == 0:
            logger.error('⛔ Не записана группа для инвайтинга')
            await show_notification(page, "⛔ Не записана группа для инвайтинга")
            return None

    async def checking_for_subscription_account(self, page: ft.Page):
        """
        ⛔ Проверка наличия аккаунта в папке с аккаунтами (подписка)
        :param page: Страница интерфейса Flet для отображения элементов управления.
        """
        if not find_filess(directory_path=path_subscription_folder, extension=self.account_extension):
            await show_notification(page, f"⛔ Нет аккаунта в папке {path_subscription_folder}")
            return None

    async def checking_for_unsubscribe_all(self, page: ft.Page):
        """
        ⛔ Проверка наличия аккаунта в папке с аккаунтами (отписка)
        :param page: Страница интерфейса Flet для отображения элементов управления.
        """
        if not find_filess(directory_path=path_unsubscribe_folder, extension=self.account_extension):
            await show_notification(page, f"⛔ Нет аккаунта в папке {path_unsubscribe_folder}")
            return None

    async def checking_for_setting_reactions(self, page: ft.Page):
        """
        ⛔ Проверка наличия аккаунта в папке с аккаунтами (Ставим реакции)
        :param page: Страница интерфейса Flet для отображения элементов управления.
        """
        if not find_filess(directory_path=path_reactions_folder, extension=self.account_extension):
            await show_notification(page, f"⛔ Нет аккаунта в папке {path_reactions_folder}")
            return None

    async def checking_for_viewing_posts_menu(self, page: ft.Page):
        """
        ⛔ Проверка наличия аккаунта в папке с аккаунтами (Автоматическое выставление просмотров меню)
        :param page: Страница интерфейса Flet для отображения элементов управления.
        """
        if not find_filess(directory_path=path_viewing_folder, extension=self.account_extension):
            await show_notification(page, f"⛔ Нет аккаунта в папке {path_viewing_folder}")
            return None

    async def checking_for_parsing_single_groups(self, page: ft.Page):
        """
        ⛔ Проверка наличия аккаунта в папке с аккаунтами (🔍 Парсинг одной группы / групп)
        :param page: Страница интерфейса Flet для отображения элементов управления.
        """
        if not find_filess(directory_path=path_parsing_folder, extension=self.account_extension):
            await show_notification(page, f"⛔ Нет аккаунта в папке {path_parsing_folder}")
            return None

    async def checking_for_bio(self, page: ft.Page):
        """
        ⛔ Проверка наличия аккаунта в папке с аккаунтами (Изменение BIO)
        :param page: Страница интерфейса Flet для отображения элементов управления.
        """
        if not find_filess(directory_path=path_bio_folder, extension=self.account_extension):
            await show_notification(page, f"⛔ Нет аккаунта в папке {path_bio_folder}")
            return None

    async def checking_creating_contact_list(self, page: ft.Page):
        """
        ⛔ Проверка наличия аккаунта в папке с аккаунтами (Формирование списка контактов)
        :param page: Страница интерфейса Flet для отображения элементов управления.
        """
        if not find_filess(directory_path=path_contact_folder, extension=self.account_extension):
            await show_notification(page, f"⛔ Нет аккаунта в папке {path_contact_folder}")
            return None

    async def checking_creating_groups(self, page: ft.Page):
        """
        ⛔ Проверка наличия аккаунта в папке с аккаунтами (Создание групп (чатов))
        :param page: Страница интерфейса Flet для отображения элементов управления.
        """
        if not find_filess(directory_path=path_creating_folder, extension=self.account_extension):
            await show_notification(page, f"⛔ Нет аккаунта в папке {path_creating_folder}")
            return None

    async def checking_sending_messages_via_chats_with_answering_machine(self, page: ft.Page):
        """
        ⛔ Проверка наличия аккаунта в папке с аккаунтами (Рассылка сообщений по чатам с автоответчиком)
        :param page: Страница интерфейса Flet для отображения элементов управления.
        """
        if not find_filess(directory_path=path_send_message_folder_answering_machine, extension=self.account_extension):
            await show_notification(page, f"⛔ Нет аккаунта в папке {path_send_message_folder_answering_machine}")
            return None
        if not find_filess(directory_path=path_send_message_folder, extension=self.account_extension):
            logger.error('⛔ Нет аккаунта в папке send_message')
            await show_notification(page, "⛔ Нет аккаунта в папке send_message")
            return None
        logger.info("⛔ Проверка папки с сообщениями на наличие заготовленных сообщений")
        if not find_filess(directory_path="user_data/message", extension=self.file_extension):
            logger.error('⛔ Нет заготовленных сообщений в папке message')
            await show_notification(page, "⛔ Нет заготовленных сообщений в папке message")
            return None
        logger.info("⛔ Проверка папки с сообщениями для автоответчика")
        if not find_filess(directory_path="user_data/answering_machine", extension=self.file_extension):
            logger.error('⛔ Нет заготовленных сообщений для автоответчика в папке answering_machine')
            await show_notification(page,
                                    "⛔ Нет заготовленных сообщений для автоответчика в папке answering_machine")
            return None
        if len(await db_handler.open_db_func_lim(table_name="writing_group_links",
                                                 account_limit=ConfigReader().get_limits())) == 0:
            logger.error('⛔ Не сформирован список для рассылки по чатам')
            await show_notification(page, "⛔ Не сформирован список для рассылки по чатам")
            return None
