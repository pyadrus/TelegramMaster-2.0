# -*- coding: utf-8 -*-
import flet as ft  # Импортируем библиотеку flet
from loguru import logger
from telethon import functions
from telethon.errors import (AuthKeyUnregisteredError, UsernamePurchaseAvailableError, UsernameOccupiedError,
                             UsernameInvalidError)

from system.account_actions.TGConnect import TGConnect
from system.auxiliary_functions.auxiliary_functions import find_files, find_filess
from system.auxiliary_functions.config import path_bio_folder, line_width_button, height_button
from system.localization.localization import done_button


class AccountBIO:

    def __init__(self):
        self.directory_path = path_bio_folder
        self.extension = 'session'
        self.tg_connect = TGConnect()

    @classmethod
    def function_button_ready(cls, page: ft.Page, btn_click, user_input):
        """
        Функция для кнопки "Готово"

        :param page: Страница интерфейса Flet для отображения элементов управления.
        :param btn_click:
        :param user_input:
        :return:
        """
        button = ft.ElevatedButton(width=line_width_button, height=height_button, text=done_button,
                                   on_click=btn_click)  # Кнопка "Готово"
        page.views.append(
            ft.View(
                "/bio_editing",
                [
                    user_input,
                    ft.Column(),  # Заполнитель для приветствия или другого содержимого (необязательно)
                    button,
                ],
            )
        )

    async def change_username_profile_gui(self, page: ft.Page) -> None:
        """
        Изменение био профиля Telegram в графическое окно Flet

        :param page: Страница интерфейса Flet для
        """
        try:
            user_input = ft.TextField(label="Введите username профиля (не более 32 символов): ", multiline=True,
                                      max_lines=19)

            async def btn_click(e) -> None:
                await self.change_username_profile(user_input.value)
                page.go("/bio_editing")  # Изменение маршрута в представлении существующих настроек
                page.update()

            self.function_button_ready(page, btn_click, user_input)
        except Exception as error:
            logger.exception(f"Ошибка: {error}")

    async def change_username_profile(self, user_input) -> None:
        """
        Изменение username профиля Telegram

        :param user_input  - новое имя пользователя
        """
        try:
            for session_name in find_filess(directory_path=self.directory_path, extension=self.extension):
                logger.info(f"{session_name}")
                client = await self.tg_connect.get_telegram_client(session_name, account_directory=self.directory_path)
                await client.connect()
                try:
                    await client(functions.account.UpdateUsernameRequest(username=user_input))
                    logger.info(f'Никнейм успешно обновлен на {user_input}')
                    client.disconnect()
                except AuthKeyUnregisteredError:
                    logger.error("Ошибка соединения с профилем")
                except (UsernamePurchaseAvailableError, UsernameOccupiedError):
                    logger.error("Никнейм уже занят")
                    client.disconnect()
                except UsernameInvalidError:
                    logger.error("Неверный никнейм")
                    client.disconnect()
        except Exception as error:
            logger.exception(f"Ошибка: {error}")

    async def change_bio_profile_gui(self, page: ft.Page) -> None:
        """
        Изменение био профиля Telegram в графическое окно Flet.

        :param page: Страница интерфейса Flet для
        """
        try:
            user_input = ft.TextField(label="Введите описание профиля, не более 70 символов: ", multiline=True,
                                      max_lines=19)

            async def btn_click(e) -> None:
                await self.change_bio_profile(user_input.value)
                page.go("/bio_editing")  # Изменение маршрута в представлении существующих настроек
                page.update()

            self.function_button_ready(page, btn_click, user_input)
        except Exception as error:
            logger.exception(f"Ошибка: {error}")

    async def change_bio_profile(self, user_input):
        """
        Изменение описания профиля.

        :param user_input  - новое описание профиля Telegram
        """
        try:
            logger.info(f"Запуск смены  описания профиля")
            for session_name in find_filess(directory_path=self.directory_path, extension=self.extension):
                logger.info(f"{session_name}")
                client = await self.tg_connect.get_telegram_client(session_name, account_directory=self.directory_path)
                await client.connect()
                while True:
                    if len(user_input) <= 70:
                        break
                    else:
                        logger.info(f"Описание профиля превышает 70 символов. Пожалуйста, введите снова. Описание "
                                    f"профиля: {len(user_input)} символов")
                try:
                    result = await client(functions.account.UpdateProfileRequest(about=user_input))
                    logger.info(f'{result}\nПрофиль успешно обновлен!')
                    await client.disconnect()
                except AuthKeyUnregisteredError:
                    logger.error("Ошибка соединения с профилем")
        except Exception as error:
            logger.exception(f"Ошибка: {error}")

    async def change_name_profile_gui(self, page: ft.Page) -> None:
        """
        Изменение био профиля Telegram в графическое окно Flet

        :param page: Страница интерфейса Flet для
        """
        try:
            user_input = ft.TextField(label="Введите имя профиля, не более 64 символов: ", multiline=True, max_lines=19)

            async def btn_click(e) -> None:
                await self.change_name_profile(user_input.value)
                page.go("/bio_editing")  # Изменение маршрута в представлении существующих настроек
                page.update()

            self.function_button_ready(page, btn_click, user_input)
        except Exception as error:
            logger.exception(f"Ошибка: {error}")

    async def change_name_profile(self, user_input):
        """
        Изменение имени профиля

        :param user_input  - новое имя пользователя
        """
        try:
            for session_name in find_filess(directory_path=self.directory_path, extension=self.extension):
                logger.info(f"{session_name}")
                client = await self.tg_connect.get_telegram_client(session_name, account_directory=self.directory_path)
                await client.connect()
                try:
                    result = await client(functions.account.UpdateProfileRequest(first_name=user_input))
                    logger.info(f'{result}\nИмя успешно обновлено!')
                    await client.disconnect()
                except AuthKeyUnregisteredError:
                    logger.error("Ошибка соединения с профилем")
        except Exception as error:
            logger.exception(f"Ошибка: {error}")

    async def change_last_name_profile_gui(self, page: ft.Page) -> None:
        """
        Изменение био профиля Telegram в графическое окно Flet

        :param page: Страница интерфейса Flet для
        """
        try:
            user_input = ft.TextField(label="Введите фамилию профиля, не более 64 символов: ", multiline=True,
                                      max_lines=19)

            async def btn_click(e) -> None:
                await self.change_last_name_profile(user_input.value)
                page.go("/bio_editing")  # Изменение маршрута в представлении существующих настроек
                page.update()

            self.function_button_ready(page, btn_click, user_input)
        except Exception as error:
            logger.exception(f"Ошибка: {error}")

    async def change_last_name_profile(self, user_input):
        """
        Изменение фамилии профиля

        :param user_input  - новое имя пользователя Telegram
        """
        try:
            for session_name in find_filess(directory_path=self.directory_path, extension=self.extension):
                logger.info(f"{session_name}")
                client = await self.tg_connect.get_telegram_client(session_name, account_directory=self.directory_path)
                await client.connect()
                try:
                    result = await client(functions.account.UpdateProfileRequest(last_name=user_input))
                    logger.info(f'{result}\nФамилия успешно обновлена!')
                    await client.disconnect()
                except AuthKeyUnregisteredError:
                    logger.error("Ошибка соединения с профилем")
        except Exception as error:
            logger.exception(f"Ошибка: {error}")

    async def change_photo_profile(self):
        """Изменение фото профиля."""
        try:
            for session_name in find_filess(directory_path=self.directory_path, extension=self.extension):
                logger.info(f"{session_name}")
                client = await self.tg_connect.get_telegram_client(session_name, account_directory=self.directory_path)
                await client.connect()
                for photo_file in find_files(directory_path="user_settings/bio", extension='jpg'):
                    try:
                        result = await client(functions.photos.UploadProfilePhotoRequest(
                            file=await client.upload_file(f"user_settings/bio/{photo_file[0]}.jpg")
                        ))
                        logger.info(f'{result}\nФото успешно обновлено!')
                    except AuthKeyUnregisteredError:
                        logger.error("Ошибка соединения с профилем")
                    finally:
                        await client.disconnect()
        except Exception as error:
            logger.exception(f"Ошибка: {error}")
