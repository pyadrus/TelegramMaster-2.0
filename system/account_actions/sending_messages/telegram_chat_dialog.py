import datetime
import json
import os
import random
import time

import flet as ft
from loguru import logger
from rich import print
from rich.progress import track
from telethon.errors import *

from system.account_actions.subscription.subscription import subscribe_to_the_group_and_send_the_link
from system.auxiliary_functions.auxiliary_functions import record_and_interrupt
from system.auxiliary_functions.global_variables import console, time_sending_messages
from system.error.telegram_errors import record_account_actions
from system.menu.app_gui import program_window, done_button, create_window
from system.notification.notification import app_notifications
from system.telegram_actions.telegram_actions import telegram_connect_and_output_name

creating_a_table = """SELECT * from writing_group_links"""
writing_data_to_a_table = """DELETE from writing_group_links where writing_group_links = ?"""
event: str = "Рассылаем сообщение по чатам Telegram"


def connecting_tg_account_creating_list_groups(db_handler):
    """Подключение к аккаунту телеграмм и формирование списка групп"""
    app_notifications(notification_text=event)  # Выводим уведомление
    # Открываем базу данных для работы с аккаунтами user_settings/software_database.db
    records: list = db_handler.open_and_read_data("config")  # Открываем базу данных
    print(f"[medium_purple3]Всего accounts: {len(records)}")
    for row in records:
        # Подключение к Telegram и вывод имя аккаунта в консоль / терминал
        client, phone = telegram_connect_and_output_name(row, db_handler)
        records: list = db_handler.open_and_read_data("writing_group_links")  # Открываем базу данных
        print(f"[medium_purple3]Всего групп: {len(records)}")

    return client, phone, records


def sending_files_via_chats(db_handler) -> None:
    """Рассылка файлов по чатам"""
    # Спрашиваем у пользователя, через какое время будем отправлять сообщения
    link_to_the_file: str = console.input(
        "[medium_purple3][+] Введите название файла с папки user_settings/files_to_send: ")
    message_text_time: str = console.input(
        "[medium_purple3][+] Введите время, через какое время будем отправлять файлы: ")
    client, phone, records = connecting_tg_account_creating_list_groups(db_handler)
    for groups in records:  # Поочередно выводим записанные группы
        groups_wr = subscribe_to_the_group_and_send_the_link(client, groups, phone, db_handler)
        description_action = f"Sending messages to a group: {groups_wr}"
        try:
            client.send_file(groups_wr, f"user_settings/files_to_send/{link_to_the_file}")  # Рассылаем файлов по чатам
            # Работу записываем в лог файл, для удобства слежения, за изменениями
            time.sleep(int(message_text_time))
            actions: str = f"[medium_purple3]Сообщение в группу {groups_wr} написано!"
            record_account_actions(phone, description_action, event, actions, db_handler)
        except ChannelPrivateError:
            actions: str = "Указанный канал является приватным, или вам запретили подписываться."
            record_account_actions(phone, description_action, event, actions, db_handler)
            db_handler.write_data_to_db(creating_a_table, writing_data_to_a_table, groups_wr)
        except PeerFloodError:
            actions: str = "Предупреждение о Flood от Telegram."
            record_and_interrupt(actions, phone, description_action, event, db_handler)
            break  # Прерываем работу и меняем аккаунт
        except FloodWaitError as e:
            actions: str = f'Flood! wait for {str(datetime.timedelta(seconds=e.seconds))}'
            record_account_actions(phone, description_action, event, actions, db_handler)
            print(f'Спим {e.seconds} секунд')
            time.sleep(e.seconds)
        except UserBannedInChannelError:
            actions: str = "Вам запрещено отправлять сообщения в супергруппу."
            record_and_interrupt(actions, phone, description_action, event, db_handler)
            break  # Прерываем работу и меняем аккаунт
        except ChatWriteForbiddenError:
            actions = "Вам запрещено писать в супергруппу / канал."
            record_and_interrupt(actions, phone, description_action, event, db_handler)
            break  # Прерываем работу и меняем аккаунт
        except (TypeError, UnboundLocalError):
            continue  # Записываем ошибку в software_database.db и продолжаем работу
        client.disconnect()  # Разрываем соединение Telegram


def sending_messages_files_via_chats() -> None:
    """Рассылка сообщений + файлов по чатам"""
    root, text = program_window()

    def output_values_from_the_input_field(db_handler) -> None:
        """Выводим значения с поля ввода (то что ввел пользователь)"""
        message_text = text.get("1.0", 'end-1c')
        closing_the_input_field()
        print("[medium_purple3][+] Введите текс сообщения которое будем отправлять в чаты: ")
        link_to_the_file: str = console.input(
            "[medium_purple3][+] Введите название файла с папки user_settings/files_to_send: ")
        # Спрашиваем у пользователя, через какое время будем отправлять сообщения
        message_text_time: str = console.input(
            "[medium_purple3][+] Введите время, через какое время будем отправлять сообщения: ")
        event: str = f"Рассылаем сообщение + файлы по чатам Telegram"
        client, phone, records = connecting_tg_account_creating_list_groups(db_handler)
        for groups in records:  # Поочередно выводим записанные группы
            groups_wr = subscribe_to_the_group_and_send_the_link(client, groups, phone, db_handler)
            description_action = f"Sending messages to a group: {groups_wr}"
            try:
                client.send_message(entity=groups_wr, message=message_text)  # Рассылаем сообщение по чатам
                # Рассылаем файлов по чатам
                client.send_file(groups_wr, f"user_settings/files_to_send/{link_to_the_file}")
                # Работу записываем в лог файл, для удобства слежения, за изменениями
                time.sleep(int(message_text_time))
                actions: str = f"[medium_purple3]Сообщение в группу {groups_wr} написано!"
                record_account_actions(phone, description_action, event, actions, db_handler)
            except ChannelPrivateError:
                actions: str = "Указанный канал является приватным, или вам запретили подписываться."
                record_account_actions(phone, description_action, event, actions, db_handler)
                db_handler.write_data_to_db(creating_a_table, writing_data_to_a_table, groups_wr)
            except PeerFloodError:
                actions = "Предупреждение о Flood от Telegram."
                record_and_interrupt(actions, phone, description_action, event, db_handler)
                break  # Прерываем работу и меняем аккаунт
            except FloodWaitError as e:
                actions: str = f'Flood! wait for {str(datetime.timedelta(seconds=e.seconds))}'
                record_account_actions(phone, description_action, event, actions, db_handler)
                print(f'Спим {e.seconds} секунд')
                time.sleep(e.seconds)
            except UserBannedInChannelError:
                actions = "Вам запрещено отправлять сообщения в супергруппу."
                record_and_interrupt(actions, phone, description_action, event, db_handler)
                break  # Прерываем работу и меняем аккаунт
            except ChatWriteForbiddenError:
                actions = "Вам запрещено писать в супергруппу / канал."
                record_and_interrupt(actions, phone, description_action, event, db_handler)
                break  # Прерываем работу и меняем аккаунт
            except (TypeError, UnboundLocalError):
                continue  # Записываем ошибку в software_database.db и продолжаем работу
        client.disconnect()  # Разрываем соединение Telegram

    def closing_the_input_field() -> None:
        """Закрываем программу"""
        root.destroy()

    done_button(root, output_values_from_the_input_field)  # Кнопка "Готово"
    root.mainloop()  # Запускаем программу


