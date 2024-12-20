# -*- coding: utf-8 -*-
import flet as ft  # Импортируем библиотеку flet

from system.auxiliary_functions.config import line_width_button, height_button
from system.localization.localization import done_button


def function_button_ready(page: ft.Page, btn_click, user_input):
    """
    Функция для кнопки "Готово"

    Аргументы:
    :param page: Страница интерфейса Flet для отображения элементов управления.
    :param btn_click:
    :param user_input:
    :return:
    """
    button = ft.ElevatedButton(width=line_width_button, height=height_button, text=done_button,
                               on_click=btn_click)  # Кнопка "Готово"
    page.views.append(
        ft.View(
            "/bio_editing",
            [
                user_input,
                ft.Column(),  # Заполнитель для приветствия или другого содержимого (необязательно)
                button,
            ],
        )
    )