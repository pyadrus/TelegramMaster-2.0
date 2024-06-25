# -*- coding: utf-8 -*-
import flet as ft  # Импортируем библиотеку flet
from loguru import logger
from telethon import functions
from telethon.errors import AuthKeyUnregisteredError, UsernamePurchaseAvailableError, UsernameOccupiedError, \
    UsernameInvalidError

from system.account_actions.TGConnect import TGConnect
from system.auxiliary_functions.auxiliary_functions import find_files


class AccountBIO:

    def __init__(self):
        self.directory_path = "user_settings/accounts/bio"
        self.extension = 'session'

    def function_button_ready(self, page: ft.Page, button, user_input):

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

    def change_username_profile_gui(self, page: ft.Page) -> None:
        """Изменение био профиля Telegram в графическое окно Flet"""
        user_input = ft.TextField(label="Введите username профиля (не более 32 символов): ", multiline=True,
                                  max_lines=19)

        async def btn_click(e) -> None:
            await self.change_username_profile(user_input.value)
            page.go("/bio_editing")  # Изменение маршрута в представлении существующих настроек
            page.update()

        button = ft.ElevatedButton("Готово", on_click=btn_click)
        self.function_button_ready(page, button, user_input)

    async def change_username_profile(self, user_input) -> None:
        """
        Изменение username профиля Telegram
        :param user_input  - новое имя пользователя
        """
        entities = find_files(directory_path=self.directory_path, extension=self.extension)
        for file in entities:
            logger.info(f"{file[0]}")
            tg_connect = TGConnect()
            proxy = await tg_connect.reading_proxies_from_the_database()
            client = await tg_connect.connecting_to_telegram(file[0], proxy, self.directory_path)
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

    def change_bio_profile_gui(self, page: ft.Page) -> None:
        """Изменение био профиля Telegram в графическое окно Flet"""
        user_input = ft.TextField(label="Введите описание профиля, не более 70 символов: ", multiline=True,
                                  max_lines=19)

        async def btn_click(e) -> None:
            await self.change_bio_profile(user_input.value)
            page.go("/bio_editing")  # Изменение маршрута в представлении существующих настроек
            page.update()

        button = ft.ElevatedButton("Готово", on_click=btn_click)
        self.function_button_ready(page, button, user_input)

    async def change_bio_profile(self, user_input):
        """Изменение описания профиля"""
        logger.info(f"Запуск смены  описания профиля")
        entities = find_files(directory_path=self.directory_path, extension=self.extension)
        for file in entities:
            logger.info(f"{file[0]}")
            tg_connect = TGConnect()
            proxy = await tg_connect.reading_proxies_from_the_database()
            client = await tg_connect.connecting_to_telegram(file[0], proxy, self.directory_path)
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

    def change_name_profile_gui(self, page: ft.Page) -> None:
        """Изменение био профиля Telegram в графическое окно Flet"""
        user_input = ft.TextField(label="Введите имя профиля, не более 64 символов: ", multiline=True,
                                  max_lines=19)

        async def btn_click(e) -> None:
            await self.change_name_profile(user_input.value)
            page.go("/bio_editing")  # Изменение маршрута в представлении существующих настроек
            page.update()

        button = ft.ElevatedButton("Готово", on_click=btn_click)
        self.function_button_ready(page, button, user_input)

    async def change_name_profile(self, user_input):
        """Изменение имени профиля"""
        entities = find_files(directory_path=self.directory_path, extension=self.extension)
        for file in entities:
            logger.info(f"{file[0]}")
            tg_connect = TGConnect()
            proxy = await tg_connect.reading_proxies_from_the_database()
            client = await tg_connect.connecting_to_telegram(file[0], proxy, self.directory_path)
            await client.connect()
            try:
                result = await client(functions.account.UpdateProfileRequest(first_name=user_input))
                logger.info(f'{result}\nИмя успешно обновлено!')
                await client.disconnect()
            except AuthKeyUnregisteredError:
                logger.error("Ошибка соединения с профилем")

    def change_last_name_profile_gui(self, page: ft.Page) -> None:
        """Изменение био профиля Telegram в графическое окно Flet"""
        user_input = ft.TextField(label="Введите фамилию профиля, не более 64 символов: ", multiline=True,
                                  max_lines=19)

        async def btn_click(e) -> None:
            await self.change_last_name_profile(user_input.value)
            page.go("/bio_editing")  # Изменение маршрута в представлении существующих настроек
            page.update()

        button = ft.ElevatedButton("Готово", on_click=btn_click)
        self.function_button_ready(page, button, user_input)

    async def change_last_name_profile(self, user_input):
        """Изменение фамилии профиля"""
        entities = find_files(directory_path=self.directory_path, extension=self.extension)
        for file in entities:
            logger.info(f"{file[0]}")
            tg_connect = TGConnect()
            proxy = await tg_connect.reading_proxies_from_the_database()
            client = await tg_connect.connecting_to_telegram(file[0], proxy, self.directory_path)
            await client.connect()
            try:
                result = await client(functions.account.UpdateProfileRequest(last_name=user_input))
                logger.info(f'{result}\nФамилия успешно обновлена!')
                await client.disconnect()
            except AuthKeyUnregisteredError:
                logger.error("Ошибка соединения с профилем")

    async def change_photo_profile(self):
        """Изменение фото профиля."""
        entities = find_files(directory_path=self.directory_path, extension=self.extension)
        for file in entities:
            logger.info(f"{file[0]}")
            tg_connect = TGConnect()
            proxy = await tg_connect.reading_proxies_from_the_database()
            client = await tg_connect.connecting_to_telegram(file[0], proxy, self.directory_path)
            await client.connect()
            photo_files = find_files(directory_path="user_settings/bio", extension='jpg')
            for photo_file in photo_files:
                try:
                    file_path = f"user_settings/bio/{photo_file[0]}.jpg"
                    result = await client(functions.photos.UploadProfilePhotoRequest(
                        file=await client.upload_file(file_path)
                    ))
                    logger.info(f'{result}\nФото успешно обновлено!')
                except AuthKeyUnregisteredError:
                    logger.error("Ошибка соединения с профилем")
                finally:
                    await client.disconnect()
