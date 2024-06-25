# -*- coding: utf-8 -*-
import sqlite3
import time

from loguru import logger
from telethon import TelegramClient
from telethon.errors import AuthKeyDuplicatedError, PhoneNumberBannedError, UserDeactivatedBanError, TimedOutError, \
    AuthKeyNotFound

from system.account_actions.TGConnect import TGConnect
from system.auxiliary_functions.auxiliary_functions import find_files
from system.auxiliary_functions.global_variables import ConfigReader
from system.proxy.checking_proxy import checking_the_proxy_for_work
from system.telegram_actions.telegram_actions import working_with_accounts


async def account_verification_for_telegram(directory_path, extension) -> None:
    """Проверка аккаунтов Telegram"""

    logger.info(f"Запуск проверки аккаунтов Telegram")
    account_verification = AccountVerification()
    tg_connect = TGConnect()
    await checking_the_proxy_for_work()  # Проверка proxy

    """Сканирование каталога с аккаунтами"""
    records = await account_verification.scanning_the_folder_with_accounts_for_telegram_accounts(directory_path,
                                                                                                 extension)
    logger.info(f"{records}")
    for entities in records:
        logger.info(f"{entities[0]}")

        """Проверка аккаунтов"""
        proxy = await tg_connect.reading_proxies_from_the_database()
        await account_verification.account_verification(directory_path, entities[0], proxy)

    logger.info(f"Окончание проверки аккаунтов Telegram")


class AccountVerification:
    """Проверка аккаунтов Telegram"""

    def __init__(self):
        self.config_reader = ConfigReader()
        self.api_id_api_hash = self.config_reader.get_api_id_data_api_hash_data()

    async def scanning_the_folder_with_accounts_for_telegram_accounts(self, directory_path, extension) -> list:
        """Сканирование в папку с аккаунтами телеграм аккаунтов"""
        logger.info("Сканирование папки с аккаунтами на наличие аккаунтов Telegram")
        entities = find_files(directory_path, extension)
        logger.info(f"Найденные аккаунты:  {entities}")
        return entities

    async def account_verification(self, directory_path, session, proxy) -> None:
        """Проверка и сортировка аккаунтов"""
        logger.info("Проверка аккаунтов!")

        api_id = self.api_id_api_hash[0]
        api_hash = self.api_id_api_hash[1]
        logger.info(f"Всего api_id_data: api_id {api_id}, api_hash {api_hash}")
        client = TelegramClient(f"{directory_path}/{session}", api_id=api_id, api_hash=api_hash,
                                system_version="4.16.30-vxCUSTOM", proxy=proxy)
        try:
            await client.connect()  # Подсоединяемся к Telegram аккаунта
            if not await client.is_user_authorized():  # Если аккаунт не авторизирован, то удаляем сессию
                await client.disconnect()  # Разрываем соединение Telegram, для удаления session файла
                working_with_accounts(account_folder=f"{directory_path}/{session.split('/')[-1]}.session",
                                      new_account_folder=f"user_settings/accounts/invalid_account/{session.split('/')[-1]}.session")
                time.sleep(1)
                return  # Возвращаемся из функции, так как аккаунт не авторизован
            await client.disconnect()  # Отключаемся от аккаунта, что бы session файл не был занят другим процессом
        except AttributeError as e:
            logger.info(f"{e}")
        except (PhoneNumberBannedError, UserDeactivatedBanError, AuthKeyNotFound, sqlite3.DatabaseError):
            client.disconnect()  # Разрываем соединение Telegram, для удаления session файла
            logger.info(f"Битый файл или аккаунт забанен {session.split('/')[-1]}.session")
            working_with_accounts(account_folder=f"{directory_path}/{session.split('/')[-1]}.session",
                                  new_account_folder=f"user_settings/accounts/invalid_account/{session.split('/')[-1]}.session")
        except TimedOutError as e:
            logger.exception(e)
            time.sleep(2)
        except AuthKeyDuplicatedError:  # На данный момент аккаунт запущен под другим ip
            await client.disconnect()  # Отключаемся от аккаунта, что бы session файл не был занят другим процессом
            logger.info(f"На данный момент аккаунт {session.split('/')[-1]} запущен под другим ip")
            working_with_accounts(account_folder=f"{directory_path}/{session.split('/')[-1]}.session",
                                  new_account_folder=f"user_settings/accounts/invalid_account/{session.split('/')[-1]}.session")