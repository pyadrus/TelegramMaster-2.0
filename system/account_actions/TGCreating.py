# -*- coding: utf-8 -*-
from loguru import logger
from telethon import functions

from system.account_actions.TGConnect import TGConnect
from system.auxiliary_functions.auxiliary_functions import find_files


class CreatingGroupsAndChats:
    """Создание групп (чатов) в автоматическом режиме"""

    def __init__(self):
        self.tg_connect = TGConnect()

    async def creating_groups_and_chats(self) -> None:
        """Создание групп (чатов) в автоматическом режиме"""
        entities = find_files(directory_path="user_settings/accounts/creating", extension='session')
        for file in entities:
            client = await self.tg_connect.get_telegram_client(file, account_directory="user_settings/accounts/creating")

            response = await client(functions.channels.CreateChannelRequest(title='My awesome title',
                                                                            about='Description for your group',
                                                                            megagroup=True))
            logger.info(response.stringify())
