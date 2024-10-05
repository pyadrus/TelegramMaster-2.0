# -*- coding: utf-8 -*-
import os
import os.path
import sqlite3
import time

import flet as ft  # Импортируем библиотеку flet
from loguru import logger
from telethon import TelegramClient
from telethon.errors import (AuthKeyDuplicatedError, PhoneNumberBannedError, UserDeactivatedBanError, TimedOutError,
                             AuthKeyNotFound, TypeNotFoundError, AuthKeyUnregisteredError, SessionPasswordNeededError,
                             ApiIdInvalidError, YouBlockedUserError)
from thefuzz import fuzz

from system.auxiliary_functions.auxiliary_functions import working_with_accounts, find_filess
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

    async def connect_to_telegram(self, session_name, account_directory) -> TelegramClient:
        """
        Создает клиент для подключения к Telegram. Proxy IPV6 - НЕ РАБОТАЮТ.
        :param session_name: Имя сессии
        :param account_directory: Путь к директории
        :return TelegramClient: TelegramClient
        """
        try:
            logger.info(f"Используем API ID: {self.api_id}, API Hash: {self.api_hash}")
            telegram_client = TelegramClient(f"{account_directory}/{session_name}", api_id=self.api_id,
                                             api_hash=self.api_hash,
                                             system_version="4.16.30-vxCUSTOM",
                                             proxy=await reading_proxy_data_from_the_database(self.db_handler))
            return telegram_client
        except Exception as e:
            logger.exception(f"Ошибка: {e}")

    async def verify_account(self, folder_name, session_name) -> None:
        """
        Проверяет и сортирует аккаунты.
        :param session_name: Имя аккаунта для проверки аккаунта
        :param folder_name: Папка с аккаунтами
        """
        try:
            logger.info(f"Проверка аккаунта {session_name}. Используем API ID: {self.api_id}, API Hash: {self.api_hash}")
            telegram_client = await self.get_telegram_client(session_name, f"user_settings/accounts/{folder_name}")
            try:
                await telegram_client.connect()  # Подсоединяемся к Telegram аккаунта
                if not await telegram_client.is_user_authorized():  # Если аккаунт не авторизирован
                    await telegram_client.disconnect()
                    time.sleep(5)
                    working_with_accounts(f"user_settings/accounts/{folder_name}/{session_name}.session",
                                          f"user_settings/accounts/banned/{session_name}.session")
                else:
                    logger.info(f'Аккаунт {session_name} авторизован')
                    await telegram_client.disconnect()  # Отключаемся после проверки
            except (PhoneNumberBannedError, UserDeactivatedBanError, AuthKeyNotFound,
                    AuthKeyUnregisteredError, AuthKeyDuplicatedError) as e:
                await self.handle_banned_account(telegram_client, folder_name, session_name, e)
            except TimedOutError as e:
                logger.exception(f"Ошибка таймаута: {e}")
                time.sleep(2)
            except sqlite3.OperationalError:
                await telegram_client.disconnect()
                working_with_accounts(f"user_settings/accounts/{folder_name}/{session_name}.session",
                                      f"user_settings/accounts/banned/{session_name}.session")
        except Exception as e:
            logger.exception(f"Ошибка: {e}")


    async def handle_banned_account(self, telegram_client, folder_name, session_name, exception):
        """
        Обработка забаненных аккаунтов.
        telegram_client.disconnect() - Отключение от Telegram.
        working_with_accounts() - Перемещение файла. Исходный путь к файлу - account_folder. Путь к новой папке,
        куда нужно переместить файл - new_account_folder
        :param telegram_client: TelegramClient
        :param folder_name: Папка с аккаунтами
        :param session_name: Имя аккаунта
        :param exception: Расширение файла
        """
        logger.error(f"⛔ Аккаунт забанен: {session_name}. {str(exception)}")
        await telegram_client.disconnect()
        working_with_accounts(f"user_settings/accounts/{folder_name}/{session_name}.session",
                              f"user_settings/accounts/banned/{session_name}.session")

    # async def working_with_accountss(self, account_folder, new_account_folder) -> None:
    #     """
    #     Асинхронная работа с аккаунтами.
    #     :param account_folder: Путь к папке с аккаунтами
    #     :param new_account_folder: Путь к новой папке для аккаунтов
    #     """
    #     try:
            # Проверяем существование директории назначения, если её нет — создаем
            # if not os.path.exists(new_account_folder):
            #     os.makedirs(new_account_folder)

            # Проверяем, существует ли уже файл в целевой директории
            # target_file = os.path.join(new_account_folder, os.path.basename(account_folder))
            # if os.path.exists(target_file):
            #     logger.warning(f"Файл {target_file} уже существует. Удаляем дубликат.")
            #     os.remove(target_file)  # Удаляем файл, если он существует

            # Перемещаем файл
            # os.replace(account_folder, target_file)
            # logger.info(f"Аккаунт успешно перемещен из {account_folder} в {target_file}")

        # except FileNotFoundError:
        #     logger.error(f"Не удалось найти аккаунт: {account_folder}")
        # except FileExistsError:
        #     os.remove(account_folder)
        #     logger.info(f"Файл {account_folder} удален, так как дубликат уже существует.")
        # except PermissionError:
        #     logger.error("Не удалось перенести файлы в нужную папку: недостаточно прав.")
        # except Exception as e:
        #     logger.exception(f"Ошибка при работе с аккаунтами: {e}")

    async def check_for_spam(self, folder_name) -> None:
        """
        Проверка аккаунта на спам через @SpamBot
        :param folder_name: папка с аккаунтами
        """
        try:
            for session_name in find_filess(directory_path=f"user_settings/accounts/{folder_name}", extension='session'):
                telegram_client = await self.get_telegram_client(session_name, account_directory=f"user_settings/accounts/{folder_name}")
                try:
                    await telegram_client.send_message('SpamBot', '/start')  # Находим спам бот, и вводим команду /start
                    for message in await telegram_client.get_messages('SpamBot'):
                        logger.info(f"{session_name} {message.message}")
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
                            await telegram_client.disconnect()  # Отключаемся от аккаунта, для освобождения процесса session файла.
                            logger.info(f"Проверка аккаунтов через SpamBot. {session_name}: {message.message}")
                            # Перенос Telegram аккаунта в папку banned, если Telegram аккаунт в бане
                            working_with_accounts(f"user_settings/accounts/{folder_name}/{session_name}.session",
                                                  f"user_settings/accounts/banned/{session_name}.session")
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
                            await telegram_client.disconnect()  # Отключаемся от аккаунта, для освобождения процесса session файла.
                            logger.error(f"Проверка аккаунтов через SpamBot. {session_name}: {message.message}")
                            # Перенос Telegram аккаунта в папку banned, если Telegram аккаунт в бане
                            logger.info(session_name)
                            working_with_accounts(f"user_settings/accounts/{folder_name}/{session_name}.session",
                                                  f"user_settings/accounts/banned/{session_name}.session")
                        logger.error(f"Проверка аккаунтов через SpamBot. {session_name}: {message.message}")
                        await telegram_client.disconnect()  # Отключаемся от аккаунта, для освобождения процесса session файла.
                except YouBlockedUserError:
                    continue  # Записываем ошибку в software_database.db и продолжаем работу
                except (AttributeError, AuthKeyUnregisteredError) as e:
                    logger.error(e)
                    continue
        except Exception as e:
            logger.exception(f"Ошибка: {e}")

    async def verify_all_accounts(self, folder_name) -> None:
        """
        Проверяет все аккаунты Telegram в указанной директории.
        :folder_name: Имя каталога с аккаунтами
        """
        try:
            logger.info(f"Запуск проверки аккаунтов Telegram из папки 📁: {folder_name}")
            await checking_the_proxy_for_work()  # Проверка proxy
            # Сканирование каталога с аккаунтами
            for session_file in find_filess(directory_path=f"user_settings/accounts/{folder_name}", extension='session'):
                logger.info(f"⚠️ Проверяемый аккаунт: user_settings/accounts/{session_file}")
                # Проверка аккаунтов
                await self.verify_account(folder_name=folder_name, session_name=session_file)
            logger.info(f"Окончание проверки аккаунтов Telegram из папки 📁: {folder_name}")
        except Exception as e:
            logger.exception(f"Ошибка: {e}")

    async def get_account_details(self, folder_name):
        """
        Получает информацию о Telegram аккаунте.
        :param folder_name: Имя каталога
        """
        try:
            logger.info(f"Запуск переименования аккаунтов Telegram из папки 📁: {folder_name}")
            await checking_the_proxy_for_work()  # Проверка proxy
            # Сканирование каталога с аккаунтами
            for session_name in find_filess(directory_path=f"user_settings/accounts/{folder_name}", extension='session'):
                logger.info(f"⚠️ Переименовываемый аккаунт: user_settings/accounts/{session_name}")
                # Переименовывание аккаунтов
                logger.info(f"Переименовывание аккаунта {session_name}. Используем API ID: {self.api_id}, API Hash: {self.api_hash}")

                telegram_client = await self.get_telegram_client(session_name, account_directory=f"user_settings/accounts/{folder_name}")

                try:
                    me = await telegram_client.get_me()
                    phone = me.phone
                    await self.rename_session_file(telegram_client, session_name, phone, folder_name)

                except TypeNotFoundError:
                    await telegram_client.disconnect()  # Разрываем соединение Telegram, для удаления session файла
                    logger.error(f"⛔ Битый файл или аккаунт забанен: {session_name}.session. Возможно, запущен под другим IP")
                    working_with_accounts(f"user_settings/accounts/{folder_name}/{session_name}.session",
                                          f"user_settings/accounts/banned/{session_name}.session")
                except AuthKeyUnregisteredError:
                    await telegram_client.disconnect()  # Разрываем соединение Telegram, для удаления session файла
                    logger.error(f"⛔ Битый файл или аккаунт забанен: {session_name}.session. Возможно, запущен под другим IP")
                    working_with_accounts(f"user_settings/accounts/{folder_name}/{session_name}.session",
                                          f"user_settings/accounts/banned/{session_name}.session")
        except Exception as e:
            logger.exception(f"Ошибка: {e}")

    async def rename_session_file(self, telegram_client, phone_old, phone, folder_name) -> None:
        """
        Переименовывает session файлы.
        :param telegram_client: Клиент для работы с Telegram
        :param phone_old: Номер телефона для переименования
        :param phone: Номер телефона для переименования (новое название для session файла)
        :param folder_name: Папка с аккаунтами
        """
        await telegram_client.disconnect()  # Отключаемся от аккаунта для освобождения session файла
        try:
            # Переименование session файла
            os.rename(f"user_settings/accounts/{folder_name}/{phone_old}.session", f"user_settings/accounts/{folder_name}/{phone}.session", )
        except FileExistsError:
            # Если файл существует, то удаляем дубликат
            os.remove(f"user_settings/accounts/{folder_name}/{phone_old}.session")
        except Exception as e:
            logger.exception(f"Ошибка: {e}")


    async def get_telegram_client(self, session_name, account_directory):
        """
        Подключение к Telegram, используя файл session.
        Имя файла сессии file[0] - session файл
        :param account_directory: Путь к директории
        :param session_name: Файл сессии (file[0] - session файл)
        :return TelegramClient: TelegramClient
        """

        logger.info(f"Имя сессии !!!!!!!!: {account_directory}/{session_name}")  # Имя файла сессии file[0] - session файл

        logger.info(f"Подключение к аккаунту: {account_directory}/{session_name}")  # Имя файла сессии file[0] - session файл
        telegram_client = await self.connect_to_telegram(session_name, account_directory)
        try:
            await telegram_client.connect()
            return telegram_client
        except AuthKeyDuplicatedError:
            await telegram_client.disconnect()  # Отключаемся от аккаунта, для освобождения процесса session файла.
            logger.info(f"На данный момент аккаунт {session_name} запущен под другим ip") # TODO посмотреть правильный путь
            working_with_accounts(f"{account_directory}/{session_name}.session",
                                  f"user_settings/accounts/banned/{session_name}.session")
        except Exception as e:
            logger.exception(f"Ошибка: {e}")

    async def start_telegram_session(self, page: ft.Page):
        """Account telegram connect, с проверкой на валидность, если ранее не было соединения, то запрашиваем код"""
        try:
            phone_number = ft.TextField(label="Введите номер телефона:", multiline=False, max_lines=1)

            async def btn_click(e) -> None:
                phone_number_value = phone_number.value
                logger.info(f"Номер телефона: {phone_number_value}")

                # Дальнейшая обработка после записи номера телефона
                proxy_settings = await reading_proxy_data_from_the_database(self.db_handler)  # Proxy IPV6 - НЕ РАБОТАЮТ
                telegram_client = TelegramClient(f"user_settings/accounts/{phone_number_value}", api_id=self.api_id,
                                                 api_hash=self.api_hash,
                                                 system_version="4.16.30-vxCUSTOM", proxy=proxy_settings)
                await telegram_client.connect()  # Подключаемся к Telegram

                if not await telegram_client.is_user_authorized():
                    logger.info("Пользователь не авторизован")
                    await telegram_client.send_code_request(phone_number_value)  # Отправка кода на телефон
                    time.sleep(2)

                    passww = ft.TextField(label="Введите код telegram:", multiline=True, max_lines=1)

                    async def btn_click_code(e) -> None:
                        try:
                            logger.info(f"Код telegram: {passww.value}")
                            await telegram_client.sign_in(phone_number_value, passww.value)  # Авторизация с кодом
                            telegram_client.disconnect()
                            page.go("/settings")  # Перенаправление в настройки, если 2FA не требуется
                            page.update()
                        except SessionPasswordNeededError:  # Если аккаунт защищен паролем, запрашиваем пароль
                            logger.info("Требуется двухфакторная аутентификация. Введите пароль.")
                            pass_2fa = ft.TextField(label="Введите пароль telegram:", multiline=False, max_lines=1)

                            async def btn_click_password(e) -> None:
                                logger.info(f"Пароль telegram: {pass_2fa.value}")
                                try:
                                    await telegram_client.sign_in(password=pass_2fa.value)
                                    logger.info("Успешная авторизация.")
                                    telegram_client.disconnect()
                                    page.go("/settings")  # Изменение маршрута в представлении существующих настроек
                                    page.update()
                                except Exception as ex:
                                    logger.error(f"Ошибка при вводе пароля: {ex}")

                            button_password = ft.ElevatedButton("Готово", on_click=btn_click_password)
                            page.views.append(ft.View(controls=[pass_2fa, button_password]))
                            page.update()  # Обновляем страницу, чтобы интерфейс отобразился

                        except ApiIdInvalidError:
                            logger.error("[!] Неверные API ID или API Hash.")
                            await telegram_client.disconnect()  # Отключаемся от Telegram
                        except Exception as ex:
                            logger.error(f"Ошибка при авторизации: {ex}")
                            await telegram_client.disconnect()  # Отключаемся от Telegram

                    button_code = ft.ElevatedButton("Готово", on_click=btn_click_code)
                    page.views.append(ft.View(controls=[passww, button_code]))
                    page.update()  # Обновляем страницу, чтобы отобразился интерфейс для ввода кода

                page.update()

            button = ft.ElevatedButton("Готово", on_click=btn_click)

            input_view = ft.View(
                controls=[phone_number, button])  # Создаем вид, который будет содержать поле ввода и кнопку

            page.views.append(input_view)  # Добавляем созданный вид на страницу
            page.update()

        except Exception as e:
            logger.exception(f"Ошибка: {e}")
