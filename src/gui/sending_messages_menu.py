# -*- coding: utf-8 -*-
import flet as ft

from src.core.configs import BUTTON_HEIGHT, BUTTON_WIDTH
from src.core.localization import (sending_messages_via_chats_ru, sending_personal_messages_with_limits_ru,
                                   sending_messages, main_menu)


def create_menu_view(title: str, buttons: list[tuple[str, str]]) -> ft.View:
    """
    Создает представление меню с заголовком и кнопками.

    :param title: Заголовок меню.
    :param buttons: Список кортежей (текст кнопки, маршрут перехода).
    :return: Объект ft.View.
    """
    return ft.View(
        route="/sending_messages",
        controls=[
            ft.AppBar(title=ft.Text(main_menu), bgcolor=ft.colors.SURFACE_VARIANT),
            ft.Text(
                spans=[
                    ft.TextSpan(
                        title,
                        ft.TextStyle(
                            size=20,
                            weight=ft.FontWeight.BOLD,
                            foreground=ft.Paint(
                                gradient=ft.PaintLinearGradient(
                                    (0, 20), (150, 20), [ft.colors.PINK, ft.colors.PURPLE]
                                )), ), ), ]),
            ft.Column([
                ft.ElevatedButton(
                    text=text, width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
                    on_click=lambda _, route=route: _.page.go(route)
                ) for text, route in buttons
            ])])


async def display_message_distribution_menu(page: ft.Page):
    """Отображает главное меню рассылки сообщений."""
    page.views.append(
        create_menu_view(
            sending_messages,
            [
                # 💬 Рассылка сообщений по чатам
                (sending_messages_via_chats_ru, "/sending_messages_files_via_chats"),
                # 📨 Отправка сообщений в личку
                (sending_personal_messages_with_limits_ru, "/sending_files_to_personal_account_with_limits"),
            ]))