def sending_messages_chats(db_handler) -> None:
    entities = []  # Создаем словарь с именами найденных аккаунтов в папке user_settings/accounts
    for x in os.listdir(path="user_settings/message"):
        if x.endswith(".json"):
            file = os.path.splitext(x)[0]
            logger.info(f"Найденные файлы: {file}.json")  # Выводим имена найденных аккаунтов
            entities.append([file])

    if entities:  # Проверяем, что список не пустой, если он не пустой
        # Выбираем рандомный файл для чтения
        random_file = random.choice(entities)
        logger.info(f"Выбран файл для чтения: {random_file[0]}.json")
        # Открываем выбранный файл с настройками
        with open(f"user_settings/message/{random_file[0]}.json", "r", encoding="utf-8") as file:
            data = json.load(file)

    logger.info(data)
    sending_messages_via_chats_time(data, db_handler)


def sending_messages_via_chats_time(message_text, db_handler) -> None:
    """Массовая рассылка в чаты"""

    client, phone, records = connecting_tg_account_creating_list_groups(db_handler)
    for groups in records:  # Поочередно выводим записанные группы
        groups_wr = subscribe_to_the_group_and_send_the_link(client, groups, phone, db_handler)
        description_action = f"Sending messages to a group: {groups_wr}"
        try:
            client.send_message(entity=groups_wr, message=message_text)  # Рассылаем сообщение по чатам

            # Convert time from minutes to seconds
            time_in_seconds = time_sending_messages * 60
            for _ in track(range(time_in_seconds), description=f"[red]Спим {time_sending_messages} минуты / минут..."):
                time.sleep(1)  # Sleep for 1 second

            actions = f"[medium_purple3]Сообщение в группу {groups_wr} написано!"
            record_account_actions(phone, description_action, event, actions, db_handler)
        except ChannelPrivateError:
            actions = "Указанный канал является приватным, или вам запретили подписываться."
            record_account_actions(phone, description_action, event, actions, db_handler)
            db_handler.write_data_to_db(creating_a_table, writing_data_to_a_table, groups_wr)
        except PeerFloodError:
            actions = "Предупреждение о Flood от Telegram."
            record_and_interrupt(actions, phone, description_action, event, db_handler)
            break  # Прерываем работу и меняем аккаунт
        except FloodWaitError as e:
            actions: str = f'Flood! wait for {str(datetime.timedelta(seconds=e.seconds))}'
            record_account_actions(phone, description_action, event, actions, db_handler)
            print(f'Спим {e.seconds} секунд')
            time.sleep(e.seconds)
        except UserBannedInChannelError:
            actions = "Вам запрещено отправлять сообщения в супергруппу."
            record_and_interrupt(actions, phone, description_action, event, db_handler)
            break  # Прерываем работу и меняем аккаунт
        except (TypeError, UnboundLocalError):
            continue  # Записываем ошибку в software_database.db и продолжаем работу
        except ChatWriteForbiddenError:
            actions = "Вам запрещено писать в супергруппу / канал."
            record_and_interrupt(actions, phone, description_action, event, db_handler)
            break  # Прерываем работу и меняем аккаунт
    client.disconnect()  # Разрываем соединение Telegram


def output_the_input_field(db_handler) -> None:
    """Выводим ссылки в поле ввода поле ввода для записи ссылок групп"""

    def main_inviting(page) -> None:
        create_window(page=page, width=600, height=600, resizable=False)  # Создаем окно с размером 600 на 600 пикселей
        text_to_send = ft.TextField(label="Введите список ссылок на группы", multiline=True, max_lines=19)
        greetings = ft.Column()

        def btn_click(e) -> None:
            print(f"Вы ввели: {text_to_send}")
            db_handler.open_and_read_data("writing_group_links")  # Удаление списка с группами
            db_handler.write_to_single_column_table("writing_group_links", text_to_send.value.split())
            page.window_close()
            page.update()

        page.add(text_to_send, ft.ElevatedButton("Готово", on_click=btn_click), greetings, )

    ft.app(target=main_inviting)


if __name__ == "__main__":
    sending_messages_files_via_chats()  # Отправляем сообщения через чаты
