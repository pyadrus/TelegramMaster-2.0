import time

from loguru import logger
from telethon.errors import AuthKeyDuplicatedError, PeerFloodError, FloodWaitError, UserPrivacyRestrictedError, \
    UserChannelsTooMuchError, BotGroupsBlockedError, ChatWriteForbiddenError, UserBannedInChannelError, \
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


class AccountVerification:
    """Проверка аккаунтов Telegram"""

    def __init__(self):
        self.db_handler = DatabaseHandler()
        self.directory_path = "user_settings/accounts/inviting"
        self.extension = "session"
        self.config_reader = ConfigReader()
        self.api_id_api_hash = self.config_reader.get_api_id_data_api_hash_data()

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


async def account_verification_for_inviting() -> None:
    """Проверка аккаунтов для инвайтинга"""

    logger.info(f"Запуск проверки аккаунтов для инвайтинга")
    inviting_to_a_group = InvitingToAGroup()
    account_verification = AccountVerification()

    """Очистка базы данных"""
    await account_verification.cleaning_the_database_from_accounts()

    """Сканирование каталога с аккаунтами"""
    records = await account_verification.scanning_the_folder_with_accounts_for_telegram_accounts()
    logger.info(f"{records}")
    for entities in records:
        logger.info(f"{entities[0]}")
        await account_verification.write_account_data_to_the_database(entities)

    """Проверка аккаунтов"""
    accounts = await account_verification.getting_accounts_from_the_database_for_inviting()
    for account in accounts:
        logger.info(f"{account[0]}")
        proxy = await inviting_to_a_group.reading_proxies_from_the_database()
        await account_verification.account_verification_for_inviting(account[0], proxy)

    logger.info(f"Окончание проверки аккаунтов для инвайтинга")


class SettingLimits:
    """Лимиты на действия TelegramMaster"""

    def __init__(self):
        self.db_handler = DatabaseHandler()
        self.config_reader = ConfigReader()
        self.account_limits = self.config_reader.get_limits()
        self.account_limits_none = None

    async def get_usernames_with_limits(self, table_name):
        """Получение списка пользователей из базы данных с учетом лимитов"""
        logger.info(f"Лимит на аккаунт: {self.account_limits}")
        number_usernames = await self.db_handler.open_db_func_lim(table_name=table_name,
                                                                  account_limit=self.account_limits)
        logger.info(f"Всего username: {len(number_usernames)}")
        return number_usernames

    async def get_usernames_without_limits(self, table_name):
        """Получение списка пользователей из базы данных без учета лимитов"""
        logger.info(f"Лимит на аккаунт (без ограничений)")
        number_usernames = await self.db_handler.open_db_func_lim(table_name=table_name,
                                                                  account_limit=self.account_limits_none)
        logger.info(f"Всего username: {len(number_usernames)}")
        return number_usernames


