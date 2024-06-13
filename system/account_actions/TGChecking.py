from loguru import logger
from telethon import TelegramClient
from telethon.errors import AuthKeyDuplicatedError

from system.account_actions.TGConnect import TGConnect
from system.auxiliary_functions.auxiliary_functions import find_files
from system.auxiliary_functions.global_variables import ConfigReader
from system.sqlite_working_tools.sqlite_working_tools import DatabaseHandler
from system.telegram_actions.telegram_actions import working_with_accounts


async def account_verification_for_inviting(directory_path, extension) -> None:
    """Проверка аккаунтов для инвайтинга"""

    logger.info(f"Запуск проверки аккаунтов для инвайтинга")
    account_verification = AccountVerification()
    tg_connect = TGConnect()

    """Очистка базы данных"""
    await account_verification.cleaning_the_database_from_accounts()

    """Сканирование каталога с аккаунтами"""
    records = await account_verification.scanning_the_folder_with_accounts_for_telegram_accounts(directory_path,
                                                                                                 extension)
    logger.info(f"{records}")
    for entities in records:
        logger.info(f"{entities[0]}")
        await account_verification.write_account_data_to_the_database(entities)

    """Проверка аккаунтов"""
    accounts = await account_verification.getting_accounts_from_the_database_for_inviting()
    for account in accounts:
        logger.info(f"{account[0]}")
        proxy = await tg_connect.reading_proxies_from_the_database()
        await account_verification.account_verification_for_inviting(directory_path, account[0], proxy)

    logger.info(f"Окончание проверки аккаунтов для инвайтинга")


class AccountVerification:
    """Проверка аккаунтов Telegram"""

    def __init__(self):
        self.db_handler = DatabaseHandler()
        self.config_reader = ConfigReader()
        self.api_id_api_hash = self.config_reader.get_api_id_data_api_hash_data()

    async def cleaning_the_database_from_accounts(self) -> None:
        """Подключение к телеграм аккаунту для инвайтинга"""
        logger.info("Очистка базы данных")
        await self.db_handler.cleaning_db(name_database_table="config")

    async def scanning_the_folder_with_accounts_for_telegram_accounts(self, directory_path, extension) -> list:
        """Сканирование в папку с аккаунтами телеграм аккаунтов"""
        logger.info("Сканирование папки с аккаунтами на наличие аккаунтов Telegram")
        entities = find_files(directory_path, extension)
        logger.info(f"Найденные аккаунты:  {entities}")
        return entities

    async def write_account_data_to_the_database(self, entities) -> None:
        """Получение списка аккаунтов и записываем в базу данных"""
        logger.info(f"Записываем данные аккаунта {entities} в базу данных")
        await self.db_handler.write_data_to_db(creating_a_table="CREATE TABLE IF NOT EXISTS config(phone)",
                                               writing_data_to_a_table="INSERT INTO config (phone) VALUES (?)",
                                               entities=entities)

    async def getting_accounts_from_the_database_for_inviting(self) -> list:
        accounts: list = await self.db_handler.open_and_read_data("config")
        logger.info(f"Всего accounts: {len(accounts)}")
        return accounts

    async def account_verification_for_inviting(self, directory_path, session, proxy) -> None:
        """Проверка и сортировка аккаунтов"""
        api_id = self.api_id_api_hash[0]
        api_hash = self.api_id_api_hash[1]
        logger.info(f"Всего api_id_data: api_id {api_id}, api_hash {api_hash}")
        client = TelegramClient(f"{directory_path}/{session}", api_id=api_id, api_hash=api_hash,
                                system_version="4.16.30-vxCUSTOM", proxy=proxy)
        try:
            await client.connect()  # Подсоединяемся к Telegram аккаунта
            await client.disconnect()  # Отсоединяемся от Telegram аккаунта
        except AuthKeyDuplicatedError:  # На данный момент аккаунт запущен под другим ip
            logger.info(f"На данный момент аккаунт {session.split('/')[-1]} запущен под другим ip")
            await client.disconnect()  # Отключаемся от аккаунта, что бы session файл не был занят другим процессом
            working_with_accounts(account_folder=f"{directory_path}/{session.split('/')[-1]}.session",
                                  new_account_folder=f"user_settings/accounts/invalid_account/{session.split('/')[-1]}.session")
