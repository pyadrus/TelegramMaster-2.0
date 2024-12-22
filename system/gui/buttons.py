# -*- coding: utf-8 -*-
import flet as ft  # Импортируем библиотеку flet

from system.config.configs import line_width_button, height_button
from system.localization.localization import done_button, back_button


def function_button_ready(page: ft.Page, btn_click, back_button_clicked, user_input) -> None:
    """
    Функция для кнопки "Готово"

    Аргументы:
    :param page: Страница интерфейса Flet для отображения элементов управления.
    :param btn_click: Кнопка "Готово"
    :param user_input: Введенные данные пользователем
    :param back_button_clicked:Кнопка "Назад"
    :return:
    """
    button = ft.ElevatedButton(width=line_width_button, height=height_button, text=done_button,
                               on_click=btn_click)  # Кнопка "Готово"
    button_back = ft.ElevatedButton(width=line_width_button, height=height_button, text=back_button,
                                    on_click=back_button_clicked)
    page.views.append(
        ft.View(
            "/bio_editing",
            [
                user_input,
                ft.Column(),  # Заполнитель для приветствия или другого содержимого (необязательно)
                button,  # Кнопка "Готово"
                button_back,  # Кнопка "Назад"
            ],
        )
    )


def function_button_ready_reactions(page: ft.Page, btn_click, back_button_clicked, chat, message) -> None:
    """
    Функция для кнопки "Готово"

    Аргументы:
    :param page: Страница интерфейса Flet для отображения элементов управления.
    :param btn_click: Кнопка "Готово"
    :param chat: Введенные данные пользователем
    :param message: Введенные данные пользователем
    :param back_button_clicked:Кнопка "Назад"
    :return:
    """
    button = ft.ElevatedButton(width=line_width_button, height=height_button, text=done_button,
                               on_click=btn_click)  # Кнопка "Готово"
    button_back = ft.ElevatedButton(width=line_width_button, height=height_button, text=back_button,
                                    on_click=back_button_clicked)
    page.views.append(
        ft.View(
            "/working_with_reactions",
            [
                chat,  # Поле ввода ссылки на чат
                message,  # Поле ввода ссылки пост
                ft.Column(),  # Заполнитель для приветствия или другого содержимого (необязательно)
                button,  # Кнопка "Готово"
                button_back,  # Кнопка "Назад"
            ],
        )
    )
