import asyncio

import schedule
from loguru import logger

from system.account_actions.TGConnect import TGConnect
from system.account_actions.TGInviting import InvitingToAGroup
from system.auxiliary_functions.global_variables import ConfigReader

hour, minutes = ConfigReader().get_hour_minutes_every_day()


async def schedule_member_invitation() -> None:
    """Запуск inviting"""
    await TGConnect().verify_account(account_directory="user_settings/accounts/inviting",
                                     session_name="session")  # Вызываем метод для проверки аккаунтов
    await InvitingToAGroup().inviting_without_limits(account_limits=ConfigReader().get_limits())


async def run_scheduler():
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)  # Используем асинхронный sleep


def launching_invite_every_day_certain_time() -> None:
    """Запуск inviting каждый день в определенное время выбранное пользователем"""
    schedule.every().day.at(f"{int(hour):02d}:{int(minutes):02d}").do(
        lambda: asyncio.ensure_future(schedule_member_invitation()))
    asyncio.ensure_future(run_scheduler())


def launching_an_invite_once_an_hour() -> None:
    """Запуск inviting 1 раз в час"""
    logger.info("Запуск программы в 00 минут")
    schedule.every().hour.at(":00").do(lambda: asyncio.ensure_future(schedule_member_invitation()))
    asyncio.ensure_future(run_scheduler())


def schedule_invite() -> None:
    """Запуск автоматической отправки приглашений участникам"""
    logger.info(f"Скрипт будет запускаться каждый день в {hour}:{minutes}")
    # Запускаем автоматизацию
    schedule.every().day.at(f"{hour}:{minutes}").do(
        lambda: asyncio.ensure_future(schedule_member_invitation()))
    asyncio.ensure_future(run_scheduler())


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    launching_an_invite_once_an_hour()  # Запуск inviting 1 раз в час
    schedule_invite()
    launching_invite_every_day_certain_time()  # Запуск inviting каждый день в определенное время
    loop.run_forever()
