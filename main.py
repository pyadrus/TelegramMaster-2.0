from loguru import logger
from rich import print

from system.menu.main_menu import main_menu
from system.telegram_actions.telegram_actions import deleting_files_by_dictionary

logger.add("setting_user/log/log.log", rotation="1 MB", compression="zip")  # Логирование программы


def launching_the_program_with_account_verification():
    """Запуск программы с проверкой аккаунтов"""
    deleting_files_by_dictionary()
    main_menu()


if __name__ == "__main__":
    try:
        launching_the_program_with_account_verification()
    except Exception as e:
        logger.exception(e)
        print("[bold red][!] Произошла ошибка, для подробного изучения проблемы просмотрите файл log.log")
