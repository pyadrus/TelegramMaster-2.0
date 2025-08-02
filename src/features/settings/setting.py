# -*- coding: utf-8 -*-
import configparser
import io
import json
import os
import sys

import flet as ft  # Импортируем библиотеку flet

from src.core.configs import BUTTON_HEIGHT, WIDTH_WIDE_BUTTON
from src.core.sqlite_working_tools import cleaning_db, save_proxy_data_to_db
from src.gui.gui import list_view, log_and_display
from src.gui.notification import show_notification
from src.locales.translations_loader import translations

config = configparser.ConfigParser(empty_lines_in_values=False, allow_no_value=True)
config.read("user_data/config/config.ini")

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class WriteDatabase:

    def __init__(self):
        table_name = "links_inviting"

    async def output_the_input_field(self, page: ft.Page, data, table_name: str, column_name: str, route: str,
                                     into_columns: str) -> None:
        """
        Окно ввода для записи списка контактов telegram

        :param data: Данные для записи в БД.
        :param page: Страница интерфейса Flet для отображения элементов управления.
        :param table_name: Имя таблицы в базе данных.
        :param column_name: Имя столбца в таблице.
        :param route: Маршрут для перехода после записи данных.
        :param into_columns: Имя столбца в таблице, в который будут записаны данные.
        """

        # text_to_send = ft.TextField(label=label, multiline=True, max_lines=19)
        # records: list = await self.db_handler.select_records_with_limit(table_name=table_name, limit=None)
        # await log_and_display(message=f"Количество данных в таблице {table_name}: {len(records)}", page=page)

        async def write_data(clear_before: bool = False) -> None:
            """Запись данных в БД с опцией предварительной очистки"""

            if clear_before:  # Проверяем, нужно ли очищать таблицу перед записью данных
                cleaning_db(table_name=table_name)  # Очищаем таблицу перед записью данных

            # data = text_to_send.value.split()
            # Удаляем дубликаты
            unique_records = list(set(data))
            await self.db_handler.write_to_single_column_table(name_database=table_name, database_columns=column_name,
                                                               into_columns=into_columns, recorded_data=unique_records)
            await show_notification(page, "Данные успешно записаны!")
            page.go(route)
            page.update()

        async def on_append_click(_: ft.ControlEvent) -> None:
            """Запись данных в базу данных"""
            await write_data(clear_before=False)

        async def on_clear_and_write_click(_: ft.ControlEvent) -> None:
            """Очистка данных и запись данных в базу данных"""
            await write_data(clear_before=True)

        async def on_back_click(_: ft.ControlEvent) -> None:
            """Возврат на предыдущий экран"""
            page.go(route)

        # Формирование представления
        # controls = [
        #     text_to_send,
        #     ft.ElevatedButton(text="Дозаписать данные в базу данных", width=WIDTH_WIDE_BUTTON, height=BUTTON_HEIGHT,
        #                       on_click=on_append_click),
        #     ft.ElevatedButton(text="Очистить данные и записать по новой", width=WIDTH_WIDE_BUTTON, height=BUTTON_HEIGHT,
        #                       on_click=on_clear_and_write_click),
        #     ft.ElevatedButton(text=translations["ru"]["buttons"]["back"], width=WIDTH_WIDE_BUTTON, height=BUTTON_HEIGHT,
        #                       on_click=on_back_click)
        # ]
        #
        # page.views.append(ft.View(route, controls=[list_view, ft.Column(controls=controls)]))


