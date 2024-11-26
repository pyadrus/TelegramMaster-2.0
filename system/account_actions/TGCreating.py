# -*- coding: utf-8 -*-
from loguru import logger
from telethon import functions

from system.account_actions.TGConnect import TGConnect
from system.auxiliary_functions.auxiliary_functions import find_filess
from system.auxiliary_functions.config import path_creating_folder


class CreatingGroupsAndChats:
    """
    Создание групп (чатов) в автоматическом режиме
    """

    def __init__(self):
        self.tg_connect = TGConnect()

    async def creating_groups_and_chats(self, page) -> None:
        """
        Создание групп (чатов) в автоматическом режиме
        """
        try:
            for session_name in find_filess(directory_path=path_creating_folder, extension='session'):
                client = await self.tg_connect.get_telegram_client(page, session_name,
                                                                   account_directory=path_creating_folder)

                response = await client(functions.channels.CreateChannelRequest(title='My awesome title',
                                                                                about='Description for your group',
                                                                                megagroup=True))
                logger.info(response.stringify())

        except TypeError: # Обработка ошибки при создании групп, если аккаунт не рабочий
            pass
        except Exception as error:
            logger.exception(f"❌ Ошибка: {error}")  # Логируем возникшее исключение вместе с сообщением об ошибке.
