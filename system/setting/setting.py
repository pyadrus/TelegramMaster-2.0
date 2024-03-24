import configparser
import getpass
import json
import os
import tkinter as tk
from tkinter import ttk

import flet as ft
from rich import print
from telethon import TelegramClient
from telethon.errors import *

from system.account_actions.creating.account_registration import telegram_connects
from system.auxiliary_functions.global_variables import console, api_id_data, api_hash_data
from system.menu.app_gui import program_window_with_dimensions
from system.notification.notification import app_notifications

config = configparser.ConfigParser(empty_lines_in_values=False, allow_no_value=True)
config.read("user_settings/config.ini")

creating_a_table = "CREATE TABLE IF NOT EXISTS config(id, hash, phone)"
writing_data_to_a_table = "INSERT INTO config (id, hash, phone) VALUES (?, ?, ?)"


def recording_the_time_to_launch_an_invite_every_day() -> None:
    def recoding_time() -> None:
        # Получаем значения из полей ввода
        hour = hour_time_entry.get()
        minutes = minutes_time_entry.get()
        # Проверка на пустой ввод
        if not hour or not minutes:
            result_label.config(text="Пожалуйста, введите оба поля!")
            return
        # Проверяем, что оба поля были заполнены целыми числами
        try:
            hour = int(hour)
            minutes = int(minutes)
        except ValueError:
            # Если пользователь ввел не число, выводим сообщение об ошибке
            result_label.config(text="Пожалуйста, введите целые числа!")
            return
        if not 0 <= hour < 24:
            # Если часы не в пределах от 0 до 23, выводим сообщение об ошибке
            result_label.config(text="Пожалуйста, введите часы в пределах от 0 до 23!")
            return
        if not 0 <= minutes < 60:
            # Если минуты не в пределах от 0 до 59, выводим сообщение об ошибке
            result_label.config(text="Пожалуйста, введите минуты в пределах от 0 до 59!")
            return
        config.get("hour_minutes_every_day", "hour")
        config.set("hour_minutes_every_day", "hour", str(hour))
        config.get("hour_minutes_every_day", "minutes")
        config.set("hour_minutes_every_day", "minutes", str(minutes))
        writing_settings_to_a_file(config)
        root.destroy()

    root = program_window_with_dimensions(geometry="300x140")
    root.resizable(False, False)  # Запретить масштабирование окна
    s = ttk.Style()  # Установка стиля оформления
    s.theme_use("winnative")
    hour_time_label = ttk.Label(root, text="Время в часах :")
    hour_time_label.pack()
    hour_time_entry = ttk.Entry(root, width=45)
    hour_time_entry.pack()
    # Создаем второе текстовое поле и связанный с ним текстовый метка
    minutes_time_label = ttk.Label(root, text="Время в минутах:")
    minutes_time_label.pack()
    minutes_time_entry = ttk.Entry(root, width=45)
    minutes_time_entry.pack()
    button = ttk.Button(root, text="Готово", command=recoding_time)  # Создаем кнопку
    button.pack()
    result_label = ttk.Label(root, text="")  # Создаем метку для вывода результата
    result_label.pack()
    root.mainloop()  # Запускаем главный цикл обработки событий


def record_account_limits() -> configparser.ConfigParser:
    """Запись лимитов на аккаунт"""
    limits = console.input("[magenta][+] Введите лимит на аккаунт : ")
    config.get("account_limits", "limits")
    config.set("account_limits", "limits", limits)
    return config


def record_message_limits() -> configparser.ConfigParser:
    """Запись лимитов на сообщения"""
    limits = console.input("[magenta][+] Введите лимит на аккаунт : ")
    config.get("message_limits", "message_limits")
    config.set("message_limits", "message_limits", limits)
    return config


def record_device_type() -> configparser.ConfigParser():
    """Запись типа устройства например: Samsung SGH600, Android 9 (P30), 4.2.1,
    Vivo V9, Android 9 (P30), 4.2.1"""
    try:
        device_model = console.input("[magenta][+] Введите модель устройства: ")
        config.get("device_model", "device_model")
        config.set("device_model", "device_model", device_model)
    except configparser.NoSectionError:  # Если в user_settings/config.ini нет записи, то создаем ее
        config["device_model"] = {"device_model": device_model}
    try:
        system_version = console.input("[magenta][+] Введите версию операционной системы: ")
        config.get("system_version", "system_version")
        config.set("system_version", "system_version", system_version)
    except configparser.NoSectionError:  # Если в user_settings/config.ini нет записи, то создаем ее
        config["system_version"] = {"system_version": system_version}
    try:
        app_version = console.input("[magenta][+] Введите версию приложения: ")
        config.get("app_version", "app_version")
        config.set("app_version", "app_version", app_version)
    except configparser.NoSectionError:  # Если в user_settings/config.ini нет записи, то создаем ее
        config["app_version"] = {"app_version": app_version}
    return config


