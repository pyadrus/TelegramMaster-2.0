from loguru import logger
from rich import print

from system.menu.main_menu_interface import main_menu
from system.telegram_actions.account_verification import deleting_files_by_dictionary

logger.add("user_settings/log/log.log", rotation="1 MB", compression="zip")  # Логирование программы


def launch_with_account_verification() -> None:
    """Запуск программы с проверкой аккаунтов"""
    deleting_files_by_dictionary()
    main_menu()  # Основное меню программы


if __name__ == "__main__":
    try:
        launch_with_account_verification()  # Проверка аккаунтов
    except Exception as e:
        logger.exception(e)
        print("[medium_purple3][!] Произошла ошибка, для подробного изучения проблемы просмотрите файл log.log")
