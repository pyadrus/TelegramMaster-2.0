import asyncio

import schedule
from loguru import logger

from system.account_actions.TGChek import TGChek
from system.account_actions.TGInviting import InvitingToAGroup
from system.auxiliary_functions.config import ConfigReader

hour, minutes = ConfigReader().get_hour_minutes_every_day()


async def schedule_member_invitation() -> None:
    """Запуск inviting"""
    try:
        await TGChek().validation_check()
        await InvitingToAGroup().inviting_without_limits(account_limits=ConfigReader().get_limits())
    except Exception as e:
        logger.exception(f"Ошибка: {e}")


async def run_scheduler():
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)  # Используем асинхронный sleep


def launching_invite_every_day_certain_time() -> None:
    """Запуск inviting каждый день в определенное время выбранное пользователем"""
    try:
        schedule.every().day.at(f"{int(hour):02d}:{int(minutes):02d}").do(
            lambda: asyncio.ensure_future(schedule_member_invitation()))
        asyncio.ensure_future(run_scheduler())
    except Exception as e:
        logger.exception(f"Ошибка: {e}")


def launching_an_invite_once_an_hour() -> None:
    """Запуск inviting 1 раз в час"""
    try:
        logger.info("Запуск программы в 00 минут")
        schedule.every().hour.at(":00").do(lambda: asyncio.ensure_future(schedule_member_invitation()))
        asyncio.ensure_future(run_scheduler())
    except Exception as e:
        logger.exception(f"Ошибка: {e}")


def schedule_invite() -> None:
    """Запуск автоматической отправки приглашений участникам"""
    try:
        logger.info(f"Скрипт будет запускаться каждый день в {hour}:{minutes}")
        # Запускаем автоматизацию
        schedule.every().day.at(f"{hour}:{minutes}").do(
            lambda: asyncio.ensure_future(schedule_member_invitation()))
        asyncio.ensure_future(run_scheduler())
    except Exception as e:
        logger.exception(f"Ошибка: {e}")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    launching_an_invite_once_an_hour()  # Запуск inviting 1 раз в час
    schedule_invite()
    launching_invite_every_day_certain_time()  # Запуск inviting каждый день в определенное время
    loop.run_forever()
