import time

import schedule
from loguru import logger
# from system.account_actions.invitation.inviting_participants_telegram import invitation_from_all_accounts_program_body
from system.auxiliary_functions.global_variables import ConfigReader
from system.sqlite_working_tools.sqlite_working_tools import DatabaseHandler
from system.telegram_actions.account_verification import deleting_files_by_dictionary

configs_reader = ConfigReader()
hour, minutes = configs_reader.get_hour_minutes_every_day()


def schedule_member_invitation() -> None:
    """Запуск inviting"""
    deleting_files_by_dictionary(DatabaseHandler())
    # invitation_from_all_accounts_program_body(name_database_table="members", db_handler=DatabaseHandler())


def launching_invite_every_day_certain_time() -> None:
    """Запуск inviting каждый день в определенное время выбранное пользователем"""
    schedule.every().day.at(f"{int(hour):02d}:{int(minutes):02d}").do(schedule_member_invitation)
    while True:
        schedule.run_pending()
        time.sleep(1)


def launching_an_invite_once_an_hour() -> None:
    """Запуск inviting 1 раз в час"""
    schedule.every().hour.at(":00").do(schedule_member_invitation)  # Запускаем автоматизацию
    # Запускаем бесконечный цикл, который будет проверять, есть ли задачи для выполнения, и ждать одну секунду перед
    # следующей проверкой
    while True:
        schedule.run_pending()
        time.sleep(1)


def schedule_invite() -> None:
    """Запуск автоматической отправки приглашений участникам"""
    # Вводим час запуска программы в формате 03, 06, 23
    hour_user: str = input("Введите часы (Пример: 02, 03, 06): ")
    # Вводим минуты запуска программы в формате 15, 25, 35
    minute_user: str = input("Введите минуты (Пример: 02, 25, 59): ")
    logger.info(f"Скрипт будет запускаться каждый день в {hour_user}:{minute_user}")
    # Запускаем автоматизацию
    schedule.every().day.at(f"{hour_user}:{minute_user}").do(schedule_member_invitation)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    launching_an_invite_once_an_hour()  # Запуск inviting 1 раз в час
    schedule_invite()
    launching_invite_every_day_certain_time()  # Запуск inviting каждый день в определенное время
