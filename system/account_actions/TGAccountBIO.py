# -*- coding: utf-8 -*-
import datetime

import flet as ft  # Импортируем библиотеку flet
from loguru import logger
from telethon import TelegramClient
from telethon import functions
from telethon.errors import (AuthKeyUnregisteredError, UsernamePurchaseAvailableError, UsernameOccupiedError,
                             UsernameInvalidError)

from system.account_actions.TGConnect import TGConnect
from system.auxiliary_functions.auxiliary_functions import find_files, find_filess
from system.auxiliary_functions.config import path_bio_folder
from system.gui.buttons import function_button_ready
from system.gui.menu_gui import log_and_display, show_notification


class AccountBIO:

    def __init__(self):
        self.directory_path = path_bio_folder
        self.extension = 'session'
        self.tg_connect = TGConnect()



    async def change_username_profile_gui(self, page: ft.Page) -> None:
        """
        Изменение био профиля Telegram в графическое окно Flet

        Аргументы:
        :param page: Страница интерфейса Flet для отображения элементов управления.
        """
        try:
            user_input = ft.TextField(label="Введите username профиля (не более 32 символов): ", multiline=True,
                                      max_lines=19)

            async def btn_click(e) -> None:
                await self.change_username_profile(page, user_input.value)
                page.go("/bio_editing")  # Изменение маршрута в представлении существующих настроек
                page.update()

            function_button_ready(page, btn_click, user_input)
        except Exception as error:
            logger.exception(f"❌ Ошибка: {error}")

    async def change_username_profile(self, page, user_input) -> None:
        """
        Изменение username профиля Telegram

        Аргументы:
        :param user_input  - новое имя пользователя
        :param page: Страница интерфейса Flet для отображения элементов управления.
        """
        try:
            for session_name in find_filess(directory_path=self.directory_path, extension=self.extension):
                logger.info(f"{session_name}")
                telegram_client: TelegramClient = await self.tg_connect.get_telegram_client(page,
                                                                                            session_name=session_name,
                                                                                            account_directory=self.directory_path)
                await telegram_client.connect()
                try:
                    await telegram_client(functions.account.UpdateUsernameRequest(username=user_input))
                    logger.info(f'Никнейм успешно обновлен на {user_input}')
                except AuthKeyUnregisteredError:
                    logger.error("❌ Ошибка соединения с профилем")
                except (UsernamePurchaseAvailableError, UsernameOccupiedError):
                    logger.error("❌ Никнейм уже занят")
                except UsernameInvalidError:
                    logger.error("❌ Неверный никнейм")
                finally:
                    await telegram_client.disconnect()
        except Exception as error:
            logger.exception(f"❌ Ошибка: {error}")

    async def change_bio_profile_gui(self, page: ft.Page) -> None:
        """
        Изменение био профиля Telegram в графическое окно Flet.

        Аргументы:
        :param page: Страница интерфейса Flet для отображения элементов управления.
        """
        try:
            user_input = ft.TextField(label="Введите описание профиля, не более 70 символов: ", multiline=True,
                                      max_lines=19)

            async def btn_click(e) -> None:
                await self.change_bio_profile(page, user_input.value)
                page.go("/bio_editing")  # Изменение маршрута в представлении существующих настроек
                page.update()

            function_button_ready(page, btn_click, user_input)
        except Exception as error:
            logger.exception(f"❌ Ошибка: {error}")

    async def change_bio_profile(self, page, user_input):
        """
        Изменение описания профиля.

        Аргументы:
        :param user_input - новое описание профиля Telegram
        :param page: Страница интерфейса Flet для отображения элементов управления.
        """

        start = datetime.datetime.now()  # фиксируем время начала выполнения кода ⏱️
        lv = ft.ListView(expand=10, spacing=1, padding=2, auto_scroll=True)
        page.controls.append(lv)  # добавляем ListView на страницу для отображения логов 📝
        page.update()  # обновляем страницу, чтобы сразу показать ListView 🔄

        # Индикация начала инвайтинга
        await log_and_display(f"▶️ Начало изменения описания профиля.\n🕒 Время старта: {str(start)}", lv, page)
        page.update()  # Обновите страницу, чтобы сразу показать сообщение 🔄

        try:
            logger.info(f"Запуск смены  описания профиля")
            for session_name in find_filess(directory_path=self.directory_path, extension=self.extension):
                logger.info(f"{session_name}")
                client = await self.tg_connect.get_telegram_client(page, session_name,
                                                                   account_directory=self.directory_path)
                await client.connect()
                while True:
                    if len(user_input) <= 70:
                        break
                    else:
                        logger.info(f"❌ Описание профиля превышает 70 символов. Пожалуйста, введите снова. Описание "
                                    f"профиля: {len(user_input)} символов")
                try:
                    result = await client(functions.account.UpdateProfileRequest(about=user_input))
                    logger.info(f'{result}\nПрофиль успешно обновлен!')
                    await client.disconnect()
                except AuthKeyUnregisteredError:
                    logger.error("❌ Ошибка соединения с профилем")
        except Exception as error:
            logger.exception(f"❌ Ошибка: {error}")

        finish = datetime.datetime.now()  # фиксируем время окончания парсинга ⏰
        await log_and_display(
            f"🔚 Конец изменения описания профиля.\n🕒 Время окончания: {finish}.\n⏳ Время работы: {finish - start}", lv, page)
        await show_notification(page, "🔚 Конец изменения описания профиля.")  # Выводим уведомление пользователю
        page.go("/bio_editing")  # переходим к основному меню инвайтинга 🏠

    async def change_name_profile_gui(self, page: ft.Page) -> None:
        """
        Изменение био профиля Telegram в графическое окно Flet

        Аргументы:
        :param page: Страница интерфейса Flet для отображения элементов управления.
        """
        try:
            user_input = ft.TextField(label="Введите имя профиля, не более 64 символов: ", multiline=True, max_lines=19)

            async def btn_click(e) -> None:
                await self.change_name_profile(page, user_input.value)
                page.go("/bio_editing")  # Изменение маршрута в представлении существующих настроек
                page.update()

            function_button_ready(page, btn_click, user_input)
        except Exception as error:
            logger.exception(f"❌ Ошибка: {error}")

    async def change_name_profile(self, page, user_input):
        """
        Изменение имени профиля

        Аргументы:
        :param user_input - новое имя пользователя
        :param page: Страница интерфейса Flet для отображения элементов управления.
        """
        try:
            for session_name in find_filess(directory_path=self.directory_path, extension=self.extension):
                logger.info(f"{session_name}")
                client = await self.tg_connect.get_telegram_client(page, session_name,
                                                                   account_directory=self.directory_path)
                await client.connect()
                try:
                    result = await client(functions.account.UpdateProfileRequest(first_name=user_input))
                    logger.info(f'{result}\nИмя успешно обновлено!')
                    await client.disconnect()
                except AuthKeyUnregisteredError:
                    logger.error("❌ Ошибка соединения с профилем")
        except Exception as error:
            logger.exception(f"❌ Ошибка: {error}")

    async def change_last_name_profile_gui(self, page: ft.Page) -> None:
        """
        Изменение био профиля Telegram в графическое окно Flet

        Аргументы:
        :param page: Страница интерфейса Flet для отображения элементов управления.
        """
        try:
            user_input = ft.TextField(label="Введите фамилию профиля, не более 64 символов: ", multiline=True,
                                      max_lines=19)

            async def btn_click(e) -> None:
                await self.change_last_name_profile(page, user_input.value)
                page.go("/bio_editing")  # Изменение маршрута в представлении существующих настроек
                page.update()

            function_button_ready(page, btn_click, user_input)
        except Exception as error:
            logger.exception(f"❌ Ошибка: {error}")

    async def change_last_name_profile(self, page, user_input):
        """
        Изменение фамилии профиля

        Аргументы:
        :param user_input - новое имя пользователя Telegram
        :param page: Страница интерфейса Flet для отображения элементов управления.
        """
        try:
            for session_name in find_filess(directory_path=self.directory_path, extension=self.extension):
                logger.info(f"{session_name}")
                client = await self.tg_connect.get_telegram_client(page, session_name,
                                                                   account_directory=self.directory_path)
                await client.connect()
                try:
                    result = await client(functions.account.UpdateProfileRequest(last_name=user_input))
                    logger.info(f'{result}\nФамилия успешно обновлена!')
                    await client.disconnect()
                except AuthKeyUnregisteredError:
                    logger.error("❌ Ошибка соединения с профилем")
        except Exception as error:
            logger.exception(f"❌ Ошибка: {error}")

    async def change_photo_profile(self, page):
        """Изменение фото профиля.

        Аргументы:
        :param page: Страница интерфейса Flet для отображения элементов управления.
        """
        try:
            for session_name in find_files(directory_path=self.directory_path, extension=self.extension):
                logger.info(f"{session_name}")
                client = await self.tg_connect.get_telegram_client(page, session_name,
                                                                   account_directory=self.directory_path)

                # Попытайтесь подключить клиента
                try:
                    await client.connect()
                    if not await client.is_connected():
                        logger.error(f"❌ Не удалось подключиться к клиенту {session_name}")
                        continue  # Перейти к следующему сеансу, если соединение не установлено

                    for photo_file in find_files(directory_path="user_settings/bio", extension='jpg'):
                        try:
                            file_path = f"user_settings/bio/{photo_file[0]}.jpg"

                            # Загрузите файл
                            result = await client(functions.photos.UploadProfilePhotoRequest(
                                file=await client.upload_file(file_path)
                            ))
                            logger.info(f'{result}\nФото успешно обновлено!')
                        except Exception as e:
                            logger.error(f"❌ Ошибка загрузки фото {photo_file[0]}: {e}")

                except AuthKeyUnregisteredError:
                    logger.error("❌ Ошибка соединения с профилем, неверный ключ авторизации.")
                except Exception as e:
                    logger.exception(f"❌ Ошибка при подключении или выполнении запроса для {session_name}: {e}")
                finally:
                    if await client.is_connected():  # Убедитесь, что клиент отключен после обработки сеанса.
                        await client.disconnect()

        except Exception as error:
            logger.exception(f"❌ Ошибка: {error}")
