from loguru import logger
from telethon import functions
from telethon.errors import AuthKeyUnregisteredError
import flet as ft  # Импортируем библиотеку flet
from system.auxiliary_functions.auxiliary_functions import find_files
from system.telegram_actions.telegram_actions import telegram_connects


class AccountRIO:

    def __init__(self, client):
        self.client = client

    def change_bio_profile_gui(self, page: ft.Page, db_handler) -> None:
        """Изменение био профиля Telegram в графическое окно Flet"""
        user_input = ft.TextField(label="Введите описание профиля, не более 70 символов: ", multiline=True,
                                  max_lines=19)

        async def btn_click(e) -> None:
            await self.change_bio_profile(db_handler, user_input.value)

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

    async def change_bio_profile(self, db_handler, user_input):
        """Изменение описания профиля"""
        entities = find_files(directory_path="user_settings/accounts/bio_accounts", extension='session')
        for file in entities:
            logger.info(f'Имя файла: {file[0]}')
            self.client = telegram_connects(db_handler, session=f"user_settings/accounts/bio_accounts/{file[0]}")

            while True:

                if len(user_input) <= 70:
                    break
                else:
                    print("Описание профиля превышает 70 символов. Пожалуйста, введите снова.")

            logger.info(f'Описание профиля: {len(user_input)} символов')
            try:
                result = self.client(functions.account.UpdateProfileRequest(about=user_input))
                logger.info(f'{result}\nПрофиль успешно обновлен!')
                self.client.disconnect()
            except AuthKeyUnregisteredError:
                logger.error("Ошибка соединения с профилем")

    def change_name_profile(self, db_handler):
        """Изменение имени профиля"""
        entities = find_files(directory_path=f"user_settings/accounts/bio_accounts", extension='session')
        for file in entities:
            self.client = telegram_connects(db_handler, session=f"user_settings/accounts/bio_accounts/{file[0]}")
            user_input: str = input('Введите имя профиля, не более 64 символов: ')
            try:
                result = self.client(functions.account.UpdateProfileRequest(first_name=user_input))
                logger.info(f'{result}\nИмя успешно обновлено!')
                self.client.disconnect()
            except AuthKeyUnregisteredError:
                logger.error("Ошибка соединения с профилем")

    def change_last_name_profile(self, db_handler):
        """Изменение фамилии профиля"""
        entities = find_files(directory_path=f"user_settings/accounts/bio_accounts", extension='session')
        for file in entities:
            self.client = telegram_connects(db_handler, session=f"user_settings/accounts/bio_accounts/{file[0]}")
            user_input: str = input('Введите фамилию профиля, не более 64 символов: ')
            try:
                result = self.client(functions.account.UpdateProfileRequest(last_name=user_input))
                logger.info(f'{result}\nФамилия успешно обновлена!')
                self.client.disconnect()
            except AuthKeyUnregisteredError:
                logger.error("Ошибка соединения с профилем")

    def change_photo_profile(self, db_handler):
        """Изменение фото профиля"""
        entities = find_files(directory_path=f"user_settings/accounts/bio_accounts", extension='session')
        for file in entities:
            self.client = telegram_connects(db_handler, session=f"user_settings/accounts/bio_accounts/{file[0]}")
            entitiess = find_files(directory_path=f"user_settings/bio", extension='jpg')
            for files in entitiess:
                try:
                    result = self.client(functions.photos.UploadProfilePhotoRequest(
                        file=self.client.upload_file(f"user_settings/bio/{files[0]}.jpg")))
                    logger.info(f'{result}\nФото успешно обновлено!')
                    self.client.disconnect()
                except AuthKeyUnregisteredError:
                    logger.error("Ошибка соединения с профилем")

    def change_username_profile(self, db_handler):
        """Изменение никнейма профиля"""
        entities = find_files(directory_path=f"user_settings/accounts/bio_accounts", extension='session')
        for file in entities:
            self.client = telegram_connects(db_handler, session=f"user_settings/accounts/bio_accounts/{file[0]}")
            user_input: str = input('Введите username профиля (не более 32 символов): ')
            try:
                result = self.client(functions.account.UpdateUsernameRequest(username=user_input))
                logger.info(f'{result}\nНикнейм успешно обновлен!')
                self.client.disconnect()
            except AuthKeyUnregisteredError:
                logger.error("Ошибка соединения с профилем")
