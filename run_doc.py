# -*- coding: utf-8 -*-
# import os
# import subprocess
# import sys

# # Путь к корню проекта (где находится scr/)
# project_root = os.path.dirname(os.path.abspath(__file__))
#
# # Команды с указанием PYTHONPATH
# commands = [
#     [sys.executable, "main.py"],  # запускает TelegramMaster 2.0
#     [sys.executable, "docs/app.py"],  # Запускает документацию
# ]
#
# # Установить PYTHONPATH на корень проекта
# env = os.environ.copy()
# env["PYTHONPATH"] = project_root
#
# processes = [subprocess.Popen(cmd, env=env) for cmd in commands]

"""Запуск документации"""
from docs.app import start_app

start_app()