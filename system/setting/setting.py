# -*- coding: utf-8 -*-
import configparser
import io
import json
import os
import sys

import flet as ft  # Импортируем библиотеку flet
from loguru import logger

from system.auxiliary_functions.config import height_button, line_width_button
from system.localization.localization import back_button
from system.sqlite_working_tools.sqlite_working_tools import DatabaseHandler

config = configparser.ConfigParser(empty_lines_in_values=False, allow_no_value=True)
config.read("user_settings/config/config.ini")

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class SettingPage:

    def __init__(self):
        self.db_handler = DatabaseHandler()

    async def creating_the_main_window_for_proxy_data_entry(self, page: ft.Page) -> None:
        """Создание главного окна для ввода дынных proxy"""
        proxy_type = ft.TextField(label="Введите тип прокси, например SOCKS5: ", multiline=True, max_lines=19)
        addr_type = ft.TextField(label="Введите ip адрес, например 194.67.248.9: ", multiline=True, max_lines=19)
        port_type = ft.TextField(label="Введите порт прокси, например 9795: ", multiline=True, max_lines=19)
        username_type = ft.TextField(label="Введите username, например NnbjvX: ", multiline=True, max_lines=19)
        password_type = ft.TextField(label="Введите пароль, например ySfCfk: ", multiline=True, max_lines=19)

        async def btn_click(e) -> None:
            rdns_types = "True"
            proxy = [proxy_type.value, addr_type.value, port_type.value, username_type.value, password_type.value,
                     rdns_types]
            await self.db_handler.save_proxy_data_to_db(proxy=proxy)
            page.go("/settings")  # Изменение маршрута в представлении существующих настроек
            page.update()

        self.add_view_with_fields_and_button(page, [proxy_type, addr_type, port_type, username_type, password_type],
                                             btn_click)

    def recording_text_for_sending_messages(self, page: ft.Page, label, unique_filename) -> None:
        """
        Запись текста в файл для отправки сообщений в Telegram в формате JSON. Данные записываются в файл с именем
        <имя файла>.json и сохраняются в формате JSON.
        """
        text_to_send = ft.TextField(label=label, multiline=True, max_lines=19)

        def btn_click(e) -> None:
            write_data_to_json_file(reactions=text_to_send.value,
                                    path_to_the_file=unique_filename)  # Сохраняем данные в файл
            page.go("/settings")  # Изменение маршрута в представлении существующих настроек
            page.update()

        self.add_view_with_fields_and_button(page, [text_to_send], btn_click)

    def output_the_input_field(self, page: ft.Page, label: str, table_name: str, column_name: str, route: str,
                               into_columns: str) -> None:
        """Окно ввода для записи списка контактов telegram"""
        text_to_send = ft.TextField(label=label, multiline=True, max_lines=19)

        async def btn_click(e) -> None:
            await self.db_handler.write_to_single_column_table(
                name_database=table_name,
                database_columns=column_name,
                into_columns=into_columns,
                recorded_data=text_to_send.value.split()
            )
            page.go(route)  # Изменение маршрута в представлении существующих настроек
            page.update()

        self.add_view_with_fields_and_button(page, [text_to_send], btn_click)

    def record_setting(self, page: ft.Page, limit_type: str, label: str):
        """Запись лимитов на аккаунт или сообщение"""
        limits = ft.TextField(label=label, multiline=True, max_lines=19)

        def btn_click(e) -> None:
            config.get(limit_type, limit_type)
            config.set(limit_type, limit_type, limits.value)
            writing_settings_to_a_file(config)

            page.go("/settings")  # Изменение маршрута в представлении существующих настроек
            page.update()

        self.add_view_with_fields_and_button(page, [limits], btn_click)

    async def recording_the_time_to_launch_an_invite_every_day(self, page: ft.Page) -> None:
        """Запись времени для запуска inviting в определенное время"""
        hour_textfield = ft.TextField(label="Час запуска приглашений (0-23):", autofocus=True, value="")
        minutes_textfield = ft.TextField(label="Минуты запуска приглашений (0-59):", value="")

        def btn_click(e) -> None:
            try:
                hour = int(hour_textfield.value)
                minutes = int(minutes_textfield.value)

                if not 0 <= hour < 24:
                    logger.info('Введите часы в пределах от 0 до 23!')
                    return
                if not 0 <= minutes < 60:
                    logger.info('Введите минуты в пределах от 0 до 59!')
                    return

                # Предполагая, что config является объектом, похожим на словарь
                config.get("hour_minutes_every_day", "hour")
                config.set("hour_minutes_every_day", "hour", str(hour))
                config.get("hour_minutes_every_day", "minutes")
                config.set("hour_minutes_every_day", "minutes", str(minutes))
                writing_settings_to_a_file(config)
                page.go("/settings")  # Изменение маршрута в представлении существующих настроек
            except ValueError:
                logger.info('Введите числовые значения для часов и минут!')
            page.update()  # Обновляем страницу

        self.add_view_with_fields_and_button(page, [hour_textfield, minutes_textfield], btn_click)

    def create_main_window(self, page: ft.Page, variable) -> None:
        """
        :param page:
        :param variable: название переменной в файле config.ini
        :return: None
        """
        smaller_timex = ft.TextField(label="Время в секундах (меньшее)", autofocus=True)
        larger_timex = ft.TextField(label="Время в секундах (большее)")

        def btn_click(e) -> None:
            try:
                smaller_times = int(smaller_timex.value)
                larger_times = int(larger_timex.value)

                if smaller_times < larger_times:  # Проверяем, что первое время меньше второго
                    # Если условие прошло проверку, то возвращаем первое и второе время
                    config = recording_limits_file(str(smaller_times), str(larger_times), variable=variable)
                    writing_settings_to_a_file(config)
                    page.go("/settings")  # Изменение маршрута в представлении существующих настроек
            except ValueError:
                pass

            page.update()

        self.add_view_with_fields_and_button(page, [smaller_timex, larger_timex], btn_click)

    async def writing_api_id_api_hash(self, page: ft.Page):
        """Записываем api, hash полученный с помощью регистрации приложения на сайте https://my.telegram.org/auth"""
        api_id_data = ft.TextField(label="Введите api_id", multiline=True, max_lines=19)
        api_hash_data = ft.TextField(label="Введите api_hash", multiline=True, max_lines=19)

        def btn_click(e) -> None:
            config.get("telegram_settings", "id")
            config.set("telegram_settings", "id", api_id_data.value)
            config.get("telegram_settings", "hash")
            config.set("telegram_settings", "hash", api_hash_data.value)
            writing_settings_to_a_file(config)
            page.go("/settings")  # Изменение маршрута в представлении существующих настроек
            page.update()

        self.add_view_with_fields_and_button(page, [api_id_data, api_hash_data], btn_click)

    @staticmethod
    def add_view_with_fields_and_button(page: ft.Page, fields: list, btn_click) -> None:
        """
        Добавляет представление с заданными текстовыми полями и кнопкой.
        :param page: Страница, на которую нужно добавить представление
        :param fields: Список текстовых полей для добавления
        :param btn_click: Кнопка для добавления
        """

        def back_button_clicked(e):
            """Кнопка возврата в меню настроек"""
            page.go("/settings")

        # Кнопка "Готово" (button) и связывает ее с функцией button_clicked.
        button = ft.ElevatedButton(width=line_width_button, height=height_button, text="Готово", on_click=btn_click)
        button_back = ft.ElevatedButton(width=line_width_button, height=height_button, text=back_button,
                                        on_click=back_button_clicked)

        page.views.append(
            ft.View(
                "/settings",
                fields + [ft.Column(), button, button_back]
                # Заполнитель для приветствия или другого содержимого (необязательно)
            )
        )


