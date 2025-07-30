# -*- coding: utf-8 -*-
import asyncio
import os
import os.path
import shutil
import sqlite3

import flet as ft  # Импортируем библиотеку flet
from loguru import logger
from telethon import TelegramClient
from telethon.errors import (ApiIdInvalidError, AuthKeyDuplicatedError,
                             AuthKeyNotFound, AuthKeyUnregisteredError,
                             PasswordHashInvalidError, PhoneNumberBannedError,
                             SessionPasswordNeededError, TimedOutError,
                             TypeNotFoundError, UserDeactivatedBanError,
                             YouBlockedUserError)
from thefuzz import fuzz

from src.core.configs import BUTTON_HEIGHT, ConfigReader, WIDTH_WIDE_BUTTON, path_accounts_folder
from src.core.utils import find_filess, working_with_accounts
from src.features.account.parsing.gui_elements import GUIProgram
from src.features.auth.logging_in import getting_phone_number_data_by_phone_number
from src.features.proxy.checking_proxy import checking_the_proxy_for_work, reading_proxy_data_from_the_database
from src.gui.gui import end_time, log_and_display, start_time
from src.gui.notification import show_notification
from src.locales.translations_loader import translations


class TGConnect:

    def __init__(self, page):
        self.config_reader = ConfigReader()
        self.api_id_api_hash = self.config_reader.get_api_id_data_api_hash_data()
        self.api_id = self.api_id_api_hash[0]
        self.api_hash = self.api_id_api_hash[1]
        self.page = page  # Страница интерфейса Flet для отображения элементов управления.

    async def verify_account(self, session_name) -> None:
        """
        Проверяет и сортирует аккаунты.

        :param session_name: Имя аккаунта для проверки аккаунта
        """
        try:
            await log_and_display(f"Проверка аккаунта {session_name}", self.page)
            client = await self.get_telegram_client(session_name=session_name,
                                                    account_directory=path_accounts_folder)
            try:
                await client.connect()  # Подсоединяемся к Telegram аккаунта
                if not await client.is_user_authorized():  # Если аккаунт не авторизирован
                    await client.disconnect()
                    await asyncio.sleep(5)
                    working_with_accounts(f"user_data/accounts/{session_name}.session",
                                          f"user_data/accounts/banned/{session_name}.session")
                else:
                    await log_and_display(f"Аккаунт {session_name} авторизован", self.page)
                    await client.disconnect()  # Отключаемся после проверки
            except (PhoneNumberBannedError, UserDeactivatedBanError, AuthKeyNotFound,
                    AuthKeyUnregisteredError, AuthKeyDuplicatedError) as e:
                await self.handle_banned_account(client, session_name, e)
            except TimedOutError as error:
                await log_and_display(f"❌ Ошибка таймаута: {error}", self.page)
                await asyncio.sleep(2)
            except sqlite3.OperationalError:
                await client.disconnect()
                working_with_accounts(f"user_data/accounts/{session_name}.session",
                                      f"user_data/accounts/banned/{session_name}.session")
            except AttributeError:
                pass
        except Exception as error:
            logger.exception(error)

    async def handle_banned_account(self, telegram_client, session_name, exception):
        """
        Обработка banned аккаунтов.
        telegram_client.disconnect() - Отключение от Telegram.
        working_with_accounts() - Перемещение файла. Исходный путь к файлу - account_folder. Путь к новой папке,
        куда нужно переместить файл - new_account_folder

        :param telegram_client: TelegramClient
        :param session_name: Имя аккаунта
        :param exception: Расширение файла
        """
        try:
            await log_and_display(message=f"⛔ Аккаунт banned: {session_name}. {str(exception)}", page=self.page)
            await telegram_client.disconnect()
            working_with_accounts(account_folder=f"user_data/accounts/{session_name}.session",
                                  new_account_folder=f"user_data/accounts/banned/{session_name}.session")
        except sqlite3.OperationalError:
            await telegram_client.disconnect()
            working_with_accounts(account_folder=f"user_data/accounts/{session_name}.session",
                                  new_account_folder=f"user_data/accounts/banned/{session_name}.session")

    async def check_for_spam(self) -> None:
        """
        Проверка аккаунта на спам через @SpamBot
        """
        try:
            start = await start_time(self.page)
            for session_name in find_filess(directory_path=path_accounts_folder, extension='session'):
                client: TelegramClient = await self.get_telegram_client(session_name=session_name,
                                                                        account_directory=path_accounts_folder)
                try:
                    await client.send_message(entity='SpamBot',
                                              message='/start')  # Находим спам бот, и вводим команду /start
                    for message in await client.get_messages('SpamBot'):
                        await log_and_display(message=f"{session_name} {message.message}", page=self.page)
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
                            await log_and_display(message=f"⛔ Аккаунт заблокирован", page=self.page)
                            await client.disconnect()  # Отключаемся от аккаунта, для освобождения процесса session файла.
                            await log_and_display(
                                message=f"Проверка аккаунтов через SpamBot. {session_name}: {message.message}",
                                page=self.page)
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
                            await log_and_display(message=f"⛔ Аккаунт заблокирован", page=self.page)
                            await client.disconnect()  # Отключаемся от аккаунта, для освобождения процесса session файла.
                            await log_and_display(
                                message=f"Проверка аккаунтов через SpamBot. {session_name}: {message.message}",
                                page=self.page)
                            # Перенос Telegram аккаунта в папку banned, если Telegram аккаунт в бане
                            await log_and_display(message=f"{session_name}", page=self.page)
                            working_with_accounts(f"user_data/accounts/{session_name}.session",
                                                  f"user_data/accounts/banned/{session_name}.session")
                        await log_and_display(
                            message=f"Проверка аккаунтов через SpamBot. {session_name}: {message.message}",
                            page=self.page)
                        try:
                            await client.disconnect()  # Отключаемся от аккаунта, для освобождения процесса session файла.
                        except sqlite3.OperationalError as e:
                            await log_and_display(message=f"Ошибка при отключении аккаунта: {session_name}",
                                                  page=self.page)
                            await self.handle_banned_account(telegram_client=client, session_name=session_name,
                                                             exception=e)

                except YouBlockedUserError:
                    continue  # Записываем ошибку в software_database.db и продолжаем работу
                except (AttributeError, AuthKeyUnregisteredError) as e:
                    await log_and_display(message=f"❌ Ошибка: {e}", page=self.page)
                    continue
                except sqlite3.DatabaseError:
                    await log_and_display(f"❌ Ошибка базы данных, аккаунта или аккаунт заблокирован.", self.page)
                    # Отключаем клиент, игнорируя ошибки с SQLite
                    try:
                        await client.disconnect()
                    except Exception as e:
                        await log_and_display(f"⚠️ Не удалось корректно отключить {session_name}: {e}", self.page)

                    # Перенос Telegram аккаунта в папку banned, если Telegram аккаунт в бане
                    await log_and_display(message=f"{session_name}", page=self.page)
                    # working_with_accounts(f"user_data/accounts/{session_name}.session",
                    #                       f"user_data/accounts/banned/{session_name}.session")
                    session_file = f"user_data/accounts/{session_name}.session"
                    banned_dir = "user_data/accounts/banned"
                    banned_file = os.path.join(banned_dir, f"{session_name}.session")
                    # Удаляем связанный .session-journal, если он есть
                    journal_file = session_file + "-journal"
                    if os.path.exists(journal_file):
                        try:
                            os.remove(journal_file)
                            await log_and_display(f"🗑 Удалён повреждённый журнал: {journal_file}", self.page)
                        except Exception as e:
                            await log_and_display(f"⚠️ Не удалось удалить session-journal: {e}", self.page)

                    # Перемещаем основной .session файл
                    try:
                        shutil.move(session_file, banned_file)
                        await log_and_display(f"🚫 Аккаунт {session_name} перемещён в папку banned.", self.page)
                    except Exception as e:
                        await log_and_display(f"❌ Не удалось переместить аккаунт: {e}", self.page)

            await end_time(start, self.page)
            await show_notification(page=self.page, message="🔚 Проверка аккаунтов завершена")
        except Exception as error:
            logger.exception(error)

    async def verify_all_accounts(self, page: ft.Page) -> None:
        """
        Проверяет все аккаунты Telegram в указанной директории.

        :param page: Страница интерфейса Flet для отображения элементов управления.
        """
        try:
            start = await start_time(page)
            await checking_the_proxy_for_work(page=page)  # Проверка proxy
            # Сканирование каталога с аккаунтами
            for session_file in find_filess(directory_path=path_accounts_folder, extension='session'):
                await log_and_display(message=f"⚠️ Проверяемый аккаунт: {session_file}", page=page)
                # Проверка аккаунтов
                await self.verify_account(session_name=session_file)
            await log_and_display(message=f"Окончание проверки аккаунтов Telegram 📁", page=page)
            await end_time(start, page)
            await show_notification(page, "🔚 Проверка аккаунтов завершена")
        except Exception as error:
            logger.exception(error)

    async def get_account_details(self, page: ft.Page):
        """
        Получает информацию о Telegram аккаунте.

        :param page: Страница интерфейса Flet для отображения элементов управления.
        """
        try:
            start = await start_time(page)
            await checking_the_proxy_for_work(page=page)  # Проверка proxy
            # Сканирование каталога с аккаунтами
            for session_name in find_filess(directory_path=path_accounts_folder, extension='session'):
                await log_and_display(message=f"⚠️ Переименовываемый аккаунт: {session_name}", page=page)
                # Переименовывание аккаунтов
                client = await self.get_telegram_client(session_name=session_name,
                                                        account_directory=path_accounts_folder)
                try:
                    me = await client.get_me()
                    await self.rename_session_file(telegram_client=client, phone_old=session_name, phone=me.phone,
                                                   page=page)
                except AttributeError:  # Если в get_me приходит NoneType (None)
                    pass
                except TypeNotFoundError:
                    await client.disconnect()  # Разрываем соединение Telegram, для удаления session файла
                    await log_and_display(
                        message=f"⛔ Битый файл или аккаунт banned: {session_name}.session. Возможно, запущен под другим IP",
                        page=page)
                    working_with_accounts(account_folder=f"user_data/accounts/{session_name}.session",
                                          new_account_folder=f"user_data/accounts/banned/{session_name}.session")
                except AuthKeyUnregisteredError:
                    await client.disconnect()  # Разрываем соединение Telegram, для удаления session файла
                    await log_and_display(translations["ru"]["errors"]["auth_key_unregistered"], page)
                    working_with_accounts(account_folder=f"user_data/accounts/{session_name}.session",
                                          new_account_folder=f"user_data/accounts/banned/{session_name}.session")
            await end_time(start, page)
            await show_notification(page=page, message="🔚 Проверка аккаунтов завершена")
        except Exception as error:
            logger.exception(error)

    async def checking_all_accounts(self, page: ft.Page) -> None:
        try:
            start = await start_time(page)
            await self.verify_all_accounts(page=page)  # Проверка валидности аккаунтов
            await self.get_account_details(page=page)  # Переименование аккаунтов
            await self.check_for_spam()  # Проверка на спам ботов
            await end_time(start, page)
            await show_notification(page=page, message="🔚 Проверка аккаунтов завершена")
        except Exception as error:
            logger.exception(error)

    @staticmethod
    async def rename_session_file(telegram_client, phone_old, phone, page: ft.Page) -> None:
        """
        Переименовывает session файлы.

        :param telegram_client: Клиент для работы с Telegram
        :param phone_old: Номер телефона для переименования
        :param phone: Номер телефона для переименования (новое название для session файла)
        :param page: Страница интерфейса Flet для отображения элементов управления.
        """
        await telegram_client.disconnect()  # Отключаемся от аккаунта для освобождения session файла
        try:
            # Переименование session файла
            os.rename(f"user_data/accounts/{phone_old}.session",
                      f"user_data/accounts/{phone}.session", )
        except FileExistsError:
            # Если файл существует, то удаляем дубликат
            os.remove(f"user_data/accounts/{phone_old}.session")
        except Exception as error:
            logger.exception(error)

        await getting_phone_number_data_by_phone_number(phone, page)  # Выводим информацию о номере телефона

    async def get_telegram_client(self, session_name, account_directory):
        """
        Подключение к Telegram, используя файл session.
        Имя файла сессии file[0] - session файл

        :param account_directory: Путь к директории
        :param session_name: Файл сессии (file[0] - session файл)
        :return TelegramClient: TelegramClient
        """
        await log_and_display(message=f"Подключение к аккаунту: {session_name}", page=self.page)
        # client = None  # Инициализируем переменную
        client = TelegramClient(
            session=f"{account_directory}/{session_name}",
            api_id=self.api_id,
            api_hash=self.api_hash,
            system_version="4.16.30-vxCUSTOM",
            proxy=reading_proxy_data_from_the_database()
        )
        try:

            await client.connect()
            me = await client.get_me()
            logger.info(f"🧾 Аккаунт: {me.first_name} {me.last_name} | @{me.username} | ID: {me.id} | Phone: {me.phone}")
            await log_and_display(
                f"🧾 Аккаунт: {me.first_name} {me.last_name} | @{me.username} | ID: {me.id} | Phone: {me.phone}",
                self.page)

            # string_session = client.session.save()
            # logger.info(f"📦 String session: {string_session}")

            # if string_session is None:
            #     client.disconnect()
            #     working_with_accounts(f"{account_directory}/{session_name}.session",
            #                           f"user_data/accounts/banned/{session_name}.session")
            return client

        # except FloodWaitError as e:
        #     logger.warning(f"[{session_name}] Слишком частые запросы. Ждем {e.seconds} сек.")
        #     await log_and_display(f"⏳ FloodWait {e.seconds} секунд для {session_name}", page)
        #     await asyncio.sleep(e.seconds)
        #     return None

        except sqlite3.OperationalError:
            await log_and_display(message=f"❌ Аккаунт {session_name} поврежден.", page=self.page)
            return None
        except sqlite3.DatabaseError:
            await log_and_display(message=f"❌ Аккаунт {session_name} поврежден.", page=self.page)
            return None
        except AuthKeyDuplicatedError:
            await client.disconnect()  # Отключаемся от аккаунта, для освобождения процесса session файла.
            await log_and_display(message=f"❌ Аккаунт {session_name} запущен под другим ip", page=self.page)
            working_with_accounts(f"{account_directory}/{session_name}.session",
                                  f"user_data/accounts/banned/{session_name}.session")
            return None
        except AttributeError as error:
            await log_and_display(message=f"❌ Ошибка: {error}", page=self.page)
            return None
        except ValueError:
            await log_and_display(message=f"❌ Ошибка подключения прокси к аккаунту {session_name}.", page=self.page)
            return None
        # except Exception as error:
        #     await client.disconnect()
        #     logger.exception(error)
        #     return None

    async def account_connection_menu(self):
        """
        Меню подключения аккаунтов
        """

        # Создаем текстовый элемент и добавляем его на страницу
        phone_number = ft.TextField(label="Введите номер телефона:", multiline=False, max_lines=1)

        async def connecting_number_accounts(_) -> None:
            phone_number_value = phone_number.value
            await log_and_display(f"Номер телефона: {phone_number_value}", self.page)
            # Дальнейшая обработка после записи номера телефона
            telegram_client = TelegramClient(
                f"user_data/accounts/{phone_number_value}",
                api_id=self.api_id, api_hash=self.api_hash, system_version="4.16.30-vxCUSTOM",
                proxy=reading_proxy_data_from_the_database())
            await telegram_client.connect()  # Подключаемся к Telegram
            if not await telegram_client.is_user_authorized():
                await log_and_display(f"Пользователь не авторизован", self.page)
                await telegram_client.send_code_request(phone_number_value)  # Отправка кода на телефон
                await asyncio.sleep(2)
                passww = ft.TextField(label="Введите код telegram:", multiline=True, max_lines=1)

                async def btn_click_code(_) -> None:
                    try:
                        await log_and_display(f"Код telegram: {passww.value}", self.page)
                        await telegram_client.sign_in(phone_number_value, passww.value)  # Авторизация с кодом
                        telegram_client.disconnect()
                        self.page.go("/")  # Перенаправление в настройки, если 2FA не требуется
                        self.page.update()
                    except SessionPasswordNeededError:  # Если аккаунт защищен паролем, запрашиваем пароль
                        await log_and_display(translations["ru"]["errors"]["two_factor_required"], self.page)
                        pass_2fa = ft.TextField(label="Введите пароль telegram:", multiline=False, max_lines=1)

                        async def btn_click_password(_) -> None:
                            await log_and_display(f"Пароль telegram: {pass_2fa.value}", self.page)
                            try:
                                await telegram_client.sign_in(password=pass_2fa.value)
                                await log_and_display(f"Успешная авторизация.", self.page)
                                telegram_client.disconnect()
                                self.page.go("/")  # Изменение маршрута в представлении существующих настроек
                                self.page.update()
                            except PasswordHashInvalidError:
                                await log_and_display(f"❌ Неверный пароль.", self.page)
                                await show_notification(self.page, f"⚠️ Неверный пароль. Попробуйте еще раз.")
                                self.page.go("/")  # Изменение маршрута в представлении существующих настроек
                            # except Exception as error:
                            #     logger.exception(error)

                        button_password = ft.ElevatedButton(width=WIDTH_WIDE_BUTTON, height=BUTTON_HEIGHT,
                                                            text=translations["ru"]["buttons"]["done"],
                                                            on_click=btn_click_password)  # Кнопка "Готово"
                        self.page.views.append(ft.View(controls=[pass_2fa, button_password]))
                        self.page.update()  # Обновляем страницу, чтобы интерфейс отобразился
                    except ApiIdInvalidError:
                        await log_and_display(f"[!] Неверные API ID или API Hash.", self.page)
                        await telegram_client.disconnect()  # Отключаемся от Telegram
                    except Exception as error:
                        logger.exception(error)
                        await telegram_client.disconnect()  # Отключаемся от Telegram

                self.page.views.append(ft.View(controls=[passww,
                                                         ft.ElevatedButton(width=WIDTH_WIDE_BUTTON,
                                                                           height=BUTTON_HEIGHT,
                                                                           text=translations["ru"]["buttons"]["done"],
                                                                           on_click=btn_click_code)]))  # Кнопка "Готово"
                self.page.update()  # Обновляем страницу, чтобы отобразился интерфейс для ввода кода
            self.page.update()

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
                    target_path = os.path.join(path_accounts_folder, file_name)
                    # Создаем директорию, если она не существует
                    os.makedirs(path_accounts_folder, exist_ok=True)
                    # Копируем файл
                    shutil.copy(file_path, target_path)
                    selected_files.value = f"Файл скопирован в: {target_path}"
                else:
                    selected_files.value = "Выбранный файл не является session файлом"
            else:
                selected_files.value = "Выбор файла отменен"
            selected_files.update()
            self.page.update()

        pick_files_dialog = ft.FilePicker(on_result=btn_click)  # Инициализация выбора файлов
        self.page.overlay.append(pick_files_dialog)  # Добавляем FilePicker на страницу

        self.page.views.append(
            ft.View("/account_connection_menu",
                    [await GUIProgram().key_app_bar(),
                     ft.Text(spans=[ft.TextSpan(
                         "Подключение аккаунта Telegram по номеру телефона.",
                         ft.TextStyle(
                             size=20,
                             weight=ft.FontWeight.BOLD,
                             foreground=ft.Paint(
                                 gradient=ft.PaintLinearGradient((0, 20), (150, 20), [ft.Colors.PINK,
                                                                                      ft.Colors.PURPLE])), ), ), ], ),
                     phone_number,
                     # 📞 Подключение аккаунтов по номеру телефона
                     ft.ElevatedButton(width=WIDTH_WIDE_BUTTON, height=BUTTON_HEIGHT,
                                       text="Получить код", on_click=connecting_number_accounts),

                     ft.Divider(
                         color="blue",  # Цвет линии
                         height=10,  # Расстояние от предыдущего элемента
                         thickness=1.5,  # Толщина линии
                     ),

                     ft.Text(spans=[ft.TextSpan(
                         "Подключение session аккаунтов Telegram",
                         ft.TextStyle(
                             size=20,
                             weight=ft.FontWeight.BOLD,
                             foreground=ft.Paint(
                                 gradient=ft.PaintLinearGradient((0, 20), (150, 20), [ft.Colors.PINK,
                                                                                      ft.Colors.PURPLE])), ), ), ], ),

                     ft.Text(f"Выберите session файл\n", size=15),
                     selected_files,  # Поле для отображения выбранного файла
                     ft.Column([  # Добавляет все чекбоксы и кнопку на страницу (page) в виде колонок.
                         # 🔑 Подключение session аккаунтов
                         ft.ElevatedButton(width=WIDTH_WIDE_BUTTON, height=BUTTON_HEIGHT,
                                           text=translations["ru"]["create_groups_menu"]["choose_session_files"],
                                           on_click=lambda _: pick_files_dialog.pick_files()),  # Кнопка выбора файла
                     ])]))