async def inviting_with_limits() -> None:
    """Инвайтинг с лимитами на аккаунт"""
    logger.info(f"Запуск инвайтинга с лимитами")

    inviting_to_a_group = InvitingToAGroup()
    inviting_with_limits_class = SettingLimits()
    accounts = await inviting_to_a_group.reading_the_list_of_accounts_from_the_database()
    for account in accounts:
        logger.info(f"{account[0]}")

        """Получение ссылки для инвайтинга"""
        links_inviting = await inviting_to_a_group.getting_an_invitation_link_from_the_database()
        for link in links_inviting:
            logger.info(f"{link[0]}")
            proxy = await inviting_to_a_group.reading_proxies_from_the_database()
            client = await inviting_to_a_group.connecting_to_telegram_for_inviting(account[0], proxy)
            await client.connect()

            """Подписка на группу для инвайтинга"""
            await subscribe_to_group_or_channel(client, link[0])

            """Получение списка usernames"""
            number_usernames = await inviting_with_limits_class.get_usernames_with_limits(table_name="members")

            logger.info(f"{number_usernames}")
            for username in number_usernames:
                logger.info(f"Пользователь username:{username[0]}")

                """Инвайтинг в группу по полученному списку"""
                config_reader = ConfigReader()
                time_inviting = config_reader.get_time_inviting()
                time_inviting_1 = time_inviting[0]
                time_inviting_2 = time_inviting[1]
                try:
                    await inviting_to_a_group.inviting_to_a_group_according_to_the_received_list(client, link,
                                                                                                 username)

                except PeerFloodError:
                    logger.error(f"Попытка приглашения {username} в группу {link[0]}. Настройки "
                                 f"конфиденциальности {username} не позволяют вам inviting")
                    record_and_interrupt(time_inviting_1, time_inviting_2)
                    break  # Прерываем работу и меняем аккаунт
                except AuthKeyDuplicatedError:
                    record_and_interrupt(time_inviting_1, time_inviting_2)
                    break  # Прерываем работу и меняем аккаунт
                except FloodWaitError as error:
                    logger.error(f'{error}')
                    record_and_interrupt(time_inviting_1, time_inviting_2)
                    break  # Прерываем работу и меняем аккаунт
                except UserPrivacyRestrictedError:
                    logger.error(
                        f"Попытка приглашения {username} в группу {link[0]}. Настройки конфиденциальности "
                        f"{username} не позволяют вам inviting")
                    await record_inviting_results(time_inviting_1, time_inviting_2, username)
                except UserChannelsTooMuchError:
                    logger.error(
                        f"Попытка приглашения {username} в группу {link[0]}. Превышен лимит у user каналов / "
                        f"супергрупп.")
                    await record_inviting_results(time_inviting_1, time_inviting_2, username)
                    continue
                except UserBannedInChannelError:
                    record_and_interrupt(time_inviting_1, time_inviting_2)
                    break  # Прерываем работу и меняем аккаунт
                except ChatWriteForbiddenError:
                    logger.error(f"Попытка приглашения {username} в группу {link[0]}. Настройки в чате не дают "
                                 f"добавлять людей в чат, возможно стоит бот админ и нужно подписаться на "
                                 f"другие проекты")
                    await record_inviting_results(time_inviting_1, time_inviting_2, username)
                    break  # Прерываем работу и меняем аккаунт
                except BotGroupsBlockedError:
                    logger.error(f"Попытка приглашения {username} в группу {link[0]}. Вы не можете добавить "
                                 f"бота в группу.")
                    await record_inviting_results(time_inviting_1, time_inviting_2, username)
                except UserNotMutualContactError:
                    logger.error(f"Попытка приглашения {username} в группу {link[0]}. User не является"
                                 f" взаимным контактом.")
                    await record_inviting_results(time_inviting_1, time_inviting_2, username)
                except ChatAdminRequiredError:
                    logger.error(f"Попытка приглашения {username} в группу {link[0]}. Требуются права "
                                 f"администратора.")
                    await record_inviting_results(time_inviting_1, time_inviting_2, username)
                except UserKickedError:
                    logger.error(f"Попытка приглашения {username} в группу {link[0]}. Пользователь был удален "
                                 f"ранее из супергруппы.")
                    await record_inviting_results(time_inviting_1, time_inviting_2, username)
                except ChannelPrivateError:
                    record_and_interrupt(time_inviting_1, time_inviting_2)
                    break  # Прерываем работу и меняем аккаунт
                except (UserIdInvalidError, UsernameNotOccupiedError, ValueError, UsernameInvalidError):
                    await record_inviting_results(time_inviting_1, time_inviting_2, username)
                    logger.error(f"Попытка приглашения {username} в группу {link[0]}. Не корректное имя "
                                 f"{username}")
                    break  # Прерываем работу и меняем аккаунт
                except (TypeError, UnboundLocalError):
                    logger.error(f"Попытка приглашения {username} в группу {link[0]}")
                    continue  # Записываем ошибку в software_database.db и продолжаем работу
                except InviteRequestSentError:
                    logger.error(f"Попытка приглашения {username} в группу {link[0]}. Доступ к функциям группы "
                                 f"станет возможен после утверждения заявки администратором на {link[0]}")
                    await record_inviting_results(time_inviting_1, time_inviting_2, username)
                    break  # Прерываем работу и меняем аккаунт
                except TypeNotFoundError:
                    record_and_interrupt(time_inviting_1, time_inviting_2)
                    break  # Прерываем работу и меняем аккаунт
                except KeyboardInterrupt:  # Закрытие окна программы
                    client.disconnect()  # Разрываем соединение telegram
                    logger.info("[!] Скрипт остановлен!")
                except Exception as error:
                    logger.error(f'{error}')  # Прерываем работу и меняем аккаунт
                else:
                    logger.info(f"[+] Участник {username} добавлен, если не состоит в чате {link[0]}")
                    await record_inviting_results(time_inviting_1, time_inviting_2, username)

            await inviting_to_a_group.unsubscribing_from_group_for_inviting(client, link)

    logger.info(f"Окончание  инвайтинга с лимитами")


