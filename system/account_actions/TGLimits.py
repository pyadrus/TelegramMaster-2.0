# -*- coding: utf-8 -*-
from loguru import logger

from system.sqlite_working_tools.sqlite_working_tools import DatabaseHandler


class SettingLimits:
    """Лимиты на действия TelegramMaster"""

    def __init__(self):
        self.db_handler = DatabaseHandler()

    async def get_usernames_with_limits(self, table_name, account_limits) -> list:
        """Получение списка пользователей из базы данных с учетом лимитов"""
        logger.info(f"Лимит на аккаунт: {account_limits}")
        number_usernames: list = await self.db_handler.open_db_func_lim(table_name=table_name,
                                                                        account_limit=account_limits)
        logger.info(f"Всего username: {len(number_usernames)}")
        return number_usernames
