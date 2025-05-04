# -*- coding: utf-8 -*-
import flet as ft  # Импортируем библиотеку flet

from src.core.configs import line_width_button, BUTTON_HEIGHT
from src.core.localization import done_button
from src.locales.translations_loader import translations


def function_button_ready(page: ft.Page, btn_click, back_button_clicked, user_input) -> None:
    """
    Функция для кнопки "Готово" и кнопки "Назад"

    :param page: Страница интерфейса Flet для отображения элементов управления.
    :param btn_click: Кнопка "Готово"
    :param user_input: Введенные данные пользователем
    :param back_button_clicked:Кнопка "Назад"
    :return:
    """
    page.views.append(
        ft.View(
            "/bio_editing",
            [
                user_input,
                ft.Column(),  # Заполнитель для приветствия или другого содержимого (необязательно)
                ft.ElevatedButton(width=line_width_button, height=BUTTON_HEIGHT, text=done_button,
                                  on_click=btn_click),  # Кнопка "Готово"
                ft.ElevatedButton(width=line_width_button, height=BUTTON_HEIGHT,
                                  text=translations["ru"]["buttons"]["back"],
                                  on_click=back_button_clicked),  # Кнопка "Назад"
            ], ))


def function_button_ready_reactions(page: ft.Page, btn_click, back_button_clicked, chat, message) -> None:
    """
    Функция для кнопки "Готово" и кнопки "Назад"

    :param page: Страница интерфейса Flet для отображения элементов управления.
    :param btn_click: Кнопка "Готово"
    :param chat: Введенные данные пользователем
    :param message: Введенные данные пользователем
    :param back_button_clicked:Кнопка "Назад"
    :return:
    """
    page.views.append(
        ft.View(
            "/working_with_reactions",
            [
                chat,  # Поле ввода ссылки на чат
                message,  # Поле ввода ссылки пост
                ft.Column(),  # Заполнитель для приветствия или другого содержимого (необязательно)
                ft.ElevatedButton(width=line_width_button, height=BUTTON_HEIGHT, text=done_button,
                                  on_click=btn_click),  # Кнопка "Готово"
                ft.ElevatedButton(width=line_width_button, height=BUTTON_HEIGHT,
                                  text=translations["ru"]["buttons"]["back"],
                                  on_click=back_button_clicked),  # Кнопка "Назад"
            ], ))


def function_button_ready_viewing(page: ft.Page, btn_click, back_button_clicked, link_channel, link_post):
    """
    Функция для кнопки "Готово" и кнопки "Назад"

    :param page: Страница интерфейса Flet для отображения элементов управления.
    :param btn_click: Кнопка "Готово"
    :param link_channel: Введенные данные пользователем
    :param link_post: Введенные данные пользователем
    :param back_button_clicked:Кнопка "Назад"
    :return:
    """
    # Добавление представления на страницу
    page.views.append(
        ft.View(
            "/viewing_posts_menu",  # Маршрут для этого представления
            [
                link_channel,  # Поле ввода ссылки на чат
                link_post,  # Поле ввода ссылки пост
                ft.Column(),  # Колонка для размещения других элементов (при необходимости)
                ft.ElevatedButton(width=line_width_button, height=BUTTON_HEIGHT, text=done_button,
                                  on_click=btn_click),  # Кнопка "Готово"
                ft.ElevatedButton(width=line_width_button, height=BUTTON_HEIGHT,
                                  text=translations["ru"]["buttons"]["back"],
                                  on_click=back_button_clicked),  # Кнопка "Назад"
            ]))
