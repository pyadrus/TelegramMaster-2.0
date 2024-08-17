# -*- coding: utf-8 -*-
from loguru import logger
from telethon.errors import SessionPasswordNeededError, ApiIdInvalidError, AuthKeyDuplicatedError
from telethon.sync import TelegramClient

from system.auxiliary_functions.auxiliary_functions import working_with_accounts
from system.auxiliary_functions.global_variables import ConfigReader
from system.proxy.checking_proxy import reading_proxy_data_from_the_database
from system.sqlite_working_tools.sqlite_working_tools import DatabaseHandler


class TGConnect:

    def __init__(self):
        self.db_handler = DatabaseHandler()
        self.config_reader = ConfigReader()
        self.api_id_api_hash = self.config_reader.get_api_id_data_api_hash_data()

    async def reading_proxies_from_the_database(self):
        """Чтение списка прокси с базы данных"""
        logger.info("Получение прокси из базы данных")
        proxy = await reading_proxy_data_from_the_database(self.db_handler)  # Proxy IPV6 - НЕ РАБОТАЮТ
        return proxy

    async def connecting_to_telegram(self, session, proxy, directory_path) -> TelegramClient:
        """
        Подключение к Telegram
        :param session: Имя сессии
        :param proxy: Прокси
        :param directory_path: Путь к директории
        :return TelegramClient: TelegramClient
        """
        api_id = self.api_id_api_hash[0]
        api_hash = self.api_id_api_hash[1]
        logger.info(f"Всего api_id_data: api_id {api_id}, api_hash {api_hash}")

        client = TelegramClient(f"{directory_path}/{session}", api_id=api_id, api_hash=api_hash,
                                system_version="4.16.30-vxCUSTOM", proxy=proxy)
        return client  # Подсоединяемся к Telegram аккаунта

    async def connect_to_telegram(self, file, directory_path):
        """Подключение к Telegram, используя файл session."""
        logger.info(f"Подключение к аккаунту: {directory_path}/{file[0]}") # Получаем имя файла сессии file[0] - session файл
        proxy = await self.reading_proxies_from_the_database()
        client = await self.connecting_to_telegram(file[0], proxy, directory_path)
        try:
            await client.connect()
            return client
        except AuthKeyDuplicatedError:
            await client.disconnect()  # Отключаемся от аккаунта, что бы session файл не был занят другим процессом
            logger.info(f"На данный момент аккаунт {file[0].split('/')[-1]} запущен под другим ip")
            working_with_accounts(account_folder=f"{directory_path}/{file[0].split('/')[-1]}.session",
                                  new_account_folder=f"user_settings/accounts/invalid_account/{file[0].split('/')[-1]}.session")

    async def telegram_connect(self):
        """Account telegram connect, с проверкой на валидность, если ранее не было соединения, то запрашиваем код"""
        logger.info("Подключение к Telegram. Введите номер телефона: ")
        phone = input(" ")
        proxy = await self.reading_proxies_from_the_database()
        client = await self.connecting_to_telegram(session=f"{phone}", proxy=proxy,
                                                   directory_path="user_settings/accounts")
        await client.connect()  # Подключаемся к Telegram
        if not await client.is_user_authorized():
            await client.send_code_request(phone)
            try:
                logger.info("[+] Введите код: ")
                phone_code = input(" ")
                # Если ранее аккаунт не подсоединялся, то просим ввести код подтверждения
                await client.sign_in(phone, code=phone_code)
            except SessionPasswordNeededError:
                """
                https://telethonn.readthedocs.io/en/latest/extra/basic/creating-a-client.html#two-factor-authorization-2fa
                """
                # Если аккаунт имеет password, то просим пользователя ввести пароль
                logger.info("Введите пароль для входа в аккаунт: ")
                password = input(" ")
                await client.sign_in(password=password)
            except ApiIdInvalidError:
                logger.info("[!] Не валидные api_id/api_hash")
        client.disconnect() # Отключаемся от Telegram
