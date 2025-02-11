# -*- coding: utf-8 -*-
import asyncio
import random
import flet as ft
from loguru import logger
from telethon import functions
from telethon import types
from telethon.tl.types import (UserStatusRecently, UserStatusOffline, UserStatusLastWeek, UserStatusLastMonth,
                               UserStatusOnline, UserStatusEmpty)

from src.features.account.TGConnect import TGConnect
from src.core.utils import find_filess
from src.core.configs import path_contact_folder
from src.core.sqlite_working_tools import DatabaseHandler


class TGContact:
    """
    Работа с контактами Telegram
    """

    def __init__(self):
        self.db_handler = DatabaseHandler()
        self.tg_connect = TGConnect()

    async def show_account_contact_list(self, page: ft.Page) -> None:
        """
        Показать список контактов аккаунтов и запись результатов в файл
        """
        try:
            for session_name in find_filess(directory_path=path_contact_folder, extension='session'):
                # Подключение к Telegram и вывод имя аккаунта в консоль / терминал
                client = await self.tg_connect.get_telegram_client(page, session_name,
                                                                   account_directory=path_contact_folder)
                await self.parsing_and_recording_contacts_in_the_database(client)
                client.disconnect()  # Разрываем соединение telegram
        except Exception as error:
            logger.exception(f"❌ Ошибка: {error}")

    async def parsing_and_recording_contacts_in_the_database(self, client) -> None:
        """
        Парсинг и запись контактов в базу данных

        :param client: Телеграм клиент
        """
        try:
            entities: list = []  # Создаем список сущностей
            for contact in await self.get_and_parse_contacts(client):  # Выводим результат parsing
                await self.get_user_data(contact, entities)
            await self.db_handler.write_parsed_chat_participants_to_db(entities)
        except Exception as error:
            logger.exception(f"❌ Ошибка: {error}")

    async def we_get_the_account_id(self, client) -> None:
        """
        Получаем id аккаунта

        :param client: Телеграм клиент
        """
        try:
            entities: list = []  # Создаем список сущностей
            for user in await self.get_and_parse_contacts(client):  # Выводим результат parsing
                await self.get_user_data(user, entities)
                await self.we_show_and_delete_the_contact_of_the_phone_book(client, user)
            await self.db_handler.write_parsed_chat_participants_to_db(entities)
        except Exception as error:
            logger.exception(f"❌ Ошибка: {error}")

    @staticmethod
    async def get_and_parse_contacts(client) -> list:
        """
        Получаем контакты

        :param client: Телеграм клиент
        """
        try:
            all_participants: list = []
            result = await client(functions.contacts.GetContactsRequest(hash=0))
            logger.info(result)  # Печатаем результат
            all_participants.extend(result.users)
            return all_participants
        except Exception as error:
            logger.exception(f"❌ Ошибка: {error}")

    @staticmethod
    async def we_show_and_delete_the_contact_of_the_phone_book(client, user) -> None:
        """
        Показываем и удаляем контакт телефонной книги

        :param client: Телеграм клиент
        :param user: Телеграм пользователя
        """
        try:
            await client(functions.contacts.DeleteContactsRequest(id=[user.id]))
            logger.info("Подождите 2 - 4 секунды")
            await asyncio.sleep(random.randrange(2, 3, 4))  # Спим для избежания ошибки о flood
        except Exception as error:
            logger.exception(f"❌ Ошибка: {error}")

    async def delete_contact(self, page) -> None:
        """
        Удаляем контакты с аккаунтов

        :param page: Страница интерфейса Flet для отображения элементов управления.
        """
        try:
            for session_name in find_filess(directory_path=path_contact_folder, extension='session'):
                # Подключение к Telegram и вывод имя аккаунта в консоль / терминал
                client = await self.tg_connect.get_telegram_client(page, session_name,
                                                                   account_directory=path_contact_folder)
                await self.we_get_the_account_id(client)
                client.disconnect()  # Разрываем соединение telegram
        except Exception as error:
            logger.exception(f"❌ Ошибка: {error}")

    async def inviting_contact(self, page) -> None:
        """
        Добавление данных в телефонную книгу с последующим формированием списка software_database.db, для inviting
        """
        try:
            # Открываем базу данных для работы с аккаунтами user_data/software_database.db
            for session_name in find_filess(directory_path=path_contact_folder, extension='session'):
                # Подключение к Telegram и вывод имя аккаунта в консоль / терминал
                client = await self.tg_connect.get_telegram_client(page, session_name,
                                                                   account_directory=path_contact_folder)
                await self.add_contact_to_phone_book(client)
        except Exception as error:
            logger.exception(f"❌ Ошибка: {error}")

    async def add_contact_to_phone_book(self, client) -> None:
        """
        Добавляем контакт в телефонную книгу

        :param client: Телеграм клиент
        """
        try:
            records: list = await self.db_handler.open_and_read_data("contact")
            logger.info(f"Всего номеров: {len(records)}")
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
                    logger.info(f"[+] Контакт с добавлен в телефонную книгу!")
                    await asyncio.sleep(4)
                    # Запись результатов parsing в файл members_contacts.db, для дальнейшего inviting
                    # После работы с номером телефона, программа удаляет номер со списка
                    await self.db_handler.delete_row_db(table="contact", column="phone", value=user["phone"])
                except ValueError:
                    logger.info(
                        f"❌ Контакт с номером {phone} не зарегистрирован или отсутствует возможность добавить в телефонную книгу!")
                    # После работы с номером телефона, программа удаляет номер со списка
                    await self.db_handler.delete_row_db(table="contact", column="phone", value=user["phone"])
            client.disconnect()  # Разрываем соединение telegram
            await self.db_handler.write_parsed_chat_participants_to_db(entities)
            await self.db_handler.remove_records_without_username()  # Чистка списка parsing списка, если нет username
        except Exception as error:
            logger.exception(f"❌ Ошибка: {error}")

    @staticmethod
    async def get_user_data(user, entities) -> None:
        """
        Получаем данные пользователя

        :param user: Телеграм пользователя
        :param entities: Список сущностей
        """
        try:
            username = user.username if user.username else "NONE"
            user_phone = user.phone if user.phone else "Номер телефона скрыт"
            first_name = user.first_name if user.first_name else ""
            last_name = user.last_name if user.last_name else ""
            photos_id = (
                "Пользователь с фото" if isinstance(user.photo, types.UserProfilePhoto) else "Пользователь без фото")
            online_at = "Был(а) недавно"
            # Статусы пользователя https://core.telegram.org/type/UserStatus
            if isinstance(user.status, (
                    UserStatusRecently, UserStatusOffline, UserStatusLastWeek, UserStatusLastMonth, UserStatusOnline,
                    UserStatusEmpty)):
                if isinstance(user.status, UserStatusOffline):
                    online_at = user.status.was_online
                if isinstance(user.status, UserStatusRecently):
                    online_at = "Был(а) недавно"
                if isinstance(user.status, UserStatusLastWeek):
                    online_at = "Был(а) на этой неделе"
                if isinstance(user.status, UserStatusLastMonth):
                    online_at = "Был(а) в этом месяце"
                if isinstance(user.status, UserStatusOnline):
                    online_at = user.status.expires
                if isinstance(user.status, UserStatusEmpty):
                    online_at = "статус пользователя еще не определен"
            user_premium = "Пользователь с premium" if user.premium else ""

            entities.append(
                [username, user.id, user.access_hash, first_name, last_name, user_phone, online_at, photos_id,
                 user_premium])
        except Exception as error:
            logger.exception(f"❌ Ошибка: {error}")
