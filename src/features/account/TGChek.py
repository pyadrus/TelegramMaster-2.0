# -*- coding: utf-8 -*-
import datetime

from loguru import logger

from src.features.account.TGConnect import TGConnect
from src.core.utils import find_folders
from src.gui.menu import show_notification


class TGChek:

    def __init__(self):
        self.TGConnect = TGConnect()

    async def validation_check(self, page):
        """
        Проверка валидности аккаунтов

        Аргументы:
        :param page: Страница интерфейса Flet для отображения элементов управления.
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
                await self.TGConnect.verify_all_accounts(page=page, folder_name=folder)

        logger.info("🔚 Проверка аккаунтов завершена")
        finish = datetime.datetime.now()  # фиксируем и выводим время окончания работы кода
        logger.info('Время окончания: ' + str(finish))
        logger.info('Время работы: ' + str(finish - start))  # вычитаем время старта из времени окончания
        await show_notification(page, "🔚 Проверка аккаунтов завершена")

    async def checking_for_spam_bots(self, page):
        """
        Проверка на спам ботов

        Аргументы:
        :param page: Страница интерфейса Flet для отображения элементов управления.
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
                await self.TGConnect.check_for_spam(page=page, folder_name=folder)

        logger.info("🔚 Проверка аккаунтов завершена")
        finish = datetime.datetime.now()  # фиксируем и выводим время окончания работы кода
        logger.info('Время окончания: ' + str(finish))
        logger.info('Время работы: ' + str(finish - start))  # вычитаем время старта из времени окончания
        await show_notification(page, "🔚 Проверка аккаунтов завершена")

    async def renaming_accounts(self, page):
        """
        Переименование аккаунтов

        Аргументы:
        :param page: Страница интерфейса Flet для отображения элементов управления.
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
                await self.TGConnect.get_account_details(page=page, folder_name=folder)

        logger.info("🔚 Проверка аккаунтов завершена")
        finish = datetime.datetime.now()  # фиксируем и выводим время окончания работы кода
        logger.info('Время окончания: ' + str(finish))
        logger.info('Время работы: ' + str(finish - start))  # вычитаем время старта из времени окончания
        await show_notification(page, "🔚 Проверка аккаунтов завершена")

    async def full_verification(self, page):
        """
        Полная проверка аккаунтов

        Аргументы:
        :param page: Страница интерфейса Flet для отображения элементов управления.
        """
        start = datetime.datetime.now()  # фиксируем и выводим время старта работы кода
        logger.info('Время старта: ' + str(start))
        logger.info("▶️ Проверка аккаунтов началась")

        await self.validation_check(page=page)  # Проверка валидности аккаунтов
        await self.renaming_accounts(page=page)  # Переименование аккаунтов
        await self.checking_for_spam_bots(page=page)  # Проверка на спам ботов

        logger.info("🔚 Проверка аккаунтов завершена")
        finish = datetime.datetime.now()  # фиксируем и выводим время окончания работы кода
        logger.info('Время окончания: ' + str(finish))
        logger.info('Время работы: ' + str(finish - start))  # вычитаем время старта из времени окончания
        await show_notification(page, "🔚 Проверка аккаунтов завершена")
