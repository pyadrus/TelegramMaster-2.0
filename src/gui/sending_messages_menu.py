# -*- coding: utf-8 -*-
import flet as ft

from src.core.configs import BUTTON_HEIGHT, BUTTON_WIDTH
from src.core.localization import (sending_messages_via_chats_ru, sending_messages_files_via_chats_ru,
                                   sending_personal_messages_with_limits_ru,
                                   sending_files_to_personal_account_with_limits_ru,
                                   sending_messages, main_menu, clearing_generated_chat_list,
                                   forming_list_of_chats_channels_ru
                                   )


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


async def sending_personal_messages_with_limits_menu(page: ft.Page):
    """Меню 📨 Отправка сообщений в личку"""
    page.views.append(
        create_menu_view(
            "📨 Отправка сообщений в личку",
            [
                # 📨 Отправка сообщений в личку
                (sending_personal_messages_with_limits_ru, "/sending_personal_messages_with_limits"),
                # 📁 Отправка файлов в личку
                (sending_files_to_personal_account_with_limits_ru, "/sending_files_to_personal_account_with_limits"),
            ]))


async def sending_messages_via_chats_menu(page: ft.Page):
    """Меню 💬 Рассылка сообщений по чатам"""
    page.views.append(
        create_menu_view(
            "💬 Рассылка сообщений по чатам",
            [
                # 💬📂 Рассылка сообщений + файлов по чатам
                (sending_messages_files_via_chats_ru, "/sending_messages_files_via_chats"),
                # 🧹 Очистка сформированного списка чатов
                (clearing_generated_chat_list, "/clearing_generated_chat_list"),
                # 📑 Формирование списка чатов / каналов
                (forming_list_of_chats_channels_ru, "/forming_list_of_chats_channels"),
            ]))


async def display_message_distribution_menu(page: ft.Page):
    """Отображает главное меню рассылки сообщений."""
    page.views.append(
        create_menu_view(
            sending_messages,
            [
                # 💬 Рассылка сообщений по чатам
                (sending_messages_via_chats_ru, "/sending_messages_via_chats_menu"),
                # 📨 Отправка сообщений в личку
                (sending_personal_messages_with_limits_ru, "/sending_personal_messages_with_limits_menu"),
            ]))
