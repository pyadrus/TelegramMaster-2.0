# -*- coding: utf-8 -*-
from loguru import logger

from telethon.errors import *
from telethon.tl.functions.channels import LeaveChannelRequest

from system.sqlite_working_tools.sqlite_working_tools import DatabaseHandler
from system.telegram_actions.telegram_actions import telegram_connect_and_output_name


async def unsubscribe_all() -> None:
    """Отписываемся от групп, каналов, личных сообщений"""
    # Открываем базу данных для работы с аккаунтами user_settings/software_database.db
    db_handler = DatabaseHandler()  # Открываем базу с аккаунтами и с выставленными лимитами
    records: list = await db_handler.open_and_read_data("config")
    logger.info(f"Всего accounts: {len(records)}")
    for row in records:
        client = await telegram_connect_and_output_name(row, db_handler)  # Подключение к Telegram и вывод имя аккаунта
        dialogs = client.iter_dialogs()
        async for dialog in dialogs:
            logger.info(f"{dialog.name}, {dialog.id}")
            await client.delete_dialog(dialog)
        await client.disconnect()


async def unsubscribe_from_the_group(client, group_link) -> None:
    """
    Отписываемся от группы.
    :param group_link: группа или канал
    :param client: Телеграм клиент
    """
    try:
        entity = await client.get_entity(group_link)
        if entity:
            await client(LeaveChannelRequest(entity))
    except ChannelPrivateError:  # Аккаунт Telegram не может отписаться так как не имеет доступа
        logger.error(f'Группа или канал: {group_link}, является закрытым или аккаунт не имеет доступ  к {group_link}')
    finally:
        await client.disconnect()  # Разрываем соединение с Telegram
