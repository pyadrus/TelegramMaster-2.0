# -*- coding: utf-8 -*-
import asyncio
import random

import flet as ft
from loguru import logger
from telethon import functions, types

from src.core.configs import path_accounts_folder
from src.core.sqlite_working_tools import add_member_to_db
from src.core.utils import find_filess
from src.features.account.TGConnect import TGConnect
from src.features.account.parsing.parsing import UserInfo
from src.gui.gui import log_and_display
from src.locales.translations_loader import translations


class TGContact:
    """
    Работа с контактами Telegram
    """

    def __init__(self, page):
        self.page = page
        self.tg_connect = TGConnect(page)

    async def show_account_contact_list(self) -> None:
        """
        Показать список контактов аккаунтов и запись результатов в файл
        """
        try:
            for session_name in find_filess(directory_path=path_accounts_folder, extension='session'):
                # Подключение к Telegram и вывод имя аккаунта в консоль / терминал
                client = await self.tg_connect.get_telegram_client(session_name,
                                                                   account_directory=path_accounts_folder)
                await self.parsing_and_recording_contacts_in_the_database(client, self.page)
                client.disconnect()  # Разрываем соединение telegram
        except Exception as error:
            logger.exception(error)

    async def parsing_and_recording_contacts_in_the_database(self, client) -> None:
        """
        Парсинг и запись контактов в базу данных

        :param client: Телеграм клиент
        """
        try:
            entities: list = []  # Создаем список сущностей
            for contact in await self.get_and_parse_contacts(client, self.page):  # Выводим результат parsing
                await self.get_user_data(contact, entities)
            await write_parsed_chat_participants_to_db(entities)
        except Exception as error:
            logger.exception(error)

    async def we_get_the_account_id(self, client, page: ft.Page) -> None:
        """
        Получаем id аккаунта

        :param client: Телеграм клиент
        :param page: Страница интерфейса
        """
        try:
            entities: list = []  # Создаем список сущностей
            for user in await self.get_and_parse_contacts(client, page):  # Выводим результат parsing
                await self.get_user_data(user, entities)
                await self.we_show_and_delete_the_contact_of_the_phone_book(client, user, page)
            await write_parsed_chat_participants_to_db(entities)
        except Exception as error:
            logger.exception(error)

    @staticmethod
    async def get_and_parse_contacts(client, page: ft.Page):
        """
        Получаем контакты

        :param client: Телеграм клиент
        :param page: Страница интерфейса
        """
        try:
            all_participants: list = []
            result = await client(functions.contacts.GetContactsRequest(hash=0))
            await log_and_display(f"{result}", page)
            all_participants.extend(result.users)
            return all_participants
        except Exception as error:
            logger.exception(error)
            return None

    async def we_show_and_delete_the_contact_of_the_phone_book(self, client, user) -> None:
        """
        Показываем и удаляем контакт телефонной книги

        :param client: Телеграм клиент
        :param user: Телеграм пользователя
        """
        try:
            await client(functions.contacts.DeleteContactsRequest(id=[await UserInfo().get_user_id(user)]))
            await log_and_display(f"Подождите 2 - 4 секунды", self.page)
            await asyncio.sleep(random.randrange(2, 3, 4))  # Спим для избежания ошибки о flood
        except Exception as error:
            logger.exception(error)

    async def delete_contact(self) -> None:
        """
        Удаляем контакты с аккаунтов
        """
        try:
            for session_name in find_filess(directory_path=path_accounts_folder, extension='session'):
                # Подключение к Telegram и вывод имя аккаунта в консоль / терминал
                client = await self.tg_connect.get_telegram_client(session_name,
                                                                   account_directory=path_accounts_folder)
                await self.we_get_the_account_id(client, self.page)
                client.disconnect()  # Разрываем соединение telegram
        except Exception as error:
            logger.exception(error)

    async def inviting_contact(self) -> None:
        """
        Добавление данных в телефонную книгу с последующим формированием списка software_database.db, для inviting
        """
        try:
            # Открываем базу данных для работы с аккаунтами user_data/software_database.db
            for session_name in find_filess(directory_path=path_accounts_folder, extension='session'):
                # Подключение к Telegram и вывод имя аккаунта в консоль / терминал
                client = await self.tg_connect.get_telegram_client(session_name,
                                                                   account_directory=path_accounts_folder)
                await self.add_contact_to_phone_book(client, self.page)
        except Exception as error:
            logger.exception(error)

    async def add_contact_to_phone_book(self, client) -> None:
        """
        Добавляем контакт в телефонную книгу

        :param client: Телеграм клиент
        """
        try:
            records: list = await open_and_read_data(table_name="contact", page=self.page)
            await log_and_display(f"Всего номеров: {len(records)}", self.page)
            entities: list = []  # Создаем список сущностей
            for rows in records:
                user = {"phone": rows[0]}
                phone = user["phone"]
                # Добавляем контакт в телефонную книгу
                await client(functions.contacts.ImportContactsRequest(contacts=[types.InputPhoneContact(client_id=0,
                                                                                                        phone=phone,
                                                                                                        first_name="Номер",
                                                                                                        last_name=phone)]))
                try:
                    # Получаем данные номера телефона https://docs.telethon.dev/en/stable/concepts/entities.html
                    contact = await client.get_entity(phone)
                    await self.get_user_data(contact, entities)
                    await log_and_display(f"[+] Контакт с добавлен в телефонную книгу!", self.page)
                    await asyncio.sleep(4)
                    # Запись результатов parsing в файл members_contacts.db, для дальнейшего inviting
                    # После работы с номером телефона, программа удаляет номер со списка
                    await delete_row_db(table="contact", column="phone", value=user["phone"])
                except ValueError:
                    await log_and_display(translations["ru"]["errors"]["contact_not_registered_or_cannot_add"], self.page)
                    # После работы с номером телефона, программа удаляет номер со списка
                    await delete_row_db(table="contact", column="phone", value=user["phone"])
            client.disconnect()  # Разрываем соединение telegram
            add_member_to_db(entities)  # Запись должна быть в таблицу members
        except Exception as error:
            logger.exception(error)

    @staticmethod
    async def get_user_data(user, entities) -> None:
        """
        Получаем данные пользователя

        :param user: Телеграм пользователя
        :param entities: Список сущностей
        """
        try:
            entities.append(
                [await UserInfo().get_username(user), await UserInfo().get_user_id(user),
                 await UserInfo().get_access_hash(user),
                 await UserInfo().get_first_name(user), await UserInfo().get_last_name(user),
                 await UserInfo().get_user_phone(user),
                 await UserInfo().get_user_online_status(user),
                 await UserInfo().get_photo_status(user),
                 await UserInfo().get_user_premium_status(user)])
        except Exception as error:
            logger.exception(error)
