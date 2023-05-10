# -*- coding: utf-8 -*-
from loguru import logger
from rich import print

from system.menu.main_menu import main_menu

logger.add("setting_user/log/log.log", rotation="1 MB", compression="zip")  # Логирование программы


def main_restart():
    """Запуск программы с проверкой аккаунтов"""
    main_menu()


if __name__ == "__main__":
    try:
        main_restart()
    except Exception as e:
        logger.exception(e)
        print("[bold red][!] Произошла ошибка, для подробного изучения проблемы просмотрите файл log.log")
