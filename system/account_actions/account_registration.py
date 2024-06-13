import flet as ft  # Импортируем библиотеку flet
from loguru import logger
from telethon import functions
from telethon.errors import AuthKeyUnregisteredError

from system.account_actions.TGChecking import account_verification_for_inviting
from system.account_actions.TGConnect import TGConnect
from system.account_actions.invitation.inviting_participants_telegram import InvitingToAGroup
from system.auxiliary_functions.auxiliary_functions import find_files


class AccountRIO:

    def __init__(self, client):
        self.client = client

    def change_bio_profile_gui(self, page: ft.Page) -> None:
        """Изменение био профиля Telegram в графическое окно Flet"""
        user_input = ft.TextField(label="Введите описание профиля, не более 70 символов: ", multiline=True,
                                  max_lines=19)

        async def btn_click(e) -> None:
            await self.change_bio_profile(user_input.value)
            page.go("/bio_editing")  # Изменение маршрута в представлении существующих настроек
            page.update()

        button = ft.ElevatedButton("Готово", on_click=btn_click)
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

    async def change_bio_profile(self, user_input):
        """Изменение описания профиля"""
        logger.info(f"Запуск смены  описания профиля")
        await account_verification_for_inviting(directory_path="user_settings/accounts/bio",
                                                extension="session")  # Вызываем метод для проверки аккаунтов
        inviting_to_a_group = InvitingToAGroup()
        tg_connect = TGConnect()
        accounts = await inviting_to_a_group.reading_the_list_of_accounts_from_the_database()
        for account in accounts:
            logger.info(f"{account[0]}")
            """Получение ссылки для инвайтинга"""
            links_inviting = await inviting_to_a_group.getting_an_invitation_link_from_the_database()
            for link in links_inviting:
                logger.info(f"{link[0]}")
                proxy = await tg_connect.reading_proxies_from_the_database()
                client = await tg_connect.connecting_to_telegram(account[0], proxy,
                                                                 "user_settings/accounts/bio")
                await client.connect()
                while True:
                    if len(user_input) <= 70:
                        break
                    else:
                        logger.info("Описание профиля превышает 70 символов. Пожалуйста, введите снова.")
                logger.info(f'Описание профиля: {len(user_input)} символов')
                try:
                    result = self.client(functions.account.UpdateProfileRequest(about=user_input))
                    logger.info(f'{result}\nПрофиль успешно обновлен!')
                    self.client.disconnect()
                except AuthKeyUnregisteredError:
                    logger.error("Ошибка соединения с профилем")

    def change_name_profile_gui(self, page: ft.Page, db_handler) -> None:
        """Изменение био профиля Telegram в графическое окно Flet"""
        user_input = ft.TextField(label="Введите имя профиля, не более 64 символов: ", multiline=True,
                                  max_lines=19)

        async def btn_click(e) -> None:
            await self.change_name_profile(db_handler, user_input.value)
            page.go("/bio_editing")  # Изменение маршрута в представлении существующих настроек
            page.update()

        button = ft.ElevatedButton("Готово", on_click=btn_click)
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

    async def change_name_profile(self, db_handler, user_input):
        """Изменение имени профиля"""
        entities = find_files(directory_path=f"user_settings/accounts/bio_accounts", extension='session')
        for file in entities:
            self.client = await telegram_connects(db_handler, session=f"user_settings/accounts/bio_accounts/{file[0]}")
            # user_input: str = input('Введите имя профиля, не более 64 символов: ')
            try:
                result = self.client(functions.account.UpdateProfileRequest(first_name=user_input))
                logger.info(f'{result}\nИмя успешно обновлено!')
                self.client.disconnect()
            except AuthKeyUnregisteredError:
                logger.error("Ошибка соединения с профилем")

    def change_last_name_profile_gui(self, page: ft.Page, db_handler) -> None:
        """Изменение био профиля Telegram в графическое окно Flet"""
        user_input = ft.TextField(label="Введите фамилию профиля, не более 64 символов: ", multiline=True,
                                  max_lines=19)

        async def btn_click(e) -> None:
            await self.change_last_name_profile(db_handler, user_input.value)
            page.go("/bio_editing")  # Изменение маршрута в представлении существующих настроек
            page.update()

        button = ft.ElevatedButton("Готово", on_click=btn_click)
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

    async def change_last_name_profile(self, db_handler, user_input):
        """Изменение фамилии профиля"""
        entities = find_files(directory_path=f"user_settings/accounts/bio_accounts", extension='session')
        for file in entities:
            self.client = await telegram_connects(db_handler, session=f"user_settings/accounts/bio_accounts/{file[0]}")
            # user_input: str = input('Введите фамилию профиля, не более 64 символов: ')
            try:
                result = self.client(functions.account.UpdateProfileRequest(last_name=user_input))
                logger.info(f'{result}\nФамилия успешно обновлена!')
                self.client.disconnect()
            except AuthKeyUnregisteredError:
                logger.error("Ошибка соединения с профилем")

    async def change_photo_profile(self, db_handler):
        """Изменение фото профиля."""
        entities = find_files(directory_path="user_settings/accounts/bio_accounts", extension='session')
        for file in entities:
            self.client = await telegram_connects(db_handler, session=f"user_settings/accounts/bio_accounts/{file[0]}")
            photo_files = find_files(directory_path="user_settings/bio", extension='jpg')
            for photo_file in photo_files:
                try:
                    file_path = f"user_settings/bio/{photo_file[0]}.jpg"
                    result = await self.client(functions.photos.UploadProfilePhotoRequest(
                        file=await self.client.upload_file(file_path)
                    ))
                    logger.info(f'{result}\nФото успешно обновлено!')
                except AuthKeyUnregisteredError:
                    logger.error("Ошибка соединения с профилем")
                except Exception as e:
                    logger.error(f"Ошибка обновления фото профиля: {e}")
                finally:
                    await self.client.disconnect()

    def change_username_profile_gui(self, page: ft.Page, db_handler) -> None:
        """Изменение био профиля Telegram в графическое окно Flet"""
        user_input = ft.TextField(label="Введите username профиля (не более 32 символов): ", multiline=True,
                                  max_lines=19)

        async def btn_click(e) -> None:
            await self.change_username_profile(db_handler, user_input.value)
            page.go("/bio_editing")  # Изменение маршрута в представлении существующих настроек
            page.update()

        button = ft.ElevatedButton("Готово", on_click=btn_click)
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

    async def change_username_profile(self, db_handler, user_input):
        """Изменение никнейма профиля"""
        entities = find_files(directory_path=f"user_settings/accounts/bio_accounts", extension='session')
        for file in entities:
            self.client = await telegram_connects(db_handler, session=f"user_settings/accounts/bio_accounts/{file[0]}")
            try:
                result = self.client(functions.account.UpdateUsernameRequest(username=user_input))
                logger.info(f'{result}\nНикнейм успешно обновлен!')
                self.client.disconnect()
            except AuthKeyUnregisteredError:
                logger.error("Ошибка соединения с профилем")
