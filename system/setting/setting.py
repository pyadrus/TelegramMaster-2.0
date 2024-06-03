import configparser
import getpass
import json
import os
import sys
import io
import flet as ft  # Импортируем библиотеку flet
from telethon import TelegramClient
from telethon.errors import *
from loguru import logger
from system.account_actions.creating.account_registration import telegram_connects
from system.auxiliary_functions.global_variables import ConfigReader
from system.sqlite_working_tools.sqlite_working_tools import DatabaseHandler

config = configparser.ConfigParser(empty_lines_in_values=False, allow_no_value=True)
config.read("user_settings/config.ini")

configs_reader = ConfigReader()
api_id_data, api_hash_data = configs_reader.get_api_id_data_api_hash_data()

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def output_the_input_field(page: ft.Page, db_handler) -> None:
    """Выводим ссылки в поле ввода поле ввода для записи ссылок групп"""
    text_to_send = ft.TextField(label="Введите список ссылок на группы", multiline=True, max_lines=19)

    async def btn_click(e) -> None:
        await db_handler.open_and_read_data("writing_group_links")  # Удаление списка с группами
        await db_handler.write_to_single_column_table(name_database="writing_group_links",
                                                      database_columns="writing_group_links",
                                                      into_columns="writing_group_links",
                                                      recorded_data=text_to_send.value.split())
        page.go("/settings")  # Изменение маршрута в представлении существующих настроек
        page.update()

    button = ft.ElevatedButton("Готово", on_click=btn_click)

    page.views.append(
        ft.View(
            "/settings",
            [
                text_to_send,
                ft.Column(),  # Заполнитель для приветствия или другого содержимого (необязательно)
                button,
            ],
        )
    )


def save_reactions(reactions, path_to_the_file):
    with open(path_to_the_file, 'w', encoding='utf-8') as file:
        json.dump(reactions, file, ensure_ascii=False, indent=4)


def record_setting(page: ft.Page, limit_type: str, label: str):
    """Запись лимитов на аккаунт или сообщение"""
    limits = ft.TextField(label=label, multiline=True, max_lines=19)

    def btn_click(e) -> None:
        config.get(limit_type, limit_type)
        config.set(limit_type, limit_type, limits.value)
        writing_settings_to_a_file(config)

        page.go("/settings")  # Изменение маршрута в представлении существующих настроек
        page.update()

    button = ft.ElevatedButton("Готово", on_click=btn_click)

    page.views.append(
        ft.View(
            "/settings",
            [
                limits,
                ft.Column(),  # Заполнитель для приветствия или другого содержимого (необязательно)
                button,
            ],
        )
    )


def record_device_type(page: ft.Page):
    """Запись типа устройства например: Samsung SGH600, Android 9 (P30), 4.2.1,
    Vivo V9, Android 9 (P30), 4.2.1"""
    device_model = ft.TextField(label="Введите модель устройства", multiline=True, max_lines=19)
    system_version = ft.TextField(label="Введите версию операционной системы", multiline=True, max_lines=19)
    app_version = ft.TextField(label="Введите версию приложения", multiline=True, max_lines=19)

    def btn_click(e) -> None:
        config.get("device_model", "device_model")
        config.set("device_model", "device_model", device_model.value)
        config.get("system_version", "system_version")
        config.set("system_version", "system_version", system_version.value)
        config.get("app_version", "app_version")
        config.set("app_version", "app_version", app_version.value)

        writing_settings_to_a_file(config)

        page.go("/settings")  # Изменение маршрута в представлении существующих настроек
        page.update()

    button = ft.ElevatedButton("Готово", on_click=btn_click)

    page.views.append(
        ft.View(
            "/settings",
            [
                device_model,
                system_version,
                app_version,
                ft.Column(),  # Заполнитель для приветствия или другого содержимого (необязательно)
                button,
            ],
        )
    )


def writing_api_id_api_hash(page: ft.Page):
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

    button = ft.ElevatedButton("Готово", on_click=btn_click)

    page.views.append(
        ft.View(
            "/settings",
            [
                api_id_data,
                api_hash_data,
                ft.Column(),  # Заполнитель для приветствия или другого содержимого (необязательно)
                button,
            ],
        )
    )


def writing_settings_to_a_file(config) -> None:
    """Запись данных в файл user_settings/config.ini"""
    with open("user_settings/config.ini", "w") as setup:  # Открываем файл в режиме записи
        config.write(setup)  # Записываем данные в файл


