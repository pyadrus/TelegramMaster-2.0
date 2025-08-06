# -*- coding: utf-8 -*-
from loguru import logger
from telethon.sessions import StringSession
from telethon.sync import TelegramClient

from src.core.configs import (path_accounts_folder)
from src.gui.gui import log_and_display


async def getting_account_data(client, page):
    """Получаем данные аккаунта"""
    me = await client.get_me()
    logger.info(f"🧾 Аккаунт: {me.first_name} {me.last_name} | @{me.username} | ID: {me.id} | Phone: {me.phone}")
    await log_and_display(
        f"🧾 Аккаунт: {me.first_name} {me.last_name} | @{me.username} | ID: {me.id} | Phone: {me.phone}", page)


async def get_string_session(session_name):
    """Получение строки сессии"""

    client = TelegramClient(
        session=f"{path_accounts_folder}/{session_name}",
        api_id=7655060,
        api_hash="cc1290cd733c1f1d407598e5a31be4a8",
        system_version="4.16.30-vxCUSTOM",
    )
    await client.connect()
    logger.info(f"✨ STRING SESSION: {StringSession.save(client.session)}")
    session_string = StringSession.save(client.session)
    await client.disconnect()
    return session_string
