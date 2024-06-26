# -*- coding: utf-8 -*-
from loguru import logger

from system.auxiliary_functions.global_variables import ConfigReader
from system.sqlite_working_tools.sqlite_working_tools import DatabaseHandler


class SettingLimits:
    """Лимиты на действия TelegramMaster"""

    def __init__(self):
        self.db_handler = DatabaseHandler()
        self.config_reader = ConfigReader()
        self.account_limits = self.config_reader.get_limits()
        self.account_limits_none = None

    async def get_usernames_with_limits(self, table_name) -> list:
        """Получение списка пользователей из базы данных с учетом лимитов"""
        logger.info(f"Лимит на аккаунт: {self.account_limits}")
        number_usernames: list = await self.db_handler.open_db_func_lim(table_name=table_name,
                                                                        account_limit=self.account_limits)
        logger.info(f"Всего username: {len(number_usernames)}")
        return number_usernames

    async def get_usernames_without_limits(self, table_name) -> list:
        """Получение списка пользователей из базы данных без учета лимитов"""
        logger.info(f"Лимит на аккаунт (без ограничений)")
        number_usernames: list = await self.db_handler.open_db_func_lim(table_name=table_name,
                                                                        account_limit=self.account_limits_none)
        logger.info(f"Всего username: {len(number_usernames)}")
        return number_usernames