def recording_limits_file(time_1, time_2, variable: str) -> configparser.ConfigParser:
    """Запись данных в файл user_settings/time_inviting.ini"""
    config.get(f"{variable}", f"{variable}_1")
    config.set(f"{variable}", f"{variable}_1", time_1)
    config.get(f"{variable}", f"{variable}_2")
    config.set(f"{variable}", f"{variable}_2", time_2)
    return config


async def connecting_new_account() -> None:
    """Вводим данные в базу данных user_settings/software_database.db"""
    phone_data = input("[+] Введите номер телефона : ")  # Вводим номер телефона
    entities = (api_id_data, api_hash_data, phone_data)
    db_handler = DatabaseHandler()
    await db_handler.write_data_to_db(creating_a_table="CREATE TABLE IF NOT EXISTS config(phone)",
                                      writing_data_to_a_table="INSERT INTO config (phone) VALUES (?)",
                                      entities=entities)
    # Подключение к Telegram, возвращаем client для дальнейшего отключения сессии
    client = await telegram_connect(phone_data, db_handler)
    client.disconnect()  # Разрываем соединение telegram
    # app_notifications(notification_text="Аккаунт подсоединился!")  # Выводим уведомление


async def telegram_connect(phone, db_handler) -> TelegramClient:
    """Account telegram connect, с проверкой на валидность, если ранее не было соединения, то запрашиваем код"""
    client = await telegram_connects(db_handler, session=f"user_settings/accounts/{phone}")
    if not client.is_user_authorized():
        await client.send_code_request(phone)
        try:
            # Если ранее аккаунт не подсоединялся, то просим ввести код подтверждения
            await client.sign_in(phone, code=input("[+] Введите код: "))
        except SessionPasswordNeededError:
            """
            https://telethonn.readthedocs.io/en/latest/extra/basic/creating-a-client.html#two-factor-authorization-2fa
            """
            # Если аккаунт имеет password, то просим пользователя ввести пароль
            await client.sign_in(password=getpass.getpass())
        except ApiIdInvalidError:
            logger.info("[!] Не валидные api_id/api_hash")
    return client


def creating_the_main_window_for_proxy_data_entry(page: ft.Page, db_handler) -> None:
    """Создание главного окна для ввода дынных proxy"""
    proxy_type = ft.TextField(label="Введите тип прокси, например SOCKS5: ", multiline=True, max_lines=19)
    addr_type = ft.TextField(label="Введите ip адрес, например 194.67.248.9: ", multiline=True, max_lines=19)
    port_type = ft.TextField(label="Введите порт прокси, например 9795: ", multiline=True, max_lines=19)
    username_type = ft.TextField(label="Введите username, например NnbjvX: ", multiline=True, max_lines=19)
    password_type = ft.TextField(label="Введите пароль, например ySfCfk: ", multiline=True, max_lines=19)

    def btn_click(e) -> None:
        rdns_types = "True"
        proxy = [proxy_type.value, addr_type.value, port_type.value, username_type.value, password_type.value,
                 rdns_types]
        db_handler.save_proxy_data_to_db(proxy=proxy)
        page.go("/settings")  # Изменение маршрута в представлении существующих настроек
        page.update()

    button = ft.ElevatedButton("Готово", on_click=btn_click)

    page.views.append(
        ft.View(
            "/settings",
            [
                proxy_type,
                addr_type,
                port_type,
                username_type,
                password_type,
                ft.Column(),  # Заполнитель для приветствия или другого содержимого (необязательно)
                button,
            ],
        )
    )


def create_main_window(page: ft.Page, variable) -> None:
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

    button = ft.ElevatedButton("Готово", on_click=btn_click)

    page.views.append(
        ft.View(
            "/settings",
            [
                smaller_timex,
                larger_timex,
                ft.Column(),  # Заполнитель для приветствия или другого содержимого (необязательно)
                button,
            ],
        )
    )


def save_message(reactions, path_to_the_file):
    """Открываем файл для записи данных в формате JSON"""
    with open(f'{path_to_the_file}', 'w', encoding='utf-8') as json_file:
        json.dump(reactions, json_file, ensure_ascii=False)  # Используем функцию dump для записи данных в файл


def get_unique_filename(base_filename):
    """Функция для получения уникального имени файла"""
    index = 1
    while True:
        new_filename = f"{base_filename}_{index}.json"
        if not os.path.isfile(new_filename):
            return new_filename
        index += 1


