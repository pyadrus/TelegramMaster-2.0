# -*- coding: utf-8 -*-
import flet as ft

from src.core.configs import BUTTON_WIDTH, BUTTON_HEIGHT
from src.features.account.TGConnect import TGConnect
from src.locales.translations_loader import translations


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
            await self.TGConnect.verify_all_accounts(page=page, list_view=list_view)

        async def renaming_accounts(_):
            """Переименование аккаунтов"""
            await self.TGConnect.get_account_details(page=page, list_view=list_view)

        async def checking_for_spam_bots(_):
            """Проверка на спам ботов"""
            await self.TGConnect.check_for_spam(page=page, list_view=list_view)

        async def full_verification(_):
            """Полная проверка аккаунтов"""
            await self.TGConnect.checking_all_accounts(page=page, list_view=list_view)

        page.views.append(
            ft.View("/account_verification_menu",
                    [ft.AppBar(title=ft.Text(translations["ru"]["menu"]["main"]),
                               bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST),
                     ft.Text(spans=[ft.TextSpan(
                         translations["ru"]["menu"]["account_check"],
                         ft.TextStyle(
                             size=20,
                             weight=ft.FontWeight.BOLD,
                             foreground=ft.Paint(
                                 gradient=ft.PaintLinearGradient((0, 20), (150, 20), [ft.Colors.PINK,
                                                                                      ft.Colors.PURPLE])), ), ), ], ),
                     list_view,
                     ft.Column([  # Добавляет все чекбоксы и кнопку на страницу (page) в виде колонок.
                         # 🤖 Проверка через спам бот
                         ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
                                           text=translations["ru"]["account_verification"]["spam_check"],
                                           on_click=checking_for_spam_bots),
                         # ✅ Проверка на валидность
                         ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
                                           text=translations["ru"]["account_verification"]["validation"],
                                           on_click=validation_check),
                         # ✏️ Переименование аккаунтов
                         ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
                                           text=translations["ru"]["account_verification"]["renaming"],
                                           on_click=renaming_accounts),
                         # 🔍 Полная проверка
                         ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
                                           text=translations["ru"]["account_verification"]["full_verification"],
                                           on_click=full_verification),
                     ])]))