class SettingPage:

    def __init__(self, page: ft.Page):
        self.page = page

    async def creating_the_main_window_for_proxy_data_entry(self) -> None:
        """
        Создание главного окна для ввода дынных proxy
        """
        self.page.controls.append(list_view)  # добавляем ListView на страницу для отображения логов 📝

        list_view.controls.append(ft.Text(f"Введите данные для записи"))  # отображаем сообщение в ListView

        proxy_type = ft.TextField(label="Введите тип прокси, например SOCKS5: ", multiline=True, max_lines=19)
        addr_type = ft.TextField(label="Введите ip адрес, например 194.67.248.9: ", multiline=True, max_lines=19)
        port_type = ft.TextField(label="Введите порт прокси, например 9795: ", multiline=True, max_lines=19)
        username_type = ft.TextField(label="Введите username, например NnbjvX: ", multiline=True, max_lines=19)
        password_type = ft.TextField(label="Введите пароль, например ySfCfk: ", multiline=True, max_lines=19)

        async def btn_click(_) -> None:
            proxy = {
                "proxy_type": proxy_type.value,
                "addr": addr_type.value,
                "port": port_type.value,
                "username": username_type.value,
                "password": password_type.value,
                "rdns": "True"
            }
            save_proxy_data_to_db(proxy=proxy)
            await show_notification(self.page, "Данные успешно записаны!")
            self.page.go("/settings")  # Изменение маршрута в представлении существующих настроек
            self.page.update()

        self.add_view_with_fields_and_button(self.page,
                                             [proxy_type, addr_type, port_type, username_type, password_type],
                                             btn_click)

    async def recording_text_for_sending_messages(self, page: ft.Page, label, unique_filename) -> None:
        """
        Запись текста в файл для отправки сообщений в Telegram в формате JSON. Данные записываются в файл с именем
        <имя файла>.json и сохраняются в формате JSON.

        :param page: Страница интерфейса Flet для отображения элементов управления.
        :param label: Текст для отображения в поле ввода.
        :param unique_filename: Имя файла для записи данных.
        """
        page.controls.append(list_view)  # добавляем ListView на страницу для отображения логов 📝
        list_view.controls.append(ft.Text(f"Введите данные для записи"))  # отображаем сообщение в ListView
        text_to_send = ft.TextField(label=label, multiline=True, max_lines=19)

        async def btn_click(_) -> None:
            write_data_to_json_file(reactions=text_to_send.value,
                                    path_to_the_file=unique_filename)  # Сохраняем данные в файл
            await show_notification(page, "Данные успешно записаны!")
            page.go("/settings")  # Изменение маршрута в представлении существующих настроек
            page.update()

        self.add_view_with_fields_and_button(page, [text_to_send], btn_click)

    async def record_setting(self, limit_type: str, limits):
        """
        Запись лимитов на аккаунт или сообщение

        :param limit_type: Тип лимита.
        :param limits: Текст для отображения в поле ввода.
        """

        # page.controls.append(list_view)  # добавляем ListView на страницу для отображения логов 📝
        # list_view.controls.append(ft.Text(f"Введите данные для записи"))  # отображаем сообщение в ListView
        # limits = ft.TextField(label=label, multiline=True, max_lines=19)
        # async def btn_click(_) -> None:
        try:
            config.get(limit_type, limit_type)
            config.set(limit_type, limit_type, limits.value)
            writing_settings_to_a_file(config)
            await show_notification(self.page, "Данные успешно записаны!")
        except configparser.NoSectionError as error:
            await show_notification(self.page, "⚠️ Поврежден файл user_data/config/config.ini")
            await log_and_display(f"Ошибка: {error}", self.page)
            # page.go("/settings")  # Изменение маршрута в представлении существующих настроек
            # page.update()
        # self.add_view_with_fields_and_button(page, [limits], btn_click)

    # async def recording_the_time_to_launch_an_invite_every_day(self, page: ft.Page) -> None:
    #     """
    #     Запись времени для запуска inviting в определенное время
    #
    #     :param page: Страница интерфейса Flet для отображения элементов управления.
    #     """
    # page.controls.append(list_view)  # добавляем ListView на страницу для отображения логов 📝
    # list_view.controls.append(ft.Text(f"Введите данные для записи"))  # отображаем сообщение в ListView
    # hour_textfield = ft.TextField(label="Час запуска приглашений (0-23):", autofocus=True, value="")
    # minutes_textfield = ft.TextField(label="Минуты запуска приглашений (0-59):", value="")

    async def recording_the_time_to_launch_an_invite_every_day(self, hour_textfield, minutes_textfield) -> None:
        """Записывает данные в файл config.ini"""
        try:
            hour = int(hour_textfield.value)
            minutes = int(minutes_textfield.value)
            if not 0 <= hour < 24:
                await log_and_display(f"Введите часы в пределах от 0 до 23!", self.page)
                return
            if not 0 <= minutes < 60:
                await log_and_display(f"Введите минуты в пределах от 0 до 59!", self.page)
                return
            # Предполагая, что config является объектом, похожим на словарь
            config.get("hour_minutes_every_day", "hour")
            config.set("hour_minutes_every_day", "hour", str(hour))
            config.get("hour_minutes_every_day", "minutes")
            config.set("hour_minutes_every_day", "minutes", str(minutes))
            writing_settings_to_a_file(config)
            await show_notification(self.page, "Данные успешно записаны!")

            # self.page.go("/settings")  # Изменение маршрута в представлении существующих настроек
        except ValueError:
            await log_and_display(f"Введите числовые значения для часов и минут!", self.page)
        self.page.update()  # Обновляем страницу

        # self.add_view_with_fields_and_button(page, [hour_textfield, minutes_textfield], btn_click)

    async def create_main_window(self, variable, smaller_timex, larger_timex) -> None:
        """
        :param variable: Название переменной в файле config.ini
        :param smaller_timex: Первое время
        :param larger_timex: Второе время
        :return: None
        """

        # self.page.controls.append(list_view)  # добавляем ListView на страницу для отображения логов 📝
        # for time_range_message in time_range: list_view.controls.append(
        #     ft.Text(f"Записанные данные в файле {time_range_message}"))  # отображаем сообщение в ListView
        # smaller_timex = ft.TextField(label="Время в секундах (меньшее)", autofocus=True)
        # larger_timex = ft.TextField(label="Время в секундах (большее)")

        # async def btn_click(_) -> None:
        #     """Обработчик клика по кнопке"""
        try:
            smaller_times = int(smaller_timex.value)
            larger_times = int(larger_timex.value)
            if smaller_times < larger_times:  # Проверяем, что первое время меньше второго
                # Если условие прошло проверку, то возвращаем первое и второе время
                writing_settings_to_a_file(
                    await recording_limits_file(str(smaller_times), str(larger_times), variable=variable,
                                                page=self.page))
                list_view.controls.append(ft.Text("Данные успешно записаны!"))  # отображаем сообщение в ListView
                await show_notification(self.page, "Данные успешно записаны!")
                self.page.go("/settings")  # Изменение маршрута в представлении существующих настроек
            else:
                list_view.controls.append(ft.Text("Ошибка: первое время должно быть меньше второго!"))
        except ValueError:
            list_view.controls.append(ft.Text("Ошибка: введите числовые значения!"))
        self.page.update()  # обновляем страницу

        # self.add_view_with_fields_and_button(self.page, [smaller_timex, larger_timex], btn_click)

    async def writing_api_id_api_hash(self, page: ft.Page):
        """
        Записываем api, hash полученный с помощью регистрации приложения на сайте https://my.telegram.org/auth

        :param page: Страница интерфейса Flet для отображения элементов управления.
        """
        page.controls.append(list_view)  # добавляем ListView на страницу для отображения логов 📝
        list_view.controls.append(ft.Text(f"Введите данные для записи"))  # отображаем сообщение в ListView
        api_id_data = ft.TextField(label="Введите api_id", multiline=True, max_lines=19)
        api_hash_data = ft.TextField(label="Введите api_hash", multiline=True, max_lines=19)

        def btn_click(_) -> None:
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

        :param page: Страница интерфейса Flet для отображения элементов управления.
        :param fields: Список текстовых полей для добавления
        :param btn_click: Кнопка для добавления
        :return: None
        """

        def back_button_clicked(_) -> None:
            """Кнопка возврата в меню настроек"""
            page.go("/settings")

        # Создание View с элементами
        page.views.append(
            ft.View(
                "/settings",
                controls=[
                    list_view,  # отображение логов 📝
                    ft.Column(
                        controls=fields + [
                            ft.ElevatedButton(width=WIDTH_WIDE_BUTTON, height=BUTTON_HEIGHT,
                                              text=translations["ru"]["buttons"]["done"],
                                              on_click=btn_click),
                            ft.ElevatedButton(width=WIDTH_WIDE_BUTTON, height=BUTTON_HEIGHT,
                                              text=translations["ru"]["buttons"]["back"],
                                              on_click=back_button_clicked)
                        ]
                    )]))


def writing_settings_to_a_file(config) -> None:
    """Запись данных в файл user_data/config.ini"""
    with open("user_data/config/config.ini", "w") as setup:  # Открываем файл в режиме записи
        config.write(setup)  # Записываем данные в файл


async def recording_limits_file(time_1, time_2, variable: str, page: ft.Page) -> configparser.ConfigParser:
    """
    Запись данных в файл TelegramMaster/user_data/config.ini

    :param time_1: Время в секундах
    :param time_2: Время в секундах
    :param variable: Название переменной в файле config.ini
    :param page: Страница интерфейса Flet для отображения элементов управления.
    """
    try:
        config.get(f"{variable}", f"{variable}_1")
        config.set(f"{variable}", f"{variable}_1", time_1)
        config.get(f"{variable}", f"{variable}_2")
        config.set(f"{variable}", f"{variable}_2", time_2)
    except configparser.NoSectionError as error:
        await log_and_display(
            message=f"❌ Не удалось получить значение переменной: {error}. Проверьте TelegramMaster/user_data/config/config.ini",
            page=page)
    return config


def write_data_to_json_file(reactions, path_to_the_file):
    """Открываем файл для записи данных в формате JSON"""
    with open(path_to_the_file, 'w', encoding='utf-8') as file:
        json.dump(reactions, file, ensure_ascii=False, indent=4)


def get_unique_filename(base_filename) -> str:
    """Функция для получения уникального имени файла"""
    index = 1
    while True:
        new_filename = f"{base_filename}_{index}.json"
        if not os.path.isfile(new_filename):
            return new_filename
        index += 1


async def reaction_gui(page: ft.Page):
    """
    Выбираем реакцию с помощью чекбокса

    :param page: Страница интерфейса Flet для отображения элементов управления.
    """

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

    async def button_clicked(_) -> None:
        """Выбранная реакция"""
        selected_reactions = [checkbox.label for checkbox in checkboxes if
                              checkbox.value]  # Получаем только выбранные реакции
        write_data_to_json_file(reactions=selected_reactions, path_to_the_file='user_data/reactions/reactions.json')

        await show_notification(page, "Данные успешно записаны!")
        page.go("/settings")  # Переход к странице настроек

    async def back_button_clicked(_) -> None:
        """Кнопка возврата в меню настроек"""
        page.go("/settings")

    # Добавляем элементы на страницу
    page.views.append(
        ft.View(
            "/settings",
            controls=[
                t,
                ft.Column([ft.Row(checkboxes[i:i + 9]) for i in range(0, len(checkboxes), 9)]),  # Чекбоксы в колонках
                ft.ElevatedButton(width=WIDTH_WIDE_BUTTON, height=BUTTON_HEIGHT,
                                  text=translations["ru"]["buttons"]["done"],
                                  on_click=button_clicked),  # Кнопка "Готово",
                ft.ElevatedButton(width=WIDTH_WIDE_BUTTON, height=BUTTON_HEIGHT,
                                  text=translations["ru"]["buttons"]["back"],
                                  on_click=back_button_clicked),  # Кнопка "Назад"
            ]
        )
    )
