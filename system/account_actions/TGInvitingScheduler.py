# -*- coding: utf-8 -*-
import asyncio

import schedule
from loguru import logger

from system.account_actions.TGChek import TGChek
from system.account_actions.TGInviting import InvitingToAGroup
from system.auxiliary_functions.config import ConfigReader

hour, minutes = ConfigReader().get_hour_minutes_every_day()


async def schedule_member_invitation(page) -> None:
    """
    Запуск inviting
    """
    try:
        await TGChek().validation_check(page=page)
        await InvitingToAGroup().inviting_without_limits(page=page, account_limits=ConfigReader().get_limits())
    except Exception as error:
        logger.exception(f"❌ Ошибка: {error}")


async def run_scheduler():
    """
    Запуск планировщика
    """
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)  # Используем асинхронный sleep


def launching_invite_every_day_certain_time(page) -> None:
    """
    Запуск inviting каждый день в определенное время выбранное пользователем
    """
    try:
        schedule.every().day.at(f"{int(hour):02d}:{int(minutes):02d}").do(
            lambda: asyncio.ensure_future(schedule_member_invitation(page=page)))
        asyncio.ensure_future(run_scheduler())
    except Exception as error:
        logger.exception(f"❌ Ошибка: {error}")


def launching_an_invite_once_an_hour(page) -> None:
    """
    Запуск inviting 1 раз в час
    """
    try:
        logger.info("Запуск программы в 00 минут")
        schedule.every().hour.at(":00").do(lambda: asyncio.ensure_future(schedule_member_invitation(page=page)))
        asyncio.ensure_future(run_scheduler())
    except Exception as error:
        logger.exception(f"❌ Ошибка: {error}")


def schedule_invite(page) -> None:
    """
    Запуск автоматической отправки приглашений участникам
    """
    try:
        logger.info(f"Скрипт будет запускаться каждый день в {hour}:{minutes}")
        # Запускаем автоматизацию
        schedule.every().day.at(f"{hour}:{minutes}").do(
            lambda: asyncio.ensure_future(schedule_member_invitation(page=page)))
        asyncio.ensure_future(run_scheduler())
    except Exception as error:
        logger.exception(f"❌ Ошибка: {error}")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_forever()
