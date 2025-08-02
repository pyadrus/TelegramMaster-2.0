# -*- coding: utf-8 -*-
import flet as ft  # Импортируем библиотеку flet


class TimeIntervalInputSection:

    async def create_time_inputs_and_save_button(self, on_save_click, label_min, label_max):
        """
        Создаёт текстовое поле для ввода данных (ссылок, времени) и кнопку сохранения.

        :param label_max: Выводимый текст на поле ввода
        :param label_min: Выводимый текст на поле ввода
        :param on_save_click: Функция-обработчик, вызываемая при нажатии на кнопку сохранения.
        :return: Кортеж из двух элементов: ft.TextField и ft.IconButton.
        https://flet.dev/docs/controls/textfield/
        """
        min_time_input = ft.TextField(label=label_min, autofocus=True, width=344)
        max_time_input = ft.TextField(label=label_max, autofocus=True, width=344)
        save_button = ft.IconButton(
            visible=True,
            icon=ft.Icons.SAVE,
            on_click=on_save_click,
            icon_size=50
        )
        return min_time_input, max_time_input, save_button

    async def build_time_input_row(self, min_time_input: ft.TextField, max_time_input: ft.TextField,
                                   save_button: ft.IconButton):
        """
        Создаёт горизонтальный контейнер (строку) с полем ввода и кнопкой.

        :param min_time_input: Текстовое поле для ввода минимального времени.
        :param max_time_input: Текстовое поле для ввода максимального времени.
        :param save_button: Кнопка сохранения.
        :return: Компонент ft.Row с размещёнными элементами.
        https://flet.dev/docs/cookbook/large-lists/#gridview
        """
        return ft.Row(
            controls=[min_time_input, max_time_input, save_button],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN  # или .START
        )


class SubscriptionLinkInputSection:
    """
    Компонент Flet для отображения текстового поля ввода и кнопки сохранения.
    Используется для ввода ссылок на Telegram-группы и каналы, на которые необходимо подписаться.
    """

    async def create_link_input_and_save_button(self, on_save_click, label_text):
        """
        Создаёт текстовое поле для ввода ссылок и кнопку сохранения.

        :param label_text:  Текст, отображаемый над полем ввода.
        :param on_save_click: Функция-обработчик, вызываемая при нажатии на кнопку сохранения.
        :return: Кортеж из двух элементов: ft.TextField и ft.IconButton.
        https://flet.dev/docs/controls/textfield/
        """
        # Поле ввода, для ссылок для подписки
        link_input = ft.TextField(
            label=label_text,
            label_style=ft.TextStyle(color=ft.Colors.GREY_400),
            width=700
        )
        save_button = ft.IconButton(
            visible=True,
            icon=ft.Icons.SAVE,
            on_click=on_save_click,
            icon_size=50
        )
        return link_input, save_button

    async def build_link_input_row(self, link_input: ft.TextField, save_button: ft.IconButton):
        """
        Создаёт горизонтальный контейнер (строку) с полем ввода и кнопкой.

        :param link_input: Текстовое поле для ввода ссылок.
        :param save_button: Кнопка сохранения.
        :return: Компонент ft.Row с размещёнными элементами.
        https://flet.dev/docs/cookbook/large-lists/#gridview
        """
        return ft.Row(
            controls=[link_input, save_button],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )
