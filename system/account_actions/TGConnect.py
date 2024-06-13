# -*- coding: utf-8 -*-
from loguru import logger
from telethon.sync import TelegramClient

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
        try:
            client = TelegramClient(f"{directory_path}/{session}", api_id=api_id, api_hash=api_hash,
                                    system_version="4.16.30-vxCUSTOM", proxy=proxy)
            return client  # Подсоединяемся к Telegram аккаунта
        except Exception as error:
            logger.error(f"Ошибка аккаунта {error}")



