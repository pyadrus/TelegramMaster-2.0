import time

from loguru import logger
from telethon.errors import AuthKeyDuplicatedError, PeerFloodError, FloodWaitError, UserPrivacyRestrictedError, \
    UserChannelsTooMuchError, UserBannedInChannelError, ChatWriteForbiddenError, BotGroupsBlockedError, \
    UserNotMutualContactError, ChatAdminRequiredError, UserKickedError, ChannelPrivateError, UserIdInvalidError, \
    UsernameNotOccupiedError, UsernameInvalidError, InviteRequestSentError, TypeNotFoundError
from telethon.sync import TelegramClient
from telethon.tl.functions.channels import InviteToChannelRequest

from system.account_actions.subscription.subscription import subscribe_to_group_or_channel
from system.account_actions.unsubscribe.unsubscribe import unsubscribe_from_the_group
from system.auxiliary_functions.auxiliary_functions import find_files, record_and_interrupt, record_inviting_results
from system.auxiliary_functions.global_variables import ConfigReader
from system.proxy.checking_proxy import reading_proxy_data_from_the_database
from system.sqlite_working_tools.sqlite_working_tools import DatabaseHandler
from system.telegram_actions.telegram_actions import working_with_accounts


class INVITING_TO_A_GROUP:
    def __init__(self):
        self.db_handler = DatabaseHandler()
        self.directory_path = "user_settings/accounts/inviting"
        self.extension = "session"
        self.config_reader = ConfigReader()
        self.api_id_api_hash = self.config_reader.get_api_id_data_api_hash_data()
        self.time_inviting = self.config_reader.get_time_inviting()

    async def cleaning_the_database_from_accounts(self) -> None:
        """Подключение к телеграм аккаунту для инвайтинга"""
        logger.info("Очистка базы данных")
        await self.db_handler.cleaning_db(name_database_table="config")

    async def scanning_the_folder_with_accounts_for_telegram_accounts(self) -> list:
        """Сканирование в папку с аккаунтами телеграм аккаунтов"""
        logger.info("Сканирование папки с аккаунтами на наличие аккаунтов Telegram")
        entities = find_files(self.directory_path, self.extension)
        logger.info(f"Найденные аккаунты:  {entities}")
        return entities

    async def write_account_data_to_the_database(self, entities) -> None:
        """Получение списка аккаунтов и записываем в базу данных"""
        logger.info(f"Записываем данные аккаунта {entities} в базу данных")
        await self.db_handler.write_data_to_db(creating_a_table="CREATE TABLE IF NOT EXISTS config(phone)",
                                               writing_data_to_a_table="INSERT INTO config (phone) VALUES (?)",
                                               entities=entities)

    async def reading_proxies_from_the_database(self) -> None:
        """Чтение списка прокси с базы данных"""
        logger.info("Получение прокси из базы данных")
        proxy = await reading_proxy_data_from_the_database(self.db_handler)  # Proxy IPV6 - НЕ РАБОТАЮТ
        return proxy

    async def getting_accounts_from_the_database_for_inviting(self) -> list:
        accounts: list = await self.db_handler.open_and_read_data("config")
        logger.info(f"Всего accounts: {len(accounts)}")
        return accounts

    async def account_verification_for_inviting(self, session, proxy) -> None:
        """Проверка и сортировка аккаунтов"""
        api_id = self.api_id_api_hash[0]
        api_hash = self.api_id_api_hash[1]
        logger.info(f"Всего api_id_data: api_id {api_id}, api_hash {api_hash}")
        client = TelegramClient(f"{self.directory_path}/{session}", api_id=api_id, api_hash=api_hash,
                                system_version="4.16.30-vxCUSTOM", proxy=proxy)
        try:
            await client.connect()  # Подсоединяемся к Telegram аккаунта
            await client.disconnect()  # Отсоединяемся от Telegram аккаунта
        except AuthKeyDuplicatedError:  # На данный момент аккаунт запущен под другим ip
            logger.info(f"На данный момент аккаунт {session.split('/')[-1]} запущен под другим ip")
            await client.disconnect()  # Отключаемся от аккаунта, что бы session файл не был занят другим процессом
            working_with_accounts(account_folder=f"{self.directory_path}/{session.split('/')[-1]}.session",
                                  new_account_folder=f"user_settings/accounts/invalid_account/{session.split('/')[-1]}.session")

    async def reading_the_list_of_accounts_from_the_database(self) -> None:
        """Inviting по заранее parsing списку и работа с несколькими аккаунтами"""
        accounts: list = await self.db_handler.open_and_read_data("config")
        logger.info(f"Всего accounts: {len(accounts)}")
        return accounts

    async def getting_an_invitation_link_from_the_database(self):
        """"Получение ссылки для инвайтинга"""
        links_inviting: list = await self.db_handler.open_and_read_data("links_inviting")  # Открываем базу данных
        logger.info(f"Ссылка для инвайтинга:  {links_inviting}")
        return links_inviting

    async def connecting_to_telegram_for_inviting(self, session, proxy):
        """Подключение к Telegram"""
        api_id = self.api_id_api_hash[0]
        api_hash = self.api_id_api_hash[1]
        logger.info(f"Всего api_id_data: api_id {api_id}, api_hash {api_hash}")
        try:
            client = TelegramClient(f"{self.directory_path}/{session}", api_id=api_id, api_hash=api_hash,
                                    system_version="4.16.30-vxCUSTOM", proxy=proxy)
            return client  # Подсоединяемся к Telegram аккаунта
        except Exception as error:
            logger.error(f"Ошибка аккаунта {error}")

    async def subscription_to_group_for_inviting(self, client, link_row) -> None:
        """Подписка на группу"""
        await subscribe_to_group_or_channel(client, link_row[0])

    async def getting_a_list_of_usernames_from_the_database(self):
        """Получение списка пользователей из базы данных"""
        number_usernames: list = await self.db_handler.open_and_read_data(table_name="members")  # Открываем базу данных
        logger.info(f"Всего username: {len(number_usernames)}")
        return number_usernames

    async def inviting_to_a_group_according_to_the_received_list(self, client, link_row, username) -> None:

        logger.error(f"Попытка приглашения {username[0]} в группу {link_row[0]}.")
        await client(InviteToChannelRequest(link_row[0], [username[0]]))
        logger.info(f'Удачно! Спим 5 секунд')
        time.sleep(5)

    async def unsubscribing_from_group_for_inviting(self, client, link_row):
        """Отписка от группы"""
        await unsubscribe_from_the_group(client, link_row[0])  # Отписка из группы
        await client.disconnect()  # Разрываем соединение telegram telegram telegram
