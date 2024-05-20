import configparser
import getpass
import json
import os

import flet as ft
from rich import print
from telethon import TelegramClient
from telethon.errors import *

from system.account_actions.creating.account_registration import telegram_connects
from system.auxiliary_functions.global_variables import console, ConfigReader
from system.menu.app_gui import create_window
from system.notification.notification import app_notifications

config = configparser.ConfigParser(empty_lines_in_values=False, allow_no_value=True)
config.read("user_settings/config.ini")

configs_reader = ConfigReader()
api_id_data, api_hash_data = configs_reader.get_api_id_data_api_hash_data()


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
    db_handler.write_data_to_db(creating_a_table="CREATE TABLE IF NOT EXISTS config(phone)",
                                writing_data_to_a_table="INSERT INTO config (phone) VALUES (?)",
                                entities=entities)
    # Подключение к Telegram, возвращаем client для дальнейшего отключения сессии
    client = telegram_connect(phone_data, db_handler)
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

    def main_inviting(page) -> None:
        create_window(page=page, width=600, height=600, resizable=False)  # Создаем окно с размером 600 на 600 пикселей
        proxy_type = ft.TextField(label="Введите тип прокси, например SOCKS5: ", multiline=True, max_lines=19)
        addr_type = ft.TextField(label="Введите ip адрес, например 194.67.248.9: ", multiline=True, max_lines=19)
        port_type = ft.TextField(label="Введите порт прокси, например 9795: ", multiline=True, max_lines=19)
        username_type = ft.TextField(label="Введите username, например NnbjvX: ", multiline=True, max_lines=19)
        password_type = ft.TextField(label="Введите пароль, например ySfCfk: ", multiline=True, max_lines=19)
        greetings = ft.Column()

        def btn_click(e) -> None:
            print(
                f"Вы ввели: {proxy_type.value, addr_type.value, port_type.value, username_type.value, password_type.value}")
            rdns_types = "True"
            proxy = [proxy_type.value, addr_type.value, port_type.value, username_type.value, password_type.value,
                     rdns_types]
            db_handler.save_proxy_data_to_db(proxy=proxy)
            page.window_close()
            page.update()

        page.add(proxy_type, addr_type, port_type, username_type, password_type, greetings,
                 ft.ElevatedButton("Готово", on_click=btn_click), greetings, )

    ft.app(target=main_inviting)  # Создаем окно


def recording_the_time_between_chat_messages(variable):
    """
    Запись времени между сообщениями
    :param variable: название переменной в файле config.ini
    :return: None
    """

    def main_inviting(page) -> None:
        create_window(page=page, width=300, height=300, resizable=False)  # Создаем окно с размером 300 на 300 пикселей
        smaller_time = ft.TextField(label="Время в минутах (меньшее)", autofocus=True)
        larger_time = ft.TextField(label="Время в минутах (большее)", autofocus=True)
        greetings = ft.Column()

        def btn_click(e) -> None:
            try:
                smaller_times = int(smaller_time.value)
                larger_times = int(larger_time.value)

                if smaller_times < larger_times:  # Проверяем, что первое время меньше второго
                    # Если условие прошло проверку, то возвращаем первое и второе время
                    print(f"Вы ввели:\n{smaller_times} минут (меньшее время)\n{larger_times} минут (большее время)")
                    config = recording_limits_file(str(smaller_times), str(larger_times), variable=variable)
                    writing_settings_to_a_file(config)
                    page.window_close()
            except ValueError:
                pass

            page.update()
            smaller_time.focus()

        page.add(smaller_time, larger_time, ft.ElevatedButton("Готово", on_click=btn_click), greetings, )

    ft.app(target=main_inviting)


def create_main_window(variable) -> None:
    """
    :param variable: название переменной в файле config.ini
    :return: None
    """

    def main_inviting(page) -> None:
        create_window(page=page, width=300, height=300, resizable=False)  # Создаем окно с размером 300 на 300 пикселей
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


def record_account_name_newsletter():
    def main_inviting(page) -> None:
        create_window(page=page, width=600, height=600, resizable=False)  # Создаем окно с размером 600 на 600 пикселей
        text_to_send = ft.TextField(label="Введите название аккаунта для отправки сообщений по чатам",
                                    multiline=True, max_lines=19)
        greetings = ft.Column()

        def btn_click(e) -> None:
            print(f"Вы ввели: {text_to_send}")
            config.get("account_name_newsletter", "account_name_newsletter")
            config.set("account_name_newsletter", "account_name_newsletter", text_to_send.value)
            writing_settings_to_a_file(config)

            page.window_close()
            page.update()

        page.add(text_to_send, ft.ElevatedButton("Готово", on_click=btn_click), greetings, )

    ft.app(target=main_inviting)


def recording_text_for_sending_messages() -> None:
    """
    Запись текста в файл для отправки сообщений в Telegram в формате JSON. Данные записываются в файл с именем
    <имя файла>.json и сохраняются в формате JSON.
    """

    def main_inviting(page) -> None:
        create_window(page=page, width=600, height=600, resizable=False)  # Создаем окно с размером 600 на 600 пикселей
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


def recording_the_time_to_launch_an_invite_every_day() -> None:
    def main_inviting(page) -> None:
        create_window(page=page, width=300, height=300, resizable=False)  # Создаем окно с размером 300 на 300 пикселей
        hour = ft.TextField(label="Время в часах :", autofocus=True)
        minutes = ft.TextField(label="Время в минутах:")
        greetings = ft.Column()

        def btn_click(e) -> None:
            try:
                if not 0 <= int(hour.value) < 24:
                    print('Введите часы в пределах от 0 до 23!')
                    return
                if not 0 <= int(minutes.value) < 60:
                    print('Введите минуты в пределах от 0 до 59!')
                    return
                config.get("hour_minutes_every_day", "hour")
                config.set("hour_minutes_every_day", "hour", str(hour.value))
                config.get("hour_minutes_every_day", "minutes")
                config.set("hour_minutes_every_day", "minutes", str(minutes.value))
                writing_settings_to_a_file(config)
                page.window_close()  # Закрываем окно
            except ValueError:
                pass
            page.update()  # Обновляем страницу

        page.add(hour, minutes, ft.ElevatedButton("Готово", on_click=btn_click), greetings, )

    ft.app(target=main_inviting)

# def recording_the_time_to_launch_an_invite_every_day(page: ft.Page) -> None:
#     hour_textfield = ft.TextField(label="Час запуска приглашений (0-23):", autofocus=True, value="")
#     minutes_textfield = ft.TextField(label="Минуты запуска приглашений (0-59):", value="")
#
#     def btn_click(e) -> None:
#         try:
#             hour = int(hour_textfield.value)
#             minutes = int(minutes_textfield.value)
#
#             if not 0 <= hour < 24:
#                 print('Введите часы в пределах от 0 до 23!')
#                 return
#             if not 0 <= minutes < 60:
#                 print('Введите минуты в пределах от 0 до 59!')
#                 return
#
#             # Assuming config is a dictionary-like object
#             config.get("hour_minutes_every_day", "hour")
#             config.set("hour_minutes_every_day", "hour", str(hour))
#             config.get("hour_minutes_every_day", "minutes")
#             config.set("hour_minutes_every_day", "minutes", str(minutes))
#             writing_settings_to_a_file(config)
#             page.go("/settings")  # Change route to existing settings view
#             # page.window_close()  # Закрываем окно
#         except ValueError:
#             print('Введите числовые значения для часов и минут!')
#         page.update()  # Обновляем страницу
#
#     button = ft.ElevatedButton("Готово", on_click=btn_click)
#
#     page.views.append(
#         ft.View(
#             "/settings",
#             [
#                 hour_textfield,
#                 minutes_textfield,
#                 ft.Column(),  # Placeholder for greetings or other content (optional)
#                 button,
#             ],
#         )
#     )


if __name__ == "__main__":
    writing_link_to_the_group()
    recording_the_time_to_launch_an_invite_every_day()
    record_account_limits()
    recording_text_for_sending_messages()
