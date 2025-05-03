# -*- coding: utf-8 -*-
import asyncio
import os
import os.path
import shutil
import sqlite3

import flet as ft  # Импортируем библиотеку flet
from loguru import logger
from telethon import TelegramClient
from telethon.errors import (AuthKeyDuplicatedError, PhoneNumberBannedError, UserDeactivatedBanError, TimedOutError,
                             AuthKeyNotFound, TypeNotFoundError, AuthKeyUnregisteredError, SessionPasswordNeededError,
                             ApiIdInvalidError, YouBlockedUserError, PasswordHashInvalidError)
from thefuzz import fuzz

from src.core.configs import ConfigReader, BUTTON_HEIGHT, line_width_button, path_accounts_folder
from src.core.localization import back_button, done_button
from src.core.sqlite_working_tools import DatabaseHandler
from src.core.utils import working_with_accounts, find_filess
from src.features.auth.logging_in import getting_phone_number_data_by_phone_number
from src.features.proxy.checking_proxy import checking_the_proxy_for_work
from src.features.proxy.checking_proxy import reading_proxy_data_from_the_database
from src.gui.menu import show_notification, log_and_display


class TGConnect:

    def __init__(self):
        self.db_handler = DatabaseHandler()
        self.config_reader = ConfigReader()
        self.api_id_api_hash = self.config_reader.get_api_id_data_api_hash_data()
        self.api_id = self.api_id_api_hash[0]
        self.api_hash = self.api_id_api_hash[1]

    async def verify_account(self, page: ft.Page, session_name) -> None:
        """
        Проверяет и сортирует аккаунты.

        :param session_name: Имя аккаунта для проверки аккаунта
        :param page: Страница интерфейса Flet для отображения элементов управления.
        """
        try:
            logger.info(
                f"Проверка аккаунта {session_name}. Используем API ID: {self.api_id}, API Hash: {self.api_hash}")
            telegram_client = await self.get_telegram_client(page, session_name, f"user_data/accounts")
            try:
                await telegram_client.connect()  # Подсоединяемся к Telegram аккаунта
                if not await telegram_client.is_user_authorized():  # Если аккаунт не авторизирован
                    await telegram_client.disconnect()
                    await asyncio.sleep(5)
                    working_with_accounts(f"user_data/accounts/{session_name}.session",
                                          f"user_data/accounts/banned/{session_name}.session")
                else:
                    logger.info(f'Аккаунт {session_name} авторизован')
                    await telegram_client.disconnect()  # Отключаемся после проверки
            except (PhoneNumberBannedError, UserDeactivatedBanError, AuthKeyNotFound,
                    AuthKeyUnregisteredError, AuthKeyDuplicatedError) as e:
                await self.handle_banned_account(telegram_client, session_name, e)
            except TimedOutError as error:
                logger.exception(f"❌ Ошибка таймаута: {error}")
                await asyncio.sleep(2)
            except sqlite3.OperationalError:
                await telegram_client.disconnect()
                working_with_accounts(f"user_data/accounts/{session_name}.session",
                                      f"user_data/accounts/banned/{session_name}.session")
        except Exception as error:
            logger.exception(f"❌ Ошибка: {error}")

    @staticmethod
    async def handle_banned_account(telegram_client, session_name, exception):
        """
        Обработка забаненных аккаунтов.
        telegram_client.disconnect() - Отключение от Telegram.
        working_with_accounts() - Перемещение файла. Исходный путь к файлу - account_folder. Путь к новой папке,
        куда нужно переместить файл - new_account_folder

        :param telegram_client: TelegramClient
        :param session_name: Имя аккаунта
        :param exception: Расширение файла
        """
        logger.error(f"⛔ Аккаунт забанен: {session_name}. {str(exception)}")
        await telegram_client.disconnect()
        working_with_accounts(f"user_data/accounts/{session_name}.session",
                              f"user_data/accounts/banned/{session_name}.session")

    async def check_for_spam(self, page: ft.Page, folder_name) -> None:
        """
        Проверка аккаунта на спам через @SpamBot

        :param folder_name: папка с аккаунтами
        :param page: Страница интерфейса Flet для отображения элементов управления.
        """
        try:
            for session_name in await find_filess(directory_path=f"user_data/accounts",
                                                  extension='session'):
                telegram_client = await self.get_telegram_client(page, session_name,
                                                                 account_directory=f"user_data/accounts")
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
                            working_with_accounts(f"user_data/accounts/{session_name}.session",
                                                  f"user_data/accounts/banned/{session_name}.session")
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
                            working_with_accounts(f"user_data/accounts/{session_name}.session",
                                                  f"user_data/accounts/banned/{session_name}.session")
                        logger.error(f"Проверка аккаунтов через SpamBot. {session_name}: {message.message}")

                        try:
                            await telegram_client.disconnect()  # Отключаемся от аккаунта, для освобождения процесса session файла.
                        except sqlite3.OperationalError as e:
                            logger.info(f"Ошибка при отключении аккаунта: {session_name}")

                            await self.handle_banned_account(telegram_client, session_name, e)

                except YouBlockedUserError:
                    continue  # Записываем ошибку в software_database.db и продолжаем работу
                except (AttributeError, AuthKeyUnregisteredError) as e:
                    logger.error(e)
                    continue

        except Exception as error:
            logger.exception(f"❌ Ошибка: {error}")

    async def verify_all_accounts(self, page: ft.Page, list_view: ft.ListView) -> None:
        """
        Проверяет все аккаунты Telegram в указанной директории.

        :param page: Страница интерфейса Flet для отображения элементов управления.
        :param list_view: Список для отображения информации.
        """
        try:
            await log_and_display(f"Запуск проверки аккаунтов Telegram из папки 📁: accounts", list_view, page)
            await checking_the_proxy_for_work()  # Проверка proxy
            # Сканирование каталога с аккаунтами
            for session_file in await find_filess(directory_path=path_accounts_folder, extension='session',
                                                  list_view=list_view, page=page):
                await log_and_display(f"⚠️ Проверяемый аккаунт: user_data/accounts/{session_file}", list_view, page)
                # Проверка аккаунтов
                await self.verify_account(page=page, session_name=session_file)
            await log_and_display(f"Окончание проверки аккаунтов Telegram из папки 📁: accounts", list_view, page)
        except Exception as error:
            logger.exception(f"❌ Ошибка: {error}")

    async def get_account_details(self, page, folder_name):
        """
        Получает информацию о Telegram аккаунте.

        :param folder_name: Имя каталога
        :param page: Страница интерфейса Flet для отображения элементов управления.
        """
        try:
            logger.info(f"Запуск переименования аккаунтов Telegram из папки 📁: {folder_name}")
            await checking_the_proxy_for_work()  # Проверка proxy
            # Сканирование каталога с аккаунтами
            for session_name in await find_filess(directory_path=f"user_data/accounts/{folder_name}",
                                                  extension='session'):
                logger.info(f"⚠️ Переименовываемый аккаунт: user_data/accounts/{session_name}")
                # Переименовывание аккаунтов
                logger.info(
                    f"Переименовывание аккаунта {session_name}. Используем API ID: {self.api_id}, API Hash: {self.api_hash}")

                telegram_client = await self.get_telegram_client(page, session_name,
                                                                 account_directory=f"user_data/accounts/{folder_name}")

                try:
                    me = await telegram_client.get_me()
                    phone = me.phone
                    await self.rename_session_file(telegram_client, session_name, phone, folder_name)

                except AttributeError:  # Если в get_me приходит NoneType (None)
                    pass

                except TypeNotFoundError:
                    await telegram_client.disconnect()  # Разрываем соединение Telegram, для удаления session файла
                    logger.error(
                        f"⛔ Битый файл или аккаунт забанен: {session_name}.session. Возможно, запущен под другим IP")
                    working_with_accounts(f"user_data/accounts/{folder_name}/{session_name}.session",
                                          f"user_data/accounts/banned/{session_name}.session")
                except AuthKeyUnregisteredError:
                    await telegram_client.disconnect()  # Разрываем соединение Telegram, для удаления session файла
                    logger.error(
                        f"⛔ Битый файл или аккаунт забанен: {session_name}.session. Возможно, запущен под другим IP")
                    working_with_accounts(f"user_data/accounts/{folder_name}/{session_name}.session",
                                          f"user_data/accounts/banned/{session_name}.session")
        except Exception as error:
            logger.exception(f"❌ Ошибка: {error}")

    @staticmethod
    async def rename_session_file(telegram_client, phone_old, phone, folder_name) -> None:
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
            os.rename(f"user_data/accounts/{folder_name}/{phone_old}.session",
                      f"user_data/accounts/{folder_name}/{phone}.session", )
        except FileExistsError:
            # Если файл существует, то удаляем дубликат
            os.remove(f"user_data/accounts/{folder_name}/{phone_old}.session")
        except Exception as error:
            logger.exception(f"❌ Ошибка: {error}")

        getting_phone_number_data_by_phone_number(phone)  # Выводим информацию о номере телефона

    async def get_telegram_client(self, page, session_name, account_directory):
        """
        Подключение к Telegram, используя файл session.
        Имя файла сессии file[0] - session файл

        :param account_directory: Путь к директории
        :param session_name: Файл сессии (file[0] - session файл)
        :param page: Страница интерфейса Flet для отображения элементов управления.
        :return TelegramClient: TelegramClient
        """
        logger.info(
            f"Подключение к аккаунту: {account_directory}/{session_name}. Используем API ID: {self.api_id}, API Hash: {self.api_hash}")  # Имя файла сессии file[0] - session файл
        telegram_client = None  # Инициализируем переменную
        try:
            telegram_client = TelegramClient(f"{account_directory}/{session_name}", api_id=self.api_id,
                                             api_hash=self.api_hash,
                                             system_version="4.16.30-vxCUSTOM",
                                             proxy=await reading_proxy_data_from_the_database(self.db_handler))

            await telegram_client.connect()
            return telegram_client

        except sqlite3.OperationalError:

            logger.info(f"❌ Аккаунт {account_directory}/{session_name} поврежден.")
            # await show_notification(
            #     page,
            #     f"⚠️ У нас возникла проблема с аккаунтом {account_directory}/{session_name}.\n\n"
            #     f"Чтобы избежать дальнейших ошибок, пожалуйста, удалите этот аккаунт вручную и попробуйте снова. 🔄"
            # )

        except sqlite3.DatabaseError:

            logger.info(f"❌ Аккаунт {session_name} поврежден.")
            # await show_notification(
            #     page,
            #     f"⚠️ У нас возникла проблема с аккаунтом {account_directory}/{session_name}.\n\n"
            #     f"Чтобы избежать дальнейших ошибок, пожалуйста, удалите этот аккаунт вручную и попробуйте снова. 🔄"
            # )

        except AuthKeyDuplicatedError:
            await telegram_client.disconnect()  # Отключаемся от аккаунта, для освобождения процесса session файла.
            logger.info(f"❌ На данный момент аккаунт {session_name} запущен под другим ip")
            working_with_accounts(f"{account_directory}/{session_name}.session",
                                  f"user_data/accounts/banned/{session_name}.session")
        except AttributeError as error:
            logger.error(f"❌ Ошибка: {error}")
        except ValueError:
            logger.info(f"❌ Ошибка подключения прокси к аккаунту {session_name}.")
        except Exception as error:
            await telegram_client.disconnect()
            logger.exception(f"❌ Ошибка: {error}")

    async def connecting_number_accounts(self, page: ft.Page):
        """
        Подключение номера Telegram аккаунта с проверкой на валидность. Если ранее не было соединения, то запрашивается
        код.

        :param page: Страница интерфейса Flet для отображения элементов управления.
        """
        try:
            # Создаем текстовый элемент и добавляем его на страницу
            header_text = ft.Text(f"Подключение аккаунтов Telegram", size=15, color="pink600")

            phone_number = ft.TextField(label="Введите номер телефона:", multiline=False, max_lines=1)

            async def btn_click(e) -> None:
                phone_number_value = phone_number.value
                logger.info(f"Номер телефона: {phone_number_value}")

                # Дальнейшая обработка после записи номера телефона
                proxy_settings = await reading_proxy_data_from_the_database(self.db_handler)  # Proxy IPV6 - НЕ РАБОТАЮТ
                telegram_client = TelegramClient(f"user_data/accounts/{phone_number_value}",
                                                 api_id=self.api_id,
                                                 api_hash=self.api_hash,
                                                 system_version="4.16.30-vxCUSTOM", proxy=proxy_settings)
                await telegram_client.connect()  # Подключаемся к Telegram

                if not await telegram_client.is_user_authorized():
                    logger.info("Пользователь не авторизован")
                    await telegram_client.send_code_request(phone_number_value)  # Отправка кода на телефон
                    await asyncio.sleep(2)

                    passww = ft.TextField(label="Введите код telegram:", multiline=True, max_lines=1)

                    async def btn_click_code(e) -> None:
                        try:
                            logger.info(f"Код telegram: {passww.value}")
                            await telegram_client.sign_in(phone_number_value, passww.value)  # Авторизация с кодом
                            telegram_client.disconnect()
                            page.go("/")  # Перенаправление в настройки, если 2FA не требуется
                            page.update()
                        except SessionPasswordNeededError:  # Если аккаунт защищен паролем, запрашиваем пароль
                            logger.info("❌ Требуется двухфакторная аутентификация. Введите пароль.")
                            pass_2fa = ft.TextField(label="Введите пароль telegram:", multiline=False, max_lines=1)

                            async def btn_click_password(e) -> None:
                                logger.info(f"Пароль telegram: {pass_2fa.value}")
                                try:
                                    await telegram_client.sign_in(password=pass_2fa.value)
                                    logger.info("Успешная авторизация.")
                                    telegram_client.disconnect()
                                    page.go("/")  # Изменение маршрута в представлении существующих настроек
                                    page.update()
                                except PasswordHashInvalidError:
                                    logger.error(f"❌ Неверный пароль.")
                                    await show_notification(page, f"⚠️ Неверный пароль. Попробуйте еще раз.")
                                    page.go("/")  # Изменение маршрута в представлении существующих настроек
                                except Exception as ex:
                                    logger.exception(f"❌ Ошибка при вводе пароля: {ex}")

                            button_password = ft.ElevatedButton(width=line_width_button, height=BUTTON_HEIGHT,
                                                                text=done_button,
                                                                on_click=btn_click_password)  # Кнопка "Готово"
                            page.views.append(ft.View(controls=[pass_2fa, button_password]))
                            page.update()  # Обновляем страницу, чтобы интерфейс отобразился

                        except ApiIdInvalidError:
                            logger.error("[!] Неверные API ID или API Hash.")
                            await telegram_client.disconnect()  # Отключаемся от Telegram
                        except Exception as error:
                            logger.exception(f"❌ Ошибка при авторизации: {error}")
                            await telegram_client.disconnect()  # Отключаемся от Telegram

                    button_code = ft.ElevatedButton(width=line_width_button, height=BUTTON_HEIGHT, text=done_button,
                                                    on_click=btn_click_code)  # Кнопка "Готово"
                    page.views.append(ft.View(controls=[passww, button_code]))
                    page.update()  # Обновляем страницу, чтобы отобразился интерфейс для ввода кода

                page.update()

            async def back_button_clicked(e):
                """
                Кнопка возврата в меню настроек
                """
                page.go("/")

            button = ft.ElevatedButton(width=line_width_button, height=BUTTON_HEIGHT, text=done_button,
                                       on_click=btn_click)  # Кнопка "Готово"
            button_back = ft.ElevatedButton(width=line_width_button, height=BUTTON_HEIGHT, text=back_button,
                                            on_click=back_button_clicked)  # Кнопка "Назад"

            input_view = ft.View(
                controls=[header_text, phone_number, button,
                          button_back])  # Создаем вид, который будет содержать поле ввода и кнопку

            page.views.append(input_view)  # Добавляем созданный вид на страницу
            page.update()

        except Exception as error:
            logger.exception(f"❌ Ошибка: {error}")

    @staticmethod
    async def connecting_session_accounts(page: ft.Page):
        """
        Подключение сессии Telegram

        :param page: Страница интерфейса Flet для отображения элементов управления.
        """
        try:
            # Создаем текстовый элемент и добавляем его на страницу
            header_text = ft.Text(f"Подключение аккаунтов Telegram.\n\n Выберите session файл\n", size=15)

            # Поле для отображения выбранного файла
            selected_files = ft.Text(value="Session файл не выбран", size=12)

            async def btn_click(e: ft.FilePickerResultEvent) -> None:
                """Обработка выбора файла"""
                if e.files:
                    file_name = e.files[0].name  # Имя файла
                    file_path = e.files[0].path  # Путь к файлу

                    # Проверка расширения файла на ".session"
                    if file_name.endswith(".session"):
                        selected_files.value = f"Выбран session файл: {file_name}"
                        selected_files.update()

                        # Определяем целевой путь для копирования файла
                        target_folder = f"user_data/accounts"
                        target_path = os.path.join(target_folder, file_name)

                        # Создаем директорию, если она не существует
                        os.makedirs(target_folder, exist_ok=True)

                        # Копируем файл
                        shutil.copy(file_path, target_path)
                        selected_files.value = f"Файл скопирован в: {target_path}"
                    else:
                        selected_files.value = "Выбранный файл не является session файлом"
                else:
                    selected_files.value = "Выбор файла отменен"

                selected_files.update()
                page.update()

            async def back_button_clicked(e):
                """Кнопка возврата в меню настроек"""
                page.go("/")

            pick_files_dialog = ft.FilePicker(on_result=btn_click)  # Инициализация выбора файлов

            page.overlay.append(pick_files_dialog)  # Добавляем FilePicker на страницу

            # Кнопка для открытия диалога выбора файлов
            button_select_file = ft.ElevatedButton(width=line_width_button, height=BUTTON_HEIGHT,
                                                   text="Выбрать session файл",
                                                   on_click=lambda _: pick_files_dialog.pick_files()
                                                   )

            # Кнопка возврата
            button_back = ft.ElevatedButton(width=line_width_button, height=BUTTON_HEIGHT, text=back_button,
                                            on_click=back_button_clicked)

            # Добавляем все элементы на страницу
            input_view = ft.View(
                controls=[
                    header_text,
                    selected_files,  # Поле для отображения выбранного файла
                    button_select_file,  # Кнопка выбора файла
                    button_back  # Кнопка возврата
                ]
            )

            page.views.append(input_view)  # Добавляем созданный вид на страницу
            page.update()

        except Exception as error:
            logger.exception(f"❌ Ошибка: {error}")
