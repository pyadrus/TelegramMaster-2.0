import time

import schedule

from system.auxiliary_functions.global_variables import console
from system.telegram_actions.telegram_actions import deleting_files_by_dictionary


def invitation_from_all_accounts_program_body() -> None:
    """Inviting по списку members"""
    deleting_files_by_dictionary()
    members_db = "members.db"
    invitation_from_all_accounts_program_body(members_db)


def launching_an_invite_by_time() -> None:
    """Запуск Inviting по времени, для автоматизации действий на сервере"""
    # Вводим час запуска программы в формате 03, 06, 23
    hour_user: str = console.input("[bold green]Введите часы (Пример: 02, 03, 06): ")
    # Вводим минуты запуска программы в формате 15, 25, 35
    minute_user: str = console.input("[bold green]Введите минуты (Пример: 02, 25, 59): ")
    console.print(f"[green]Скрипт будет запускаться каждый день в {hour_user}:{minute_user}")
    # Запускаем автоматизацию
    schedule.every().day.at(f"{hour_user}:{minute_user}").do(invitation_from_all_accounts_program_body)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    invitation_from_all_accounts_program_body()