def recording_text_for_sending_messages(page: ft.Page) -> None:
    """
    Запись текста в файл для отправки сообщений в Telegram в формате JSON. Данные записываются в файл с именем
    <имя файла>.json и сохраняются в формате JSON.
    """
    text_to_send = ft.TextField(label="Введите текст сообщения", multiline=True, max_lines=19)

    def btn_click(e) -> None:
        unique_filename = get_unique_filename(base_filename='user_settings/message/message')
        save_message(reactions=text_to_send.value,
                     path_to_the_file=unique_filename)  # Сохраняем данные в файл
        page.go("/settings")  # Изменение маршрута в представлении существующих настроек
        page.update()

    button = ft.ElevatedButton("Готово", on_click=btn_click)

    page.views.append(
        ft.View(
            "/settings",
            [
                text_to_send,
                ft.Column(),  # Заполнитель для приветствия или другого содержимого (необязательно)
                button,
            ],
        )
    )


def recording_the_time_to_launch_an_invite_every_day(page: ft.Page) -> None:
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

    button = ft.ElevatedButton("Готово", on_click=btn_click)

    page.views.append(
        ft.View(
            "/settings",
            [
                hour_textfield,
                minutes_textfield,
                ft.Column(),  # Заполнитель для приветствия или другого содержимого (необязательно)
                button,
            ],
        )
    )


def record_the_number_of_accounts(page: ft.Page):
    """Запись количества аккаунтов проставляющих реакции"""
    smaller_time = ft.TextField(label="Введите количество реакций", autofocus=True)

    def btn_click(e) -> None:
        try:
            smaller_times = int(smaller_time.value)  # Extract the text value from the TextField
            save_reactions(reactions=smaller_times,  # Количество аккаунтов для проставления реакций
                           path_to_the_file='user_settings/reactions/number_accounts.json')
            page.go("/settings")  # Изменение маршрута в представлении существующих настроек
            page.update()

        except ValueError:
            pass

    button = ft.ElevatedButton("Готово", on_click=btn_click)

    page.views.append(
        ft.View(
            "/settings",
            [
                smaller_time,
                ft.Column(),  # Заполнитель для приветствия или другого содержимого (необязательно)
                button,
            ],
        )
    )


def recording_link_channel(page: ft.Page):
    """Запись ссылки на канал / группу"""
    smaller_time = ft.TextField(label="Введите ссылку на группу", autofocus=True)

    def btn_click(e) -> None:
        link_text = smaller_time.value  # Извлечение текстового значения из TextField
        save_reactions(reactions=link_text,
                       path_to_the_file='user_settings/reactions/link_channel.json')  # Запись ссылки в json файл
        page.go("/settings")  # Изменение маршрута в представлении существующих настроек
        page.update()

    button = ft.ElevatedButton("Готово", on_click=btn_click)

    page.views.append(
        ft.View(
            "/settings",
            [
                smaller_time,
                ft.Column(),  # Заполнитель для приветствия или другого содержимого (необязательно)
                button,
            ],
        )
    )


