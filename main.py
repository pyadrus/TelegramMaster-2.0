from loguru import logger

from system.menu.main_menu_interface import main_menu
from system.sqlite_working_tools.sqlite_working_tools import DatabaseHandler
from system.telegram_actions.account_verification import deleting_files_by_dictionary

logger.add("user_settings/log/log.log", rotation="1 MB", compression="zip")  # Логирование программы


def launch_with_account_verification() -> None:
    """Запуск программы с проверкой аккаунтов"""
    db_handler = DatabaseHandler()
    deleting_files_by_dictionary(db_handler)
    main_menu()  # Основное меню программы


if __name__ == "__main__":
    try:
        launch_with_account_verification()  # Проверка аккаунтов
    except Exception as e:
        logger.exception(f"[!] Произошла ошибка {e}, для подробного изучения проблемы просмотрите файл log.log")

