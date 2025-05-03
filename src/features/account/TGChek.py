# -*- coding: utf-8 -*-
import datetime

import flet as ft

from src.core.configs import BUTTON_WIDTH, BUTTON_HEIGHT, path_accounts_folder
from src.core.localization import (main_menu, checking_accounts, checking_through_a_spam_bot_ru, validation_check_ru,
                                   renaming_accounts_ru, full_verification_ru)
from src.core.utils import find_folders
from src.features.account.TGConnect import TGConnect
from src.gui.menu import show_notification, log_and_display
from loguru import logger


class TGChek:

    def __init__(self):
        self.TGConnect = TGConnect()

    async def account_verification_menu(self, page: ft.Page):
        """
        Меню проверки аккаунтов

        :param page: Страница интерфейса Flet для отображения элементов управления.
        """
        list_view = ft.ListView(expand=10, spacing=1, padding=2, auto_scroll=True)

        async def validation_check(_) -> None:
            """Проверка валидности аккаунтов"""
            try:
                start_time = datetime.datetime.now()  # фиксируем и выводим время старта работы кода
                await log_and_display(f"▶️ Проверка аккаунтов началась.\n🕒 Время старта: {str(start_time)}", list_view,
                                      page)
                for folder in await find_folders(directory_path=path_accounts_folder, list_view=list_view, page=page):
                    await log_and_display(f"Проверка аккаунтов из папки 📁 {folder} на валидность", list_view, page)
                    await self.TGConnect.verify_all_accounts(page=page, list_view=list_view)
                await log_and_display(f"▶️ Проверка аккаунтов началась.\n🕒 Время старта: {str(start_time)}", list_view,
                                      page)
                finish = datetime.datetime.now()  # фиксируем и выводим время окончания работы кода
                await log_and_display(
                    f"🔚 Конец проверки.\n🕒 Время окончания: {finish}.\n⏳ Время работы: {finish - start_time}",
                    list_view,
                    page)
                await show_notification(page, "🔚 Проверка аккаунтов завершена")
            except Exception as error:
                logger.exception(f"❌ Ошибка: {error}")

        async def renaming_accounts(_):
            """Переименование аккаунтов"""
            try:
                start_time = datetime.datetime.now()  # фиксируем и выводим время старта работы кода
                await log_and_display(f"▶️ Проверка аккаунтов началась.\n🕒 Время старта: {str(start_time)}", list_view,
                                      page)
                for folder in await find_folders(directory_path=path_accounts_folder, list_view=list_view, page=page):
                    await log_and_display(f"Переименование аккаунтов из папки 📁 {folder}", list_view, page)
                    if folder == "invalid_account":
                        continue  # Продолжаем цикл, пропуская эту итерацию
                    else:
                        await self.TGConnect.get_account_details(page=page, folder_name=folder, list_view=list_view)
                finish = datetime.datetime.now()  # фиксируем и выводим время окончания работы кода
                await log_and_display(
                    f"🔚 Конец проверки.\n🕒 Время окончания: {finish}.\n⏳ Время работы: {finish - start_time}",
                    list_view,
                    page)
                await show_notification(page, "🔚 Проверка аккаунтов завершена")
            except Exception as error:
                logger.exception(f"❌ Ошибка: {error}")

        async def checking_for_spam_bots(_):
            """Проверка на спам ботов"""
            start_time = datetime.datetime.now()  # фиксируем и выводим время старта работы кода
            await log_and_display(f"▶️ Проверка аккаунтов началась.\n🕒 Время старта: {str(start_time)}", list_view,
                                  page)
            for folder in await find_folders(directory_path=path_accounts_folder, list_view=list_view, page=page):
                await log_and_display(f"Проверка аккаунтов из папки 📁 {folder} через спам бот", list_view, page)
                if folder == "invalid_account":
                    continue  # Продолжаем цикл, пропуская эту итерацию
                else:
                    await self.TGConnect.check_for_spam(page=page, list_view=list_view)
            finish = datetime.datetime.now()  # фиксируем и выводим время окончания работы кода
            await log_and_display(
                f"🔚 Конец проверки.\n🕒 Время окончания: {finish}.\n⏳ Время работы: {finish - start_time}", list_view,
                page)
            await show_notification(page, "🔚 Проверка аккаунтов завершена")

        async def full_verification(_):
            """
            Полная проверка аккаунтов
            """
            start_time = datetime.datetime.now()  # фиксируем и выводим время старта работы кода
            await log_and_display(f"▶️ Проверка аккаунтов началась.\n🕒 Время старта: {str(start_time)}", list_view,
                                  page)
            await validation_check(_)  # Проверка валидности аккаунтов
            await renaming_accounts(_)  # Переименование аккаунтов
            await checking_for_spam_bots(_)  # Проверка на спам ботов
            finish = datetime.datetime.now()  # фиксируем и выводим время окончания работы кода
            await log_and_display(
                f"🔚 Конец проверки.\n🕒 Время окончания: {finish}.\n⏳ Время работы: {finish - start_time}", list_view,
                page)
            await show_notification(page, "🔚 Проверка аккаунтов завершена")

        page.views.append(
            ft.View("/account_verification_menu",
                    [ft.AppBar(title=ft.Text(main_menu),
                               bgcolor=ft.colors.SURFACE_VARIANT),
                     ft.Text(spans=[ft.TextSpan(
                         checking_accounts,
                         ft.TextStyle(
                             size=20,
                             weight=ft.FontWeight.BOLD,
                             foreground=ft.Paint(
                                 gradient=ft.PaintLinearGradient((0, 20), (150, 20), [ft.colors.PINK,
                                                                                      ft.colors.PURPLE])), ), ), ], ),
                     list_view,
                     ft.Column([  # Добавляет все чекбоксы и кнопку на страницу (page) в виде колонок.
                         # 🤖 Проверка через спам бот
                         ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
                                           text=checking_through_a_spam_bot_ru,
                                           on_click=checking_for_spam_bots),
                         # ✅ Проверка на валидность
                         ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT, text=validation_check_ru,
                                           on_click=validation_check),
                         # ✏️ Переименование аккаунтов
                         ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT, text=renaming_accounts_ru,
                                           on_click=renaming_accounts),
                         # 🔍 Полная проверка
                         ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT, text=full_verification_ru,
                                           on_click=full_verification),

                     ])]))
