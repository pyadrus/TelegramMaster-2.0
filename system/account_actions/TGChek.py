import datetime

from loguru import logger

from system.account_actions.TGConnect import TGConnect
from system.auxiliary_functions.auxiliary_functions import find_folders


class TGChek:

    def __init__(self):
        self.TGConnect = TGConnect()

    async def validation_check(self):
        """
        Проверка валидности аккаунтов
        """
        start = datetime.datetime.now()  # фиксируем и выводим время старта работы кода
        logger.info('Время старта: ' + str(start))
        logger.info("▶️ Проверка аккаунтов началась")

        for folder in find_folders(directory_path="user_settings/accounts"):
            logger.info(f'Проверка аккаунтов из папки 📁 {folder} на валидность')
            if folder == "invalid_account":
                logger.info(f"⛔ Пропускаем папку 📁: {folder}")
                continue  # Пропускаем эту папку
            elif folder == "banned":
                logger.info(f"⛔ Пропускаем папку 📁: {folder}")
                continue  # Пропускаем эту папку
            else:
                logger.info(f"Папка с которой работаем: {folder}")
                await self.TGConnect.verify_all_accounts(folder_name=folder)

        logger.info("🔚 Проверка аккаунтов завершена")
        finish = datetime.datetime.now()  # фиксируем и выводим время окончания работы кода
        logger.info('Время окончания: ' + str(finish))
        logger.info('Время работы: ' + str(finish - start))  # вычитаем время старта из времени окончания

    async def checking_for_spam_bots(self):
        """
        Проверка на спам ботов
        """
        start = datetime.datetime.now()  # фиксируем и выводим время старта работы кода
        logger.info('Время старта: ' + str(start))
        logger.info("▶️ Проверка аккаунтов началась")

        for folder in find_folders(directory_path="user_settings/accounts"):
            logger.info(f'Проверка аккаунтов из папки 📁 {folder} через спам бот')
            if folder == "invalid_account":
                logger.info(f"⛔ Пропускаем папку 📁: {folder}")
                continue  # Продолжаем цикл, пропуская эту итерацию
            else:
                await self.TGConnect.check_for_spam(folder_name=folder)

        logger.info("🔚 Проверка аккаунтов завершена")
        finish = datetime.datetime.now()  # фиксируем и выводим время окончания работы кода
        logger.info('Время окончания: ' + str(finish))
        logger.info('Время работы: ' + str(finish - start))  # вычитаем время старта из времени окончания

    async def renaming_accounts(self):
        """
        Переименование аккаунтов
        """
        start = datetime.datetime.now()  # фиксируем и выводим время старта работы кода
        logger.info('Время старта: ' + str(start))
        logger.info("▶️ Проверка аккаунтов началась")

        for folder in find_folders(directory_path="user_settings/accounts"):
            logger.info(f'Переименование аккаунтов из папки 📁 {folder}')
            if folder == "invalid_account":
                logger.info(f"⛔ Пропускаем папку 📁: {folder}")
                continue  # Продолжаем цикл, пропуская эту итерацию
            else:
                await self.TGConnect.get_account_details(folder_name=folder)

        logger.info("🔚 Проверка аккаунтов завершена")
        finish = datetime.datetime.now()  # фиксируем и выводим время окончания работы кода
        logger.info('Время окончания: ' + str(finish))
        logger.info('Время работы: ' + str(finish - start))  # вычитаем время старта из времени окончания

    async def full_verification(self):
        """
        Полная проверка аккаунтов
        """
        start = datetime.datetime.now()  # фиксируем и выводим время старта работы кода
        logger.info('Время старта: ' + str(start))
        logger.info("▶️ Проверка аккаунтов началась")

        await self.validation_check()  # Проверка валидности аккаунтов
        await self.renaming_accounts()  # Переименование аккаунтов
        await self.checking_for_spam_bots()  # Проверка на спам ботов

        logger.info("🔚 Проверка аккаунтов завершена")
        finish = datetime.datetime.now()  # фиксируем и выводим время окончания работы кода
        logger.info('Время окончания: ' + str(finish))
        logger.info('Время работы: ' + str(finish - start))  # вычитаем время старта из времени окончания
