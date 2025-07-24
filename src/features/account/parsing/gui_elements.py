# -*- coding: utf-8 -*-
import flet as ft  # Импортируем библиотеку flet

from src.locales.translations_loader import translations


class GUIProgram:
    """Элементы графического интерфейса программы."""

    @staticmethod
    async def key_app_bar():
        """Кнопка в верхней панели приложения (возврат в главное меню)."""
        return ft.AppBar(
            toolbar_height=40,
            title=ft.Text(translations["ru"]["menu"]["main"]),
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
        )

    @staticmethod
    async def outputs_text_gradient():
        """Выводит текст с градиентом на странице."""
        # Создаем текст с градиентным оформлением через TextStyle
        return ft.Text(
            spans=[
                ft.TextSpan(
                    translations["ru"]["menu"]["parsing"],
                    ft.TextStyle(
                        size=20,
                        weight=ft.FontWeight.NORMAL,
                        foreground=ft.Paint(
                            color=ft.Colors.PINK,
                        ),
                    ),
                )
            ],
        )

    @staticmethod
    async def diver_castom():
        """Разделительная линия"""
        return ft.Divider(height=1, color="red")