def reaction_gui(page: ft.Page):
    """Выбираем реакцию с помощью чекбокса"""
    t = ft.Text(value='Выберите реакцию')  # Создает текстовое поле (t).
    c1 = ft.Checkbox(label="😀")  # Создает чекбокс c1 с меткой "😀".
    c2 = ft.Checkbox(label="😎")
    c3 = ft.Checkbox(label="😍")
    c4 = ft.Checkbox(label="😂")
    c5 = ft.Checkbox(label="😡")
    c6 = ft.Checkbox(label="😱")
    c7 = ft.Checkbox(label="👍")
    c8 = ft.Checkbox(label="👎")
    c9 = ft.Checkbox(label="❤")
    c10 = ft.Checkbox(label="🔥")
    c11 = ft.Checkbox(label="🎉")
    c12 = ft.Checkbox(label="😁")
    c13 = ft.Checkbox(label="😢")
    c14 = ft.Checkbox(label="💩")
    c15 = ft.Checkbox(label="👏")
    c16 = ft.Checkbox(label="🤷‍♀️")
    c17 = ft.Checkbox(label="🤷")
    c18 = ft.Checkbox(label="🤷‍♂️")
    c19 = ft.Checkbox(label="👾")
    c20 = ft.Checkbox(label="🙊")
    c21 = ft.Checkbox(label="💊")
    c22 = ft.Checkbox(label="😘")
    c23 = ft.Checkbox(label="🦄")
    c24 = ft.Checkbox(label="💘")
    c25 = ft.Checkbox(label="🆒")
    c26 = ft.Checkbox(label="🗿")
    c27 = ft.Checkbox(label="🤪")
    c28 = ft.Checkbox(label="💅")
    c29 = ft.Checkbox(label="☃️")
    c30 = ft.Checkbox(label="🎄")
    c31 = ft.Checkbox(label="🎅")
    c32 = ft.Checkbox(label="🤗")
    c33 = ft.Checkbox(label="🤬")
    c34 = ft.Checkbox(label="🤮")
    c35 = ft.Checkbox(label="🤡")
    c36 = ft.Checkbox(label="🥴")
    c37 = ft.Checkbox(label="💯")
    c38 = ft.Checkbox(label="🌭")
    c39 = ft.Checkbox(label="⚡️")
    c40 = ft.Checkbox(label="🍌")
    c41 = ft.Checkbox(label="🖕")
    c42 = ft.Checkbox(label="💋")
    c43 = ft.Checkbox(label="👀")
    c44 = ft.Checkbox(label="🤝")
    c45 = ft.Checkbox(label="🍾")
    c46 = ft.Checkbox(label="🏆")
    c47 = ft.Checkbox(label="🥱")
    c48 = ft.Checkbox(label="🕊")
    c49 = ft.Checkbox(label="😭")

    def button_clicked(e):
        """Выбранная реакция"""
        selected_reactions = []  # Создает пустой список selected_reactions для хранения выбранных реакций.
        for checkbox in [c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12, c13, c14, c15, c16, c17, c18, c19, c20,
                         c21, c22, c23, c24, c25, c26, c27, c28, c29, c30, c31, c32, c33, c34, c35, c36, c37, c38,
                         c39, c40, c41, c42, c43, c44, c45, c46, c47, c48, c49]:  # Перебирает чекбоксы (c1 - c49).
            if checkbox.value:  # Проверяет, отмечен ли чекбокс.
                # Если чекбокс отмечен, добавляет его текст (метку) в список selected_reactions.
                selected_reactions.append(checkbox.label)

        save_reactions(reactions=selected_reactions,
                       path_to_the_file='user_settings/reactions/reactions.json')  # Сохраняем реакцию в json файл
        page.go("/settings")  # Изменение маршрута в представлении существующих настроек

    # Кнопка "Готово" (button) и связывает ее с функцией button_clicked.
    button = ft.ElevatedButton("Готово", on_click=button_clicked)

    page.views.append(
        ft.View(
            "/settings",
            controls=[
                t,  # Добавляет текстовое поле t на страницу (page).
                ft.Column([  # Добавляет все чекбоксы и кнопку на страницу (page) в виде колонок.
                    ft.Row([c1, c2, c3, c4, c5, c6, c49]),
                    ft.Row([c7, c8, c9, c10, c11, c48, c47]),
                    ft.Row([c19, c20, c21, c23, c24, c47, c46]),
                    ft.Row([c25, c26, c27, c28, c29, c30, c45]),
                    ft.Row([c31, c32, c33, c34, c35, c36, c44]),
                    ft.Row([c37, c38, c39, c41, c42, c43]),
                    ft.Row([c12, c13, c14, c15, c16, c17, c18]),
                    ft.Row([c40, c22, c34, c35, c48, c49]),
                ]),
                button,  # Добавляет кнопку на страницу (page).
            ]
        )
    )


def writing_members(page: ft.Page, db_handler) -> None:
    """Запись username в software_database.db в графическое окно Flet"""
    text_to_send = ft.TextField(label="Введите список username", multiline=True, max_lines=19)

    def btn_click(e) -> None:
        db_handler.write_to_single_column_table(name_database="members",
                                                database_columns="username, id, access_hash, first_name, last_name, "
                                                                 "user_phone, online_at, photos_id, user_premium",
                                                into_columns="members (username)",
                                                recorded_data=text_to_send.value.split())

        page.go("/settings")  # Изменение маршрута в представлении существующих настроек
        page.update()

    button = ft.ElevatedButton("Готово", on_click=btn_click)

    page.views.append(
        ft.View(
            "/settings",
            [
                text_to_send,
                ft.Column(),  # Заполнитель для приветствия или другого содержимого (необязательно)
                button,
            ],
        )
    )
