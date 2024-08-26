# -*- coding: utf-8 -*-
import os
import os.path
import sqlite3
import time

from loguru import logger
from telethon import TelegramClient
from telethon.errors import (AuthKeyDuplicatedError, PhoneNumberBannedError, UserDeactivatedBanError, TimedOutError,
                             AuthKeyNotFound, TypeNotFoundError, AuthKeyUnregisteredError, SessionPasswordNeededError,
                             ApiIdInvalidError, YouBlockedUserError)
from telethon.tl.functions.users import GetFullUserRequest
from thefuzz import fuzz

from system.auxiliary_functions.auxiliary_functions import find_files, working_with_accounts
from system.auxiliary_functions.global_variables import ConfigReader
from system.proxy.checking_proxy import checking_the_proxy_for_work
from system.proxy.checking_proxy import reading_proxy_data_from_the_database
from system.sqlite_working_tools.sqlite_working_tools import DatabaseHandler


class TGConnect:

    def __init__(self):
        self.db_handler = DatabaseHandler()
        self.config_reader = ConfigReader()
        self.api_id_api_hash = self.config_reader.get_api_id_data_api_hash_data()
        self.api_id = self.api_id_api_hash[0]
        self.api_hash = self.api_id_api_hash[1]

    async def connect_to_telegram(self, session, account_directory) -> TelegramClient:
        """
        Создает клиент для подключения к Telegram.
        :param session: Имя сессии
        :param account_directory: Путь к директории
        :return TelegramClient: TelegramClient
        """
        logger.info(f"Используем API ID: {self.api_id}, API Hash: {self.api_hash}")
        proxy_settings = await reading_proxy_data_from_the_database(self.db_handler)  # Proxy IPV6 - НЕ РАБОТАЮТ
        telegram_client = TelegramClient(f"{account_directory}/{session}", api_id=self.api_id, api_hash=self.api_hash,
                                         system_version="4.16.30-vxCUSTOM", proxy=proxy_settings)
        return telegram_client

    async def verify_account(self, account_directory, session_name) -> None:
        """
        Проверяет и сортирует аккаунты.
        :param account_directory: Путь к каталогу с аккаунтами
        :param session_name: Имя аккаунта для проверки аккаунта
        """
        logger.info(f"Проверка аккаунта {session_name}. Используем API ID: {self.api_id}, API Hash: {self.api_hash}")
        telegram_client = await self.get_telegram_client(session_name[0], account_directory)
        try:
            await telegram_client.connect()  # Подсоединяемся к Telegram аккаунта
            if not await telegram_client.is_user_authorized():  # Если аккаунт не авторизирован, то удаляем сессию
                await telegram_client.disconnect()  # Разрываем соединение Telegram, для удаления session файла
                working_with_accounts(account_folder=f"{account_directory}/{session_name.split('/')[-1]}.session",
                                      new_account_folder=f"user_settings/accounts/invalid_account/{session_name.split('/')[-1]}.session")
                time.sleep(1)
                return  # Возвращаемся из функции, так как аккаунт не авторизован
            await telegram_client.disconnect()  # Отключаемся от аккаунта, что бы session файл не был занят другим процессом
        except AttributeError as e:
            logger.info(f"{e}")
        except (PhoneNumberBannedError, UserDeactivatedBanError, AuthKeyNotFound, sqlite3.DatabaseError,
                AuthKeyUnregisteredError, AuthKeyDuplicatedError):
            telegram_client.disconnect()  # Разрываем соединение Telegram, для удаления session файла
            logger.error(f"⛔ Битый файл или аккаунт забанен: {session_name.split('/')[-1]}.session. Возможно, запущен под другим IP")
            working_with_accounts(account_folder=f"{account_directory}/{session_name.split('/')[-1]}.session",
                                  new_account_folder=f"user_settings/accounts/invalid_account/{session_name.split('/')[-1]}.session")
        except TimedOutError as e:
            logger.exception(e)
            time.sleep(2)

    async def check_for_spam(self, folder_name) -> None:
        """
        Проверка аккаунта на спам через @SpamBot
        :param folder_name: папка с аккаунтами
        """
        session_files = find_files(directory_path=f"user_settings/accounts/{folder_name}", extension='session')
        for session_file in session_files:
            telegram_client = await self.get_telegram_client(session_file , account_directory=f"user_settings/accounts/{folder_name}")
            try:
                await telegram_client.send_message('SpamBot', '/start')  # Находим спам бот, и вводим команду /start
                messages = await telegram_client.get_messages('SpamBot')
                for message in messages:
                    logger.info(f"{session_file } {message.message}")
                    similarity_ratio_ru: int = fuzz.ratio(f"{message.message}",
                                                          "Очень жаль, что Вы с этим столкнулись. К сожалению, "
                                                          "иногда наша антиспам-система излишне сурово реагирует на "
                                                          "некоторые действия. Если Вы считаете, что Ваш аккаунт "
                                                          "ограничен по ошибке, пожалуйста, сообщите об этом нашим "
                                                          "модераторам. Пока действуют ограничения, Вы не сможете "
                                                          "писать тем, кто не сохранил Ваш номер в список контактов, "
                                                          "а также приглашать таких пользователей в группы или каналы. "
                                                          "Если пользователь написал Вам первым, Вы сможете ответить, "
                                                          "несмотря на ограничения.")
                    if similarity_ratio_ru >= 97:
                        logger.info('⛔ Аккаунт заблокирован')
                        await telegram_client.disconnect()  # Отключаемся от аккаунта, что бы session файл не был занят другим процессом
                        logger.info(f"Проверка аккаунтов через SpamBot. {session_file [0]}: {message.message}")
                        # Перенос Telegram аккаунта в папку banned, если Telegram аккаунт в бане
                        working_with_accounts(account_folder=f"user_settings/accounts/{folder_name}/{session_file [0]}.session",
                                              new_account_folder=f"user_settings/accounts/banned/{session_file [0]}.session")
                    similarity_ratio_en: int = fuzz.ratio(f"{message.message}",
                                                          "I’m very sorry that you had to contact me. Unfortunately, "
                                                          "some account_actions can trigger a harsh response from our "
                                                          "anti-spam systems. If you think your account was limited by "
                                                          "mistake, you can submit a complaint to our moderators. While "
                                                          "the account is limited, you will not be able to send messages "
                                                          "to people who do not have your number in their phone contacts "
                                                          "or add them to groups and channels. Of course, when people "
                                                          "contact you first, you can always reply to them.")
                    if similarity_ratio_en >= 97:
                        logger.info('⛔ Аккаунт заблокирован')
                        await telegram_client.disconnect()  # Отключаемся от аккаунта, что бы session файл не был занят другим процессом
                        logger.error(f"Проверка аккаунтов через SpamBot. {session_file [0]}: {message.message}")
                        # Перенос Telegram аккаунта в папку banned, если Telegram аккаунт в бане
                        logger.info(session_file [0])
                        working_with_accounts(account_folder=f"user_settings/accounts/{folder_name}/{session_file [0]}.session",
                                              new_account_folder=f"user_settings/accounts/banned/{session_file [0]}.session")
                    logger.error(f"Проверка аккаунтов через SpamBot. {session_file [0]}: {message.message}")
            except YouBlockedUserError:
                continue  # Записываем ошибку в software_database.db и продолжаем работу
            except (AttributeError, AuthKeyUnregisteredError) as e:
                logger.error(e)
                continue

    async def verify_all_accounts(self, account_directory, extension) -> None:
        """
        Проверяет все аккаунты Telegram в указанной директории.
        :param account_directory: Путь к каталогу с аккаунтами
        :param extension: Расширение файла с аккаунтами
        """
        logger.info(f"Запуск проверки аккаунтов Telegram из папки 📁: {account_directory}")
        await checking_the_proxy_for_work()  # Проверка proxy
        # Сканирование каталога с аккаунтами
        session_files = find_files(account_directory, extension)
        for session_file in session_files:
            logger.info(f"⚠️ Проверяемый аккаунт: {account_directory}/{session_file[0]}")
            # Проверка аккаунтов
            await self.verify_account(account_directory, session_file[0])
            # Получение данных аккаунта
            telegram_client = await self.get_telegram_client(file=session_file, account_directory=account_directory)
            try:
                first_name, last_name, phone_number = await self.get_account_details(telegram_client, account_name="me",
                                                                                     account_directory=account_directory,
                                                                                     session_name=session_file[0])
                # Выводим результат полученного имени и номера телефона
                logger.info(f"📔 Данные аккаунта: {first_name} {last_name} {phone_number}")
                # Переименовываем сессию
                await self.rename_session_file(telegram_client, session_file[0], phone_number, account_directory)
            except TypeError as e:
                logger.error(f"TypeError: {e}")  # Ошибка

        logger.info(f"Окончание проверки аккаунтов Telegram из папки 📁: {account_directory}")

    async def get_account_details(self, telegram_client, account_name, account_directory, session_name):
        """
        Получает информацию о Telegram аккаунте.
        :param telegram_client: Клиент для работы с Telegram
        :param account_name: Имя аккаунта для проверки аккаунта
        :param account_directory: Путь к файлу
        :param session_name: Имя session файла
        """
        try:
            full_user = await telegram_client(GetFullUserRequest(account_name))
            for user in full_user.users:
                first_name = user.first_name if user.first_name else ""
                last_name = user.last_name if user.last_name else ""
                phone_number = user.phone if user.phone else ""
                return first_name, last_name, phone_number
        except TypeNotFoundError:
            await telegram_client.disconnect()  # Разрываем соединение Telegram, для удаления session файла
            logger.error(f"⛔ Битый файл или аккаунт забанен: {session_name.split('/')[-1]}.session. Возможно, запущен под другим IP")
            working_with_accounts(account_folder=f"{account_directory}/{session_name.split('/')[-1]}.session",
                                  new_account_folder=f"user_settings/accounts/invalid_account/{session_name.split('/')[-1]}.session")
        except AuthKeyUnregisteredError:
            await telegram_client.disconnect()  # Разрываем соединение Telegram, для удаления session файла
            logger.error(f"⛔ Битый файл или аккаунт забанен: {session_name.split('/')[-1]}.session. Возможно, запущен под другим IP")
            working_with_accounts(account_folder=f"{account_directory}/{session_name.split('/')[-1]}.session",
                                  new_account_folder=f"user_settings/accounts/invalid_account/{session_name.split('/')[-1]}.session")

    async def rename_session_file(self, telegram_client, phone_old, phone, account_directory) -> None:
        """
        Переименовывает session файлы.
        :param telegram_client: Клиент для работы с Telegram
        :param phone_old: Номер телефона для переименования
        :param phone: Номер телефона для переименования
        :param account_directory: Путь к каталогу с файлами
        """
        await telegram_client.disconnect()  # Отключаемся от аккаунта для освобождения session файла
        try:
            # Переименование session файла
            os.rename(f"{account_directory}/{phone_old}.session", f"{account_directory}/{phone}.session", )
        except FileExistsError:
            # Если файл существует, то удаляем дубликат
            os.remove(f"{account_directory}/{phone_old}.session")

    async def get_telegram_client(self, file, account_directory):
        """
        Подключение к Telegram, используя файл session.
        Имя файла сессии file[0] - session файл
        :param account_directory: Путь к директории
        :param file: Файл сессии (file[0] - session файл)
        :return TelegramClient: TelegramClient
        """
        logger.info(f"Подключение к аккаунту: {account_directory}/{file[0]}")  # Получаем имя файла сессии file[0] - session файл
        telegram_client = await self.get_telegram_client(file[0], account_directory)
        try:
            await telegram_client.connect()
            return telegram_client
        except AuthKeyDuplicatedError:
            await telegram_client.disconnect()  # Отключаемся от аккаунта, что бы session файл не был занят другим процессом
            logger.info(f"На данный момент аккаунт {file[0].split('/')[-1]} запущен под другим ip")
            working_with_accounts(account_folder=f"{account_directory}/{file[0].split('/')[-1]}.session",
                                  new_account_folder=f"user_settings/accounts/invalid_account/{file[0].split('/')[-1]}.session")

    async def start_telegram_session(self):
        """Account telegram connect, с проверкой на валидность, если ранее не было соединения, то запрашиваем код"""
        logger.info("Подключение к Telegram. Введите номер телефона: ")
        # TODO: Убрать input() в коде
        phone_number = input(" ")
        telegram_client = await self.get_telegram_client(file=f"{phone_number}", account_directory="user_settings/accounts")
        await telegram_client.connect()  # Подключаемся к Telegram
        if not await telegram_client.is_user_authorized():
            await telegram_client.send_code_request(phone_number)
            try:
                logger.info("[+] Введите код: ")
                # TODO: Убрать input() в коде
                phone_code = input(" ")
                # Если ранее аккаунт не подсоединялся, то просим ввести код подтверждения
                await telegram_client.sign_in(phone_number, code=phone_code)
            except SessionPasswordNeededError:
                # Если аккаунт имеет password, то просим пользователя ввести пароль
                logger.info("Введите пароль для входа в аккаунт: ")
                # TODO: Убрать input() в коде
                password = input(" ")
                await telegram_client.sign_in(password=password)
            except ApiIdInvalidError:
                logger.info("[!] Неверные API ID или API Hash.")
        telegram_client.disconnect()  # Отключаемся от Telegram
