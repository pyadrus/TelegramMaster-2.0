# -*- coding: utf-8 -*-
import flet as ft  # Импортируем библиотеку flet
from loguru import logger  # Импортируем библиотеку loguru
from telethon import functions  # Импортируем библиотеку telethon
from telethon.errors import (AuthKeyUnregisteredError, UsernamePurchaseAvailableError, UsernameOccupiedError,
                             UsernameInvalidError)

from system.account_actions.TGConnect import TGConnect
from system.config.configs import path_bio_folder
from system.gui.buttons import function_button_ready
from system.gui.menu import show_notification
from system.utils.utils import find_files, find_filess


class AccountBIO:
    """
    Класс, отвечающий за вызов функций изменения данных аккаунта Telegram.
    """

    def __init__(self):
        self.directory_path = path_bio_folder
        self.extension = 'session'
        self.tg_connect = TGConnect()
        self.account_actions = AccountActions(self.directory_path, self.extension, self.tg_connect)

    async def change_photo_profile_gui(self, page: ft.Page) -> None:
        """
        Изменение фото профиля Telegram в графическое окно Flet

        Аргументы:
        :param page: Страница интерфейса Flet для отображения элементов управления.
        """
        await self.account_actions.change_photo_profile(page)

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
                await self.account_actions.change_username_profile(page, user_input.value)
                page.go("/bio_editing")  # Изменение маршрута в представлении существующих настроек
                page.update()

            function_button_ready(page, btn_click, user_input)  # Функция для кнопки "Готово"
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
                await self.account_actions.change_bio_profile(page, user_input.value)
                page.go("/bio_editing")  # Изменение маршрута в представлении существующих настроек
                page.update()

            function_button_ready(page, btn_click, user_input)  # Функция для кнопки "Готово"
        except Exception as error:
            logger.exception(f"❌ Ошибка: {error}")

    async def change_name_profile_gui(self, page: ft.Page) -> None:
        """
        Изменение био профиля Telegram в графическое окно Flet

        Аргументы:
        :param page: Страница интерфейса Flet для отображения элементов управления.
        """
        try:
            user_input = ft.TextField(label="Введите имя профиля, не более 64 символов: ", multiline=True, max_lines=19)

            async def btn_click(e) -> None:
                await self.account_actions.change_name_profile(page, user_input.value)
                page.go("/bio_editing")  # Изменение маршрута в представлении существующих настроек
                page.update()

            function_button_ready(page, btn_click, user_input)  # Функция для кнопки "Готово"
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
                await self.account_actions.change_last_name_profile(page, user_input.value)
                page.go("/bio_editing")  # Изменение маршрута в представлении существующих настроек
                page.update()

            function_button_ready(page, btn_click, user_input)  # Функция для кнопки "Готово"
        except Exception as error:
            logger.exception(f"❌ Ошибка: {error}")


class AccountActions:
    """
    Класс, отвечающий за выполнение действий над аккаунтом Telegram.
    """

    def __init__(self, directory_path, extension, tg_connect):
        self.directory_path = directory_path  # путь к папке с аккаунтами Telegram
        self.extension = extension  # расширение файла с аккаунтом Telegram (session)
        self.tg_connect = tg_connect  # объект класса TelegramConnect (подключение к Telegram аккаунту)

    async def change_bio_profile(self, page, user_input):
        """
        Изменение описания профиля Telegram аккаунта.

        Аргументы:
        :param user_input - новое описание профиля Telegram
        :param page: Страница интерфейса Flet для отображения элементов управления.
        :return: None
        """

        try:
            logger.info(f"Запуск смены  описания профиля")
            for session_name in find_filess(directory_path=self.directory_path, extension=self.extension):
                logger.info(f"{session_name}")
                client = await self.tg_connect.get_telegram_client(page, session_name,
                                                                   account_directory=self.directory_path)
                await client.connect()

                if len(user_input) > 70:
                    await show_notification(page, f"❌ Описание профиля превышает 70 символов ({len(user_input)}).")
                    return
                try:
                    result = await client(functions.account.UpdateProfileRequest(about=user_input))
                    logger.info(f'{result}\nПрофиль успешно обновлен!')
                except AuthKeyUnregisteredError:
                    logger.error("❌ Ошибка соединения с профилем")
                finally:
                    await client.disconnect()

        except Exception as error:
            logger.exception(f"❌ Ошибка: {error}")

        await show_notification(page, "Описание профиля изменено")  # Выводим уведомление пользователю
        page.go("/bio_editing")  # переходим к основному меню изменения описания профиля 🏠

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
                client = await self.tg_connect.get_telegram_client(page,
                                                                   session_name=session_name,
                                                                   account_directory=self.directory_path)
                await client.connect()
                try:
                    await client(functions.account.UpdateUsernameRequest(username=user_input))
                    await show_notification(page, f'Никнейм успешно обновлен на {user_input}')  # Выводим уведомление пользователю
                except AuthKeyUnregisteredError:
                    await show_notification(page, "❌ Ошибка соединения с профилем")  # Выводим уведомление пользователю
                except (UsernamePurchaseAvailableError, UsernameOccupiedError):
                    await show_notification(page, "❌ Никнейм уже занят")  # Выводим уведомление пользователю
                except UsernameInvalidError:
                    await show_notification(page, "❌ Неверный никнейм")  # Выводим уведомление пользователю
                finally:
                    await client.disconnect()
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
                client = await self.tg_connect.get_telegram_client(page, session_name=session_name,
                                                                   account_directory=self.directory_path)
                await client.connect()
                try:
                    result = await client(functions.account.UpdateProfileRequest(first_name=user_input))
                    logger.info(f'{result}\nИмя успешно обновлено!')
                except AuthKeyUnregisteredError:
                    await show_notification(page, "❌ Ошибка соединения с профилем")  # Выводим уведомление пользователю
                finally:
                    await client.disconnect()
                await show_notification(page, "Имя профиля изменено")  # Выводим уведомление пользователю
                page.go("/bio_editing")  # переходим к основному меню изменения имени профиля 🏠
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

                except AuthKeyUnregisteredError:
                    await show_notification(page, "❌ Ошибка соединения с профилем")  # Выводим уведомление пользователю
                finally:
                    await client.disconnect()
                await show_notification(page, "🔚 Фамилия изменена")  # Выводим уведомление пользователю
        except Exception as error:
            logger.exception(f"❌ Ошибка: {error}")

    async def change_photo_profile(self, page):
        """Изменение фото профиля.

        Аргументы:
        :param page: Страница интерфейса Flet для отображения элементов управления.
        """
        try:
            for session_name in find_filess(directory_path=self.directory_path, extension=self.extension):
                logger.info(f"{session_name}")
                client = await self.tg_connect.get_telegram_client(page, session_name,
                                                                   account_directory=self.directory_path)


                for photo_file in find_files(directory_path="user_settings/bio", extension='jpg'):
                    try:
                        await client.connect()
                        await client(functions.photos.UploadProfilePhotoRequest(file=await client.upload_file(f"user_settings/bio/{photo_file[0]}.jpg")))
                    except AuthKeyUnregisteredError:
                        await show_notification(page, "❌ Ошибка соединения с профилем")  # Выводим уведомление пользователю
                    finally:
                        await client.disconnect()
        except Exception as error:
            logger.exception(f"❌ Ошибка: {error}")

        await show_notification(page, "🔚 Фото изменено")  # Выводим уведомление пользователю
        page.go("/bio_editing")  # переходим к основному меню изменения описания профиля 🏠

# 286
