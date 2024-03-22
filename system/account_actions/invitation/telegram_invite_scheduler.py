import time

import schedule

from system.account_actions.invitation.inviting_participants_telegram import invitation_from_all_accounts_program_body
from system.auxiliary_functions.global_variables import console, hour, minutes
from system.telegram_actions.account_verification import deleting_files_by_dictionary


def schedule_member_invitation() -> None:
    """Запуск inviting"""
    deleting_files_by_dictionary()
    invitation_from_all_accounts_program_body(name_database_table="members")


def launching_invite_every_day_certain_time() -> None:
    """Запуск inviting каждый день в определенное время выбранное пользователем"""
    schedule.every().day.at(f"{hour}:{minutes}").do(schedule_member_invitation)
    while True:
        schedule.run_pending()
        time.sleep(1)


def launching_an_invite_once_an_hour() -> None:
    """Запуск inviting 1 раз в час"""
    # Запускаем автоматизацию
    schedule.every().hour.at(":00").do(schedule_member_invitation)
    # Запускаем бесконечный цикл, который будет проверять, есть ли задачи для выполнения, и ждать одну секунду перед
    # следующей проверкой
    while True:
        schedule.run_pending()
        time.sleep(1)


def schedule_invite() -> None:
    """Запуск автоматической отправки приглашений участникам"""
    # Вводим час запуска программы в формате 03, 06, 23
    hour_user: str = console.input("[magenta]Введите часы (Пример: 02, 03, 06): ")
    # Вводим минуты запуска программы в формате 15, 25, 35
    minute_user: str = console.input("[magenta]Введите минуты (Пример: 02, 25, 59): ")
    console.print(f"[magenta]Скрипт будет запускаться каждый день в {hour_user}:{minute_user}")
    # Запускаем автоматизацию
    schedule.every().day.at(f"{hour_user}:{minute_user}").do(schedule_member_invitation)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    launching_an_invite_once_an_hour()
    schedule_invite()
    schedule_member_invitation()
    launching_invite_every_day_certain_time()  # Запуск inviting каждый день в определенное время