async def inviting_without_limits() -> None:
    """Инвайтинг без лимитов"""
    logger.info(f"Запуск инвайтинга без лимитов")
    inviting_to_a_group = InvitingToAGroup()
    inviting_with_limits_class = SettingLimits()

    """Инвайтинг"""
    accounts = await inviting_to_a_group.reading_the_list_of_accounts_from_the_database()
    for account in accounts:
        logger.info(f"{account[0]}")

        """Получение ссылки для инвайтинга"""
        links_inviting = await inviting_to_a_group.getting_an_invitation_link_from_the_database()
        for link in links_inviting:
            logger.info(f"{link[0]}")
            proxy = await inviting_to_a_group.reading_proxies_from_the_database()
            client = await inviting_to_a_group.connecting_to_telegram_for_inviting(account[0], proxy)
            await client.connect()

            """Подписка на группу для инвайтинга"""
            await subscribe_to_group_or_channel(client, link[0])

            """Получение списка usernames"""
            number_usernames = await inviting_with_limits_class.get_usernames_without_limits(table_name="members")
            for username in number_usernames:
                logger.info(f"Пользователь username:{username[0]}")

                """Инвайтинг в группу по полученному списку"""
                config_reader = ConfigReader()
                time_inviting = config_reader.get_time_inviting()
                time_inviting_1 = time_inviting[0]
                time_inviting_2 = time_inviting[1]
                try:
                    await inviting_to_a_group.inviting_to_a_group_according_to_the_received_list(client, link,
                                                                                                 username)

                except PeerFloodError:
                    logger.error(f"Попытка приглашения {username} в группу {link[0]}. Настройки "
                                 f"конфиденциальности {username} не позволяют вам inviting")
                    record_and_interrupt(time_inviting_1, time_inviting_2)
                    break  # Прерываем работу и меняем аккаунт
                except AuthKeyDuplicatedError:
                    record_and_interrupt(time_inviting_1, time_inviting_2)
                    break  # Прерываем работу и меняем аккаунт
                except FloodWaitError as error:
                    logger.error(f'{error}')
                    record_and_interrupt(time_inviting_1, time_inviting_2)
                    break  # Прерываем работу и меняем аккаунт
                except UserPrivacyRestrictedError:
                    logger.error(
                        f"Попытка приглашения {username} в группу {link[0]}. Настройки конфиденциальности "
                        f"{username} не позволяют вам inviting")
                    await record_inviting_results(time_inviting_1, time_inviting_2, username)
                except UserChannelsTooMuchError:
                    logger.error(
                        f"Попытка приглашения {username} в группу {link[0]}. Превышен лимит у user каналов / "
                        f"супергрупп.")
                    await record_inviting_results(time_inviting_1, time_inviting_2, username)
                    continue
                except UserBannedInChannelError:
                    record_and_interrupt(time_inviting_1, time_inviting_2)
                    break  # Прерываем работу и меняем аккаунт
                except ChatWriteForbiddenError:
                    logger.error(f"Попытка приглашения {username} в группу {link[0]}. Настройки в чате не дают "
                                 f"добавлять людей в чат, возможно стоит бот админ и нужно подписаться на "
                                 f"другие проекты")
                    await record_inviting_results(time_inviting_1, time_inviting_2, username)
                    break  # Прерываем работу и меняем аккаунт
                except BotGroupsBlockedError:
                    logger.error(f"Попытка приглашения {username} в группу {link[0]}. Вы не можете добавить "
                                 f"бота в группу.")
                    await record_inviting_results(time_inviting_1, time_inviting_2, username)
                except UserNotMutualContactError:
                    logger.error(f"Попытка приглашения {username} в группу {link[0]}. User не является"
                                 f" взаимным контактом.")
                    await record_inviting_results(time_inviting_1, time_inviting_2, username)
                except ChatAdminRequiredError:
                    logger.error(f"Попытка приглашения {username} в группу {link[0]}. Требуются права "
                                 f"администратора.")
                    await record_inviting_results(time_inviting_1, time_inviting_2, username)
                except UserKickedError:
                    logger.error(f"Попытка приглашения {username} в группу {link[0]}. Пользователь был удален "
                                 f"ранее из супергруппы.")
                    await record_inviting_results(time_inviting_1, time_inviting_2, username)
                except ChannelPrivateError:
                    record_and_interrupt(time_inviting_1, time_inviting_2)
                    break  # Прерываем работу и меняем аккаунт
                except (UserIdInvalidError, UsernameNotOccupiedError, ValueError, UsernameInvalidError):
                    await record_inviting_results(time_inviting_1, time_inviting_2, username)
                    logger.error(f"Попытка приглашения {username} в группу {link[0]}. Не корректное имя "
                                 f"{username}")
                    break  # Прерываем работу и меняем аккаунт
                except (TypeError, UnboundLocalError):
                    logger.error(f"Попытка приглашения {username} в группу {link[0]}")
                    continue  # Записываем ошибку в software_database.db и продолжаем работу
                except InviteRequestSentError:
                    logger.error(f"Попытка приглашения {username} в группу {link[0]}. Доступ к функциям группы "
                                 f"станет возможен после утверждения заявки администратором на {link[0]}")
                    await record_inviting_results(time_inviting_1, time_inviting_2, username)
                    break  # Прерываем работу и меняем аккаунт
                except TypeNotFoundError:
                    record_and_interrupt(time_inviting_1, time_inviting_2)
                    break  # Прерываем работу и меняем аккаунт
                except KeyboardInterrupt:  # Закрытие окна программы
                    client.disconnect()  # Разрываем соединение telegram
                    logger.info("[!] Скрипт остановлен!")
                except Exception as error:
                    logger.error(f'{error}')  # Прерываем работу и меняем аккаунт
                else:
                    logger.info(f"[+] Участник {username} добавлен, если не состоит в чате {link[0]}")
                    await record_inviting_results(time_inviting_1, time_inviting_2, username)

            await inviting_to_a_group.unsubscribing_from_group_for_inviting(client, link)
    logger.info("[!] Инвайтинг окончен!")