def writing_settings_to_a_file(config) -> None:
    """Запись данных в файл user_settings/config.ini"""
    with open("user_settings/config/config.ini", "w") as setup:  # Открываем файл в режиме записи
        config.write(setup)  # Записываем данные в файл


def recording_limits_file(time_1, time_2, variable: str) -> configparser.ConfigParser:
    """
    Запись данных в файл TelegramMaster/user_settings/config.ini
    :param time_1: Время в секундах
    :param time_2: Время в секундах
    :param variable: Название переменной в файле config.ini
    """
    try:
        config.get(f"{variable}", f"{variable}_1")
        config.set(f"{variable}", f"{variable}_1", time_1)
        config.get(f"{variable}", f"{variable}_2")
        config.set(f"{variable}", f"{variable}_2", time_2)
        return config
    except configparser.NoSectionError as error:
        logger.error(
            f"Не удалось получить значение переменной: {error}. Проверьте TelegramMaster/user_settings/config/config.ini")


def write_data_to_json_file(reactions, path_to_the_file):
    """Открываем файл для записи данных в формате JSON"""
    with open(path_to_the_file, 'w', encoding='utf-8') as file:
        json.dump(reactions, file, ensure_ascii=False, indent=4)


def get_unique_filename(base_filename):
    """Функция для получения уникального имени файла"""
    index = 1
    while True:
        new_filename = f"{base_filename}_{index}.json"
        if not os.path.isfile(new_filename):
            return new_filename
        index += 1


