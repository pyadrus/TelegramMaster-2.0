from loguru import logger

from system.auxiliary_functions.global_variables import logger_info
from system.menu.main_menu_interface import main_menu
from system.sqlite_working_tools.sqlite_working_tools import DatabaseHandler
from system.telegram_actions.account_verification import deleting_files_by_dictionary


def launch_with_account_verification() -> None:
    """Запуск программы с проверкой аккаунтов"""

    logger_info.info("[deadly] Это информационное сообщение.")
    db_handler = DatabaseHandler()
    deleting_files_by_dictionary(db_handler)
    main_menu()  # Основное меню программы


if __name__ == "__main__":
    try:
        launch_with_account_verification()  # Проверка аккаунтов
    except Exception as e:
        logger.exception(f"[!] Произошла ошибка {e}, для подробного изучения проблемы просмотрите файл log.log")
