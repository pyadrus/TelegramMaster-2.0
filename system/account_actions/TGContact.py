# -*- coding: utf-8 -*-
import random
import time

from loguru import logger
from telethon import functions
from telethon import types
from telethon.tl.types import UserStatusRecently, UserStatusOffline, UserStatusLastWeek, UserStatusLastMonth, \
    UserStatusOnline, UserStatusEmpty

from system.account_actions.TGConnect import TGConnect
from system.auxiliary_functions.global_variables import ConfigReader
from system.sqlite_working_tools.sqlite_working_tools import DatabaseHandler


class TGContact:
    """Работа с контактами Telegram"""

    def __init__(self):
        self.db_handler = DatabaseHandler()
        self.tg_connect = TGConnect()
        self.config_reader = ConfigReader()

    async def connect_to_telegram(self, file):
        """
        Подключение к Telegram, используя файл session.
        :param file: Имя файла с которым будем работать
        """
        logger.info(f"{file[0]}")
        proxy = await self.tg_connect.reading_proxies_from_the_database()
        client = await self.tg_connect.connecting_to_telegram(file[0], proxy, "user_settings/accounts/parsing")
        await client.connect()
        return client

    async def show_account_contact_list(self) -> None:
        """Показать список контактов аккаунтов и запись результатов в файл"""
        # Открываем базу данных для работы с аккаунтами user_settings/software_database.db
        records: list = await self.db_handler.open_and_read_data("config")
        for row in records:
            # Подключение к Telegram и вывод имя аккаунта в консоль / терминал
            # client, phone = telegram_connect_and_output_name(row, db_handler)
            await self.parsing_and_recording_contacts_in_the_database(client)
            client.disconnect()  # Разрываем соединение telegram

    async def parsing_and_recording_contacts_in_the_database(self, client) -> None:
        """Парсинг и запись контактов в базу данных"""
        entities: list = []  # Создаем список сущностей
        all_participants = await self.get_and_parse_contacts(client)
        for contact in all_participants:  # Выводим результат parsing
            await self.get_user_data(contact, entities)
        await self.db_handler.write_parsed_chat_participants_to_db(entities)

    async def we_get_the_account_id(self, client) -> None:
        """Получаем id аккаунта"""
        entities: list = []  # Создаем список сущностей
        all_participants = await self.get_and_parse_contacts(client)
        for user in all_participants:  # Выводим результат parsing
            await self.get_user_data(user, entities)
            await self.we_show_and_delete_the_contact_of_the_phone_book(client, user)
        await self.db_handler.write_parsed_chat_participants_to_db(entities)

    async def get_and_parse_contacts(self, client) -> list:
        all_participants: list = []
        result = client(functions.contacts.GetContactsRequest(hash=0))
        logger.info(result)  # Печатаем результат
        all_participants.extend(result.users)
        return all_participants

    async def we_show_and_delete_the_contact_of_the_phone_book(self, client, user) -> None:
        """Показываем и удаляем контакт телефонной книги"""
        client(functions.contacts.DeleteContactsRequest(id=[user.id]))
        logger.info("Подождите 2 - 4 секунды")
        time.sleep(random.randrange(2, 3, 4))  # Спим для избежания ошибки о flood

    async def delete_contact(self) -> None:
        """Удаляем контакты с аккаунтов"""
        records: list = await self.db_handler.open_and_read_data("config")
        for row in records:
            # Подключение к Telegram и вывод имя аккаунта в консоль / терминал
            # client, phone = await telegram_connect_and_output_name(row, db_handler)
            await self.we_get_the_account_id(client)
            client.disconnect()  # Разрываем соединение telegram

    async def inviting_contact(self) -> None:
        """Добавление данных в телефонную книгу с последующим формированием списка software_database.db, для inviting"""
        # Открываем базу данных для работы с аккаунтами user_settings/software_database.db
        records: list = await self.db_handler.open_and_read_data("config")
        logger.info(f"Всего accounts: {len(records)}")
        for row in records:
            # Подключение к Telegram и вывод имя аккаунта в консоль / терминал
            # client, phone = await telegram_connect_and_output_name(row, db_handler)
            await self.adding_a_contact_to_the_phone_book(client)

    async def adding_a_contact_to_the_phone_book(self, client) -> None:
        """Добавляем контакт в телефонную книгу"""
        records: list = await self.db_handler.open_and_read_data("contact")
        logger.info(f"Всего номеров: {len(records)}")
        entities: list = []  # Создаем список сущностей
        for rows in records:
            user = {"phone": rows[0]}
            phone = user["phone"]
            # Добавляем контакт в телефонную книгу
            client(functions.contacts.ImportContactsRequest(contacts=[types.InputPhoneContact(client_id=0,
                                                                                              phone=phone,
                                                                                              first_name="Номер",
                                                                                              last_name=phone)]))
            try:
                # Получаем данные номера телефона https://docs.telethon.dev/en/stable/concepts/entities.html
                contact = client.get_entity(phone)
                await self.get_user_data(contact, entities)
                logger.info(f"[+] Контакт с добавлен в телефонную книгу!")
                time.sleep(4)
                # Запись результатов parsing в файл members_contacts.db, для дальнейшего inviting
                # После работы с номером телефона, программа удаляет номер со списка
                await self.db_handler.delete_row_db(table="contact", column="phone", value=user["phone"])
            except ValueError:
                logger.info(
                    f"[+] Контакт с номером {phone} не зарегистрирован или отсутствует возможность добавить в телефонную книгу!")
                # После работы с номером телефона, программа удаляет номер со списка
                await self.db_handler.delete_row_db(table="contact", column="phone", value=user["phone"])
        client.disconnect()  # Разрываем соединение telegram
        await self.db_handler.write_parsed_chat_participants_to_db(entities)
        await self.db_handler.clean_no_username()  # Чистка списка parsing списка, если нет username

    async def get_user_data(self, user, entities) -> None:
        """Получаем данные пользователя"""
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

    async def add_contact_to_phone_book(self, client) -> None:
        """Добавляем контакт в телефонную книгу"""
        records: list = await self.db_handler.open_and_read_data("contact")
        logger.info(f"Всего номеров: {len(records)}")
        entities: list = []  # Создаем список сущностей
        for rows in records:
            user = {"phone": rows[0]}
            phone = user["phone"]
            # Добавляем контакт в телефонную книгу
            client(functions.contacts.ImportContactsRequest(contacts=[types.InputPhoneContact(client_id=0,
                                                                                              phone=phone,
                                                                                              first_name="Номер",
                                                                                              last_name=phone)]))
            try:
                # Получаем данные номера телефона https://docs.telethon.dev/en/stable/concepts/entities.html
                contact = client.get_entity(phone)
                await self.get_user_data(contact, entities)
                logger.info(f"[+] Контакт с добавлен в телефонную книгу!")
                time.sleep(4)
                # Запись результатов parsing в файл members_contacts.db, для дальнейшего inviting
                # После работы с номером телефона, программа удаляет номер со списка
                await self.db_handler.delete_row_db(table="contact", column="phone", value=user["phone"])
            except ValueError:
                logger.info(f"[+] Контакт с номером {phone} не зарегистрирован или отсутствует возможность добавить в телефонную книгу!")
                # После работы с номером телефона, программа удаляет номер со списка
                await self.db_handler.delete_row_db(table="contact", column="phone", value=user["phone"])
        client.disconnect()  # Разрываем соединение telegram
        await self.db_handler.write_parsed_chat_participants_to_db(entities)
        await self.db_handler.clean_no_username()  # Чистка списка parsing списка, если нет username