def writing_settings_to_a_file(config) -> None:
    """Запись данных в файл user_settings/config.ini"""
    with open("user_settings/config.ini", "w") as setup:  # Открываем файл в режиме записи
        config.write(setup)  # Записываем данные в файл


def writing_api_id_api_hash() -> configparser.ConfigParser:
    """Записываем api, hash полученный с помощью регистрации приложения на сайте https://my.telegram.org/auth"""
    api_id_data = console.input("[magenta][+] Введите api_id : ")
    config.get("telegram_settings", "id")
    config.set("telegram_settings", "id", api_id_data)
    api_hash_data = console.input("[magenta][+] Введите api_hash : ")
    config.get("telegram_settings", "hash")
    config.set("telegram_settings", "hash", api_hash_data)
    return config


def writing_link_to_the_group() -> configparser.ConfigParser:
    """Записываем ссылку для inviting групп"""
    target_group_entity_user = console.input("[magenta][+] Введите ссылку на группу : ")  # Вводим ссылку на группу
    # Находим ссылку в файле и меняем на свою
    config.get("link_to_the_group", "target_group_entity")
    config.set("link_to_the_group", "target_group_entity", target_group_entity_user)
    return config


def recording_limits_file(time_1, time_2, variable: str) -> configparser.ConfigParser:
    """Запись данных в файл user_settings/time_inviting.ini"""
    config.get(f"{variable}", f"{variable}_1")
    config.set(f"{variable}", f"{variable}_1", time_1)
    config.get(f"{variable}", f"{variable}_2")
    config.set(f"{variable}", f"{variable}_2", time_2)
    return config


def connecting_new_account(db_handler) -> None:
    """Вводим данные в базу данных user_settings/software_database.db"""
    phone_data = console.input("[magenta][+] Введите номер телефона : ")  # Вводим номер телефона
    entities = (api_id_data, api_hash_data, phone_data)
    db_handler.write_data_to_db(creating_a_table, writing_data_to_a_table, entities)
    # Подключение к Telegram, возвращаем client для дальнейшего отключения сессии
    client = telegram_connect(phone_data)
    client.disconnect()  # Разрываем соединение telegram
    app_notifications(notification_text="Аккаунт подсоединился!")  # Выводим уведомление


def telegram_connect(phone, db_handler) -> TelegramClient:
    """Account telegram connect, с проверкой на валидность, если ранее не было соединения, то запрашиваем код"""

    client = telegram_connects(db_handler, session=f"user_settings/accounts/{phone}")

    if not client.is_user_authorized():
        client.send_code_request(phone)
        try:
            # Если ранее аккаунт не подсоединялся, то просим ввести код подтверждения
            client.sign_in(phone, code=console.input("[medium_purple3][+] Введите код: "))
        except SessionPasswordNeededError:
            """
            https://telethonn.readthedocs.io/en/latest/extra/basic/creating-a-client.html#two-factor-authorization-2fa
            """
            # Если аккаунт имеет password, то просим пользователя ввести пароль
            client.sign_in(password=getpass.getpass())
        except ApiIdInvalidError:
            print("[medium_purple3][!] Не валидные api_id/api_hash")
    return client


def creating_the_main_window_for_proxy_data_entry(db_handler) -> None:
    """Создание главного окна для ввода дынных proxy"""
    print("Proxy IPV6 - НЕ РАБОТАЮТ")

    def recording_proxy_data() -> list:
        """Запись данных для proxy, Proxy IPV6 - НЕ РАБОТАЮТ"""
        proxy_types = proxy_type_entry.get()
        addr_types = addr_type_entry.get()
        port_types = port_type_entry.get()
        username_types = username_type_entry.get()
        password_types = password_type_entry.get()
        rdns_types = "True"
        proxy = [proxy_types, addr_types, port_types, username_types, password_types, rdns_types]
        root.destroy()
        return proxy

    root = program_window_with_dimensions(geometry="300x250")
    root.resizable(False, False)  # Запретить масштабирование окна
    # Создаем первое текстовое поле и связанный с ним текстовый метка
    proxy_type = tk.Label(root, text="Введите тип прокси, например SOCKS5: ")
    proxy_type.pack()
    proxy_type_entry = tk.Entry(root, width=45)
    proxy_type_entry.pack()
    # Создаем второе текстовое поле и связанный с ним текстовый метка
    addr_type = tk.Label(root, text="Введите ip адрес, например 194.67.248.9: ")
    addr_type.pack()
    addr_type_entry = tk.Entry(root, width=45)
    addr_type_entry.pack()
    # Создаем третье текстовое поле и связанный с ним текстовый метка
    port_type = tk.Label(root, text="Введите порт прокси, например 9795: ")
    port_type.pack()
    port_type_entry = tk.Entry(root, width=45)
    port_type_entry.pack()
    # Создаем четвертое текстовое поле и связанный с ним текстовый метка
    username_type = tk.Label(root, text="Введите username, например NnbjvX: ")
    username_type.pack()
    username_type_entry = tk.Entry(root, width=45)
    username_type_entry.pack()
    # Создаем пятое текстовое поле и связанный с ним текстовый метка
    password_type = tk.Label(root, text="Введите password, например ySfCfk: ")
    password_type.pack()
    password_type_entry = tk.Entry(root, width=45)
    password_type_entry.pack()
    # Создаем кнопку
    button = tk.Button(root, text="Готово",
                       command=lambda: db_handler.save_proxy_data_to_db(proxy=recording_proxy_data()))
    button.pack()
    result_label = tk.Label(root, text="")  # Создаем метку для вывода результата
    result_label.pack()
    root.mainloop()  # Запускаем главный цикл обработки событий


def recording_the_time_between_chat_messages(variable):
    """Запись времени между сообщениями"""

    def main_inviting(page) -> None:
        page.window_width = 300  # ширина окна
        page.window_height = 300  # высота окна
        page.window_resizable = False  # Запрет на изменение размера окна
        smaller_time = ft.TextField(label="Время в минутах", autofocus=True)
        greetings = ft.Column()

        def btn_click(e) -> None:
            try:
                smaller_times = int(smaller_time.value)

                config.get(f"{variable}", f"{variable}")
                config.set(f"{variable}", f"{variable}", str(smaller_times))  # Записываем в файл значение
                writing_settings_to_a_file(config)
                page.window_close()
            except ValueError:
                pass

            page.update()
            smaller_time.focus()

        page.add(smaller_time, ft.ElevatedButton("Готово", on_click=btn_click), greetings, )

    ft.app(target=main_inviting)


def create_main_window(variable) -> None:
    """
    :param variable: название переменной в файле config.ini
    :return: None
    """

    def main_inviting(page) -> None:
        page.window_width = 300  # ширина окна
        page.window_height = 300  # высота окна
        page.window_resizable = False  # Запрет на изменение размера окна
        smaller_time = ft.TextField(label="Время в секундах (меньшее)", autofocus=True)
        larger_time = ft.TextField(label="Время в секундах (большее)")
        greetings = ft.Column()

        def btn_click(e) -> None:
            try:
                smaller_times = int(smaller_time.value)
                larger_times = int(larger_time.value)

                if smaller_times < larger_times:  # Проверяем, что первое время меньше второго
                    # Если условие прошло проверку, то возвращаем первое и второе время
                    print(f"Вы ввели:\n{smaller_times} секунд (меньшее время)\n{larger_times} секунд (большее время)")
                    config = recording_limits_file(str(smaller_times), str(larger_times), variable=variable)
                    writing_settings_to_a_file(config)
                    page.window_close()
            except ValueError:
                pass

            page.update()
            smaller_time.focus()

        page.add(smaller_time, larger_time, ft.ElevatedButton("Готово", on_click=btn_click), greetings, )

    ft.app(target=main_inviting)


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


def recording_text_for_sending_messages() -> None:
    """
    Запись текста в файл для отправки сообщений в Telegram в формате JSON. Данные записываются в файл с именем
    <имя файла>.json и сохраняются в формате JSON.
    """

    def main_inviting(page) -> None:
        page.window_width = 600  # ширина окна
        page.window_height = 600  # высота окна
        page.window_resizable = False  # Запрет на изменение размера окна
        text_to_send = ft.TextField(label="Введите текст сообщения", multiline=True, max_lines=19)
        greetings = ft.Column()

        def btn_click(e) -> None:
            print(f"Вы ввели: {text_to_send}")
            base_filename = 'user_settings/message/message'
            unique_filename = get_unique_filename(base_filename)
            save_message(reactions=text_to_send.value,
                         path_to_the_file=unique_filename)  # Сохраняем данные в файл
            page.window_close()
            page.update()

        page.add(text_to_send, ft.ElevatedButton("Готово", on_click=btn_click), greetings, )

    ft.app(target=main_inviting)


if __name__ == "__main__":
    writing_link_to_the_group()
    recording_the_time_to_launch_an_invite_every_day()
    record_account_limits()
    recording_text_for_sending_messages()
