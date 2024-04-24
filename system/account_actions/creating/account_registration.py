from loguru import logger
from telethon import functions
from telethon.errors import AuthKeyUnregisteredError

from system.telegram_actions.telegram_actions import telegram_connects


class AccountRIO:

    def __init__(self, client):
        self.client = client

    def change_profile_descriptions(self):
        """Смена описания профиля"""
        user_input: str = input('Введите описание профиля, не более 70 символов: ')
        try:
            result = self.client(functions.account.UpdateProfileRequest(about=user_input))
            logger.info(f'{result}\nПрофиль успешно обновлен!')
            self.client.disconnect()
        except AuthKeyUnregisteredError:
            logger.error("Ошибка соединения с профилем")

    def change_profile_name(self):
        """Смена имени профиля"""
        user_input: str = input('Введите имя профиля: ')
        try:
            result = self.client(functions.account.UpdateProfileRequest(first_name=user_input))
            logger.info(f'{result}\nИмя успешно обновлено!')
            self.client.disconnect()
        except AuthKeyUnregisteredError:
            logger.error("Ошибка соединения с профилем")

    def change_profile_last_name(self):
        """Смена фамилии профиля"""
        user_input: str = input('Введите фамилию профиля: ')
        try:
            result = self.client(functions.account.UpdateProfileRequest(last_name=user_input))
            logger.info(f'{result}\nФамилия успешно обновлена!')
            self.client.disconnect()
        except AuthKeyUnregisteredError:
            logger.error("Ошибка соединения с профилем")

    def change_bio_profile(self, db_handler):
        """Изменение описания профиля"""
        user_input: str = input('Введите название файла, без session: ')
        self.client = telegram_connects(db_handler, session=f"user_settings/accounts/bio_accounts/{user_input}")
        self.change_profile_descriptions()

    def change_name_profile(self, db_handler):
        """Изменение имени профиля"""
        user_input: str = input('Введите название файла, без session: ')
        self.client = telegram_connects(db_handler, session=f"user_settings/accounts/bio_accounts/{user_input}")
        self.change_profile_name()

    def change_last_name_profile(self, db_handler):
        """Изменение фамилии профиля"""
        user_input: str = input('Введите название файла, без session: ')
        self.client = telegram_connects(db_handler, session=f"user_settings/accounts/bio_accounts/{user_input}")
        self.change_profile_last_name()

    def change_photo_profile(self, db_handler):
        """Изменение фото профиля"""
        user_input: str = input('Введите название файла, без session: ')
        self.client = telegram_connects(db_handler, session=f"user_settings/accounts/bio_accounts/{user_input}")
        self.change_profile_photo()

    def change_profile_photo(self):
        """Изменение фото профиля"""
        user_input: str = input('Введите название файла c фото: ')
        try:
            result = self.client(functions.photos.UploadProfilePhotoRequest(
                file=self.client.upload_file(f"user_settings/accounts/bio_accounts/{user_input}")))
            logger.info(f'{result}\nФото успешно обновлено!')
            self.client.disconnect()
        except AuthKeyUnregisteredError:
            logger.error("Ошибка соединения с профилем")

    def change_username_profile(self, db_handler):
        """Изменение никнейма профиля"""
        user_input: str = input('Введите название файла, без session: ')
        self.client = telegram_connects(db_handler, session=f"user_settings/accounts/bio_accounts/{user_input}")
        self.change_profile_username()

    def change_profile_username(self):
        """Изменение никнейма профиля"""
        user_input: str = input('Введите никнейм: ')
        try:
            result = self.client(functions.account.UpdateUsernameRequest(username=user_input))
            logger.info(f'{result}\nНикнейм успешно обновлен!')
            self.client.disconnect()
        except AuthKeyUnregisteredError:
            logger.error("Ошибка соединения с профилем")