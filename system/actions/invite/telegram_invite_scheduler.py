import time

import schedule

from system.actions.invite.inviting_participants_telegram import invitation_from_all_accounts_program_body
from system.auxiliary_functions.global_variables import console
from system.telegram_actions.telegram_actions import deleting_files_by_dictionary


def schedule_member_invitation():
    """Запуск inviting"""
    invitation_from_all_accounts_program_body(name_database_table="members")


def launching_an_invite_once_an_hour():
    """Запуск inviting 1 раз в час"""
    # Запускаем автоматизацию
    schedule.every().hour.at(":00").do(schedule_member_invitation)
    # Запускаем бесконечный цикл, который будет проверять, есть ли задачи для выполнения, и ждать одну секунду перед
    # следующей проверкой
    while True:
        schedule.run_pending()
        time.sleep(1)


def invite_members() -> None:
    """Отправка приглашений всем участникам из базы данных"""
    deleting_files_by_dictionary()
    members_db = "members.db"
    invite_members(members_db)


def schedule_invite() -> None:
    """Запуск автоматической отправки приглашений участникам"""
    # Вводим час запуска программы в формате 03, 06, 23
    hour_user: str = console.input("[bold green]Введите часы (Пример: 02, 03, 06): ")
    # Вводим минуты запуска программы в формате 15, 25, 35
    minute_user: str = console.input("[bold green]Введите минуты (Пример: 02, 25, 59): ")
    console.print(f"[green]Скрипт будет запускаться каждый день в {hour_user}:{minute_user}")
    # Запускаем автоматизацию
    schedule.every().day.at(f"{hour_user}:{minute_user}").do(invite_members)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    invite_members()