class InvitingToAGroup:
    def __init__(self):
        self.db_handler = DatabaseHandler()
        self.directory_path = "user_settings/accounts/inviting"
        self.extension = "session"
        self.config_reader = ConfigReader()
        self.api_id_api_hash = self.config_reader.get_api_id_data_api_hash_data()
        self.time_inviting = self.config_reader.get_time_inviting()

    async def reading_proxies_from_the_database(self) -> None:
        """Чтение списка прокси с базы данных"""
        logger.info("Получение прокси из базы данных")
        proxy = await reading_proxy_data_from_the_database(self.db_handler)  # Proxy IPV6 - НЕ РАБОТАЮТ
        return proxy

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

    async def inviting_to_a_group_according_to_the_received_list(self, client, link_row, username) -> None:

        logger.error(f"Попытка приглашения {username[0]} в группу {link_row[0]}.")
        await client(InviteToChannelRequest(link_row[0], [username[0]]))
        logger.info(f'Удачно! Спим 5 секунд')
        time.sleep(5)

    async def unsubscribing_from_group_for_inviting(self, client, link_row):
        """Отписка от группы"""
        await unsubscribe_from_the_group(client, link_row[0])  # Отписка из группы
        await client.disconnect()  # Разрываем соединение telegram telegram telegram


if __name__ == "__main__":
    inviting_without_limits()
    account_verification_for_inviting()
    inviting_with_limits()