async def reaction_gui(page: ft.Page):
    """Выбираем реакцию с помощью чекбокса"""

    t = ft.Text(value='Выберите реакцию')  # Создает текстовое поле (t).

    # Создаем все чекбоксы единожды и сохраняем их в списке
    checkboxes = [
        ft.Checkbox(label="😀"), ft.Checkbox(label="😎"), ft.Checkbox(label="😍"),
        ft.Checkbox(label="😂"), ft.Checkbox(label="😡"), ft.Checkbox(label="😱"),
        ft.Checkbox(label="😭"), ft.Checkbox(label="👍"), ft.Checkbox(label="👎"),
        ft.Checkbox(label="❤"), ft.Checkbox(label="🔥"), ft.Checkbox(label="🎉"),
        ft.Checkbox(label="😁"), ft.Checkbox(label="😢"), ft.Checkbox(label="💩"),
        ft.Checkbox(label="👏"), ft.Checkbox(label="🤷‍♀️"), ft.Checkbox(label="🤷"),
        ft.Checkbox(label="🤷‍♂️"), ft.Checkbox(label="👾"), ft.Checkbox(label="🙊"),
        ft.Checkbox(label="💊"), ft.Checkbox(label="😘"), ft.Checkbox(label="🦄"),
        ft.Checkbox(label="💘"), ft.Checkbox(label="🆒"), ft.Checkbox(label="🗿"),
        ft.Checkbox(label="🤪"), ft.Checkbox(label="💅"), ft.Checkbox(label="☃️"),
        ft.Checkbox(label="🎄"), ft.Checkbox(label="🎅"), ft.Checkbox(label="🤗"),
        ft.Checkbox(label="🤬"), ft.Checkbox(label="🤮"), ft.Checkbox(label="🤡"),
        ft.Checkbox(label="🥴"), ft.Checkbox(label="💯"), ft.Checkbox(label="🌭"),
        ft.Checkbox(label="⚡️"), ft.Checkbox(label="🍌"), ft.Checkbox(label="🖕"),
        ft.Checkbox(label="💋"), ft.Checkbox(label="👀"), ft.Checkbox(label="🤝"),
        ft.Checkbox(label="🍾"), ft.Checkbox(label="🏆"), ft.Checkbox(label="🥱"),
        ft.Checkbox(label="🕊"), ft.Checkbox(label="😭")
    ]

    def button_clicked(e):
        """Выбранная реакция"""
        selected_reactions = [checkbox.label for checkbox in checkboxes if checkbox.value]  # Получаем только выбранные реакции
        write_data_to_json_file(reactions=selected_reactions, path_to_the_file='user_settings/reactions/reactions.json')
        page.go("/settings")  # Переход к странице настроек

    def back_button_clicked(e):
        """Кнопка возврата в меню настроек"""
        page.go("/settings")

    # Кнопка "Готово" и "Назад"
    button = ft.ElevatedButton(width=line_width_button, height=height_button, text="Готово", on_click=button_clicked)
    button_back = ft.ElevatedButton(width=line_width_button, height=height_button, text=back_button, on_click=back_button_clicked)

    # Добавляем элементы на страницу
    page.views.append(
        ft.View(
            "/settings",
            controls=[
                t,
                ft.Column([ft.Row(checkboxes[i:i + 9]) for i in range(0, len(checkboxes), 9)]),  # Чекбоксы в колонках
                button,
                button_back
            ]
        )
    )
