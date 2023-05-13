# -*- coding: utf-8 -*-
import sys
import time
from tkinter import *

from rich import print
from telethon.errors import *

from system.actions.subscription.subscription import subscribe_to_the_group_and_send_the_link
from system.auxiliary_functions.auxiliary_functions import deleting_files_if_available
from system.auxiliary_functions.auxiliary_functions import record_and_interrupt
from system.auxiliary_functions.global_variables import console
from system.error.telegram_errors import record_account_actions
from system.menu.gui_program import program_window
from system.notification.notification import app_notifications
from system.sqlite_working_tools.sqlite_working_tools import open_the_db_and_read_the_data
from system.sqlite_working_tools.sqlite_working_tools import write_data_to_db
from system.sqlite_working_tools.sqlite_working_tools import write_to_single_column_table
from system.telegram_actions.telegram_actions import connect_to_telegram_account_and_output_name

folder, files = "setting_user", "members_group.csv"
creating_a_table = """SELECT * from writing_group_links"""
writing_data_to_a_table = """DELETE from writing_group_links where writing_group_links = ?"""
event: str = f"Рассылаем сообщение по чатам Telegram"


def sending_files_via_chats() -> None:
    """Рассылка файлов по чатам"""
    # Спрашиваем у пользователя, через какое время будем отправлять сообщения
    link_to_the_file: str = console.input("[bold red][+] Введите название файла с папки setting_user/files_to_send: ")
    message_text_time: str = console.input("[bold red][+] Введите время, через какое время будем отправлять файлы: ")
    # Выводим уведомление, если операционная система windows 7, то выводим уведомление в консоль
    app_notifications(notification_text=event)
    # Открываем базу данных для работы с аккаунтами setting_user/software_database.db
    records: list = open_the_db_and_read_the_data(name_database_table="config")
    print(f"[bold red]Всего accounts: {len(records)}")
    for row in records:
        # Подключение к Telegram и вывод имя аккаунта в консоль / терминал
        client, phone = connect_to_telegram_account_and_output_name(row)
        try:
            records: list = open_the_db_and_read_the_data(name_database_table="writing_group_links")
            print(f"[bold red]Всего групп: {len(records)}")
            for groups in records:  # Поочередно выводим записанные группы
                groups_wr = subscribe_to_the_group_and_send_the_link(client, groups, phone)
                description_action = f"Sending messages to a group: {groups_wr}"
                try:
                    # Рассылаем файлов по чатам
                    client.send_file(groups_wr, f"setting_user/files_to_send/{link_to_the_file}")
                    # Работу записываем в лог файл, для удобства слежения, за изменениями
                    time.sleep(int(message_text_time))
                    actions: str = f"[bold red]Сообщение в группу {groups_wr} написано!"
                    record_account_actions(phone, description_action, event, actions)
                except ChannelPrivateError:
                    actions: str = "Указанный канал является приватным, или вам запретили подписываться."
                    record_account_actions(phone, description_action, event, actions)
                    write_data_to_db(creating_a_table, writing_data_to_a_table, groups_wr)
                except PeerFloodError:
                    actions: str = "Предупреждение о Flood от Telegram."
                    record_and_interrupt(actions, phone, description_action, event)
                    break  # Прерываем работу и меняем аккаунт
                except FloodWaitError as e:
                    actions: str = f'Flood! wait for {e.seconds} seconds'
                    record_account_actions(phone, description_action, event, actions)
                    print(f'Спим {e.seconds} секунд')
                    time.sleep(e.seconds)
                except UserBannedInChannelError:
                    actions: str = "Вам запрещено отправлять сообщения в супергруппу."
                    record_and_interrupt(actions, phone, description_action, event)
                    break  # Прерываем работу и меняем аккаунт
                except ChatWriteForbiddenError:
                    actions = "Вам запрещено писать в супергруппу / канал."
                    record_and_interrupt(actions, phone, description_action, event)
                    break  # Прерываем работу и меняем аккаунт
                except (TypeError, UnboundLocalError):
                    continue  # Записываем ошибку в software_database.db и продолжаем работу
            client.disconnect()  # Разрываем соединение Telegram
        except KeyError:
            sys.exit(1)


def sending_messages_files_via_chats() -> None:
    """Рассылка сообщений + файлов по чатам"""
    root, text = program_window()

    def output_values_from_the_input_field() -> None:
        """Выводим значения с поля ввода (то что ввел пользователь)"""
        message_text = text.get("1.0", 'end-1c')
        closing_the_input_field()
        print("[bold red][+] Введите текс сообщения которое будем отправлять в чаты: ")
        link_to_the_file: str = console.input(
            "[bold red][+] Введите название файла с папки setting_user/files_to_send: ")
        # Спрашиваем у пользователя, через какое время будем отправлять сообщения
        message_text_time: str = console.input(
            "[bold red][+] Введите время, через какое время будем отправлять сообщения: ")
        event: str = f"Рассылаем сообщение + файлы по чатам Telegram"
        # Выводим уведомление, если операционная система windows 7, то выводим уведомление в консоль
        app_notifications(notification_text=event)
        # Открываем базу данных для работы с аккаунтами setting_user/software_database.db
        records: list = open_the_db_and_read_the_data(name_database_table="config")
        print(f"[bold red]Всего accounts: {len(records)}")
        for row in records:
            # Подключение к Telegram и вывод имя аккаунта в консоль / терминал
            client, phone = connect_to_telegram_account_and_output_name(row)
            try:
                # Открываем базу данных
                records: list = open_the_db_and_read_the_data(name_database_table="writing_group_links")
                print(f"[bold red]Всего групп: {len(records)}")
                for groups in records:  # Поочередно выводим записанные группы
                    groups_wr = subscribe_to_the_group_and_send_the_link(client, groups, phone)
                    description_action = f"Sending messages to a group: {groups_wr}"
                    try:
                        # Рассылаем сообщение по чатам
                        client.send_message(entity=groups_wr, message=message_text)
                        # Рассылаем файлов по чатам
                        client.send_file(groups_wr, f"setting_user/files_to_send/{link_to_the_file}")
                        # Работу записываем в лог файл, для удобства слежения, за изменениями
                        time.sleep(int(message_text_time))
                        actions: str = f"[bold red]Сообщение в группу {groups_wr} написано!"
                        record_account_actions(phone, description_action, event, actions)
                    except ChannelPrivateError:
                        actions: str = "Указанный канал является приватным, или вам запретили подписываться."
                        record_account_actions(phone, description_action, event, actions)
                        write_data_to_db(creating_a_table, writing_data_to_a_table, groups_wr)
                    except PeerFloodError:
                        actions = "Предупреждение о Flood от Telegram."
                        record_and_interrupt(actions, phone, description_action, event)
                        break  # Прерываем работу и меняем аккаунт
                    except FloodWaitError as e:
                        actions = f'Flood! wait for {e.seconds} seconds'
                        record_account_actions(phone, description_action, event, actions)
                        print(f'Спим {e.seconds} секунд')
                        time.sleep(e.seconds)
                    except UserBannedInChannelError:
                        actions = "Вам запрещено отправлять сообщения в супергруппу."
                        record_and_interrupt(actions, phone, description_action, event)
                        break  # Прерываем работу и меняем аккаунт
                    except ChatWriteForbiddenError:
                        actions = "Вам запрещено писать в супергруппу / канал."
                        record_and_interrupt(actions, phone, description_action, event)
                        break  # Прерываем работу и меняем аккаунт
                    except (TypeError, UnboundLocalError):
                        continue  # Записываем ошибку в software_database.db и продолжаем работу
                client.disconnect()  # Разрываем соединение Telegram
            except KeyError:
                sys.exit(1)

    def closing_the_input_field() -> None:
        """Закрываем программу"""
        root.destroy()

    # Создаем кнопку по нажатии которой выведется поле ввода. После ввода чатов данные запишутся во временный файл
    but = Button(root, text="Готово", command=output_values_from_the_input_field)
    but.pack()
    root.mainloop()  # Запускаем программу


def sending_messages_via_chats_time(message_text) -> None:
    """Массовая рассылка в чаты"""
    # Спрашиваем у пользователя, через какое время будем отправлять сообщения
    message_text_time: str = console.input(
        "[bold red][+] Введите время, через какое время будем отправлять сообщения: ")
    # Выводим уведомление, если операционная система windows 7, то выводим уведомление в консоль
    app_notifications(notification_text=event)
    # Открываем базу данных для работы с аккаунтами setting_user/software_database.db
    records: list = open_the_db_and_read_the_data(name_database_table="config")
    print(f"[bold red]Всего accounts: {len(records)}")
    for row in records:
        # Подключение к Telegram и вывод имя аккаунта в консоль / терминал
        client, phone = connect_to_telegram_account_and_output_name(row)
        try:
            # Открываем базу данных
            records: list = open_the_db_and_read_the_data(name_database_table="writing_group_links")
            print(f"[bold red]Всего групп: {len(records)}")
            for groups in records:  # Поочередно выводим записанные группы
                groups_wr = subscribe_to_the_group_and_send_the_link(client, groups, phone)
                description_action = f"Sending messages to a group: {groups_wr}"
                try:
                    # Рассылаем сообщение по чатам
                    client.send_message(entity=groups_wr, message=message_text)
                    # Работу записываем в лог файл, для удобства слежения, за изменениями
                    time.sleep(int(message_text_time))
                    actions = f"[bold red]Сообщение в группу {groups_wr} написано!"
                    record_account_actions(phone, description_action, event, actions)
                except ChannelPrivateError:
                    actions = "Указанный канал является приватным, или вам запретили подписываться."
                    record_account_actions(phone, description_action, event, actions)
                    write_data_to_db(creating_a_table, writing_data_to_a_table, groups_wr)
                except PeerFloodError:
                    actions = "Предупреждение о Flood от Telegram."
                    record_and_interrupt(actions, phone, description_action, event)
                    break  # Прерываем работу и меняем аккаунт
                except FloodWaitError as e:
                    actions = f'Flood! wait for {e.seconds} seconds'
                    record_account_actions(phone, description_action, event, actions)
                    print(f'Спим {e.seconds} секунд')
                    time.sleep(e.seconds)
                except UserBannedInChannelError:
                    actions = "Вам запрещено отправлять сообщения в супергруппу."
                    record_and_interrupt(actions, phone, description_action, event)
                    break  # Прерываем работу и меняем аккаунт
                except (TypeError, UnboundLocalError):
                    continue  # Записываем ошибку в software_database.db и продолжаем работу
                except ChatWriteForbiddenError:
                    actions = "Вам запрещено писать в супергруппу / канал."
                    record_and_interrupt(actions, phone, description_action, event)
                    break  # Прерываем работу и меняем аккаунт
            client.disconnect()  # Разрываем соединение Telegram
        except KeyError:
            sys.exit(1)


def message_entry_window() -> None:
    """Выводим поле ввода для ввода текста сообщения"""
    # Предупреждаем пользователя о вводе ссылок в графическое окно программы
    print("[bold red][+] Введите текст который будем рассылать по чатам, для вставки в графическое окно готового "
          "текста используйте комбинацию клавиш Ctrl + V, обратите внимание что при использование комбинации язык "
          "должен быть переключен на английский")

    root, text = program_window()

    def output_values_from_the_input_field() -> None:
        """Выводим значения с поля ввода (то что ввел пользователь)"""
        message_text = text.get("1.0", 'end-1c')
        closing_the_input_field()
        sending_messages_via_chats_time(message_text)

    def closing_the_input_field() -> None:
        """Закрываем программу"""
        root.destroy()

    # Создаем кнопку по нажатии которой выведется поле ввода. После ввода чатов данные запишутся во временный файл
    but = Button(root, text="Готово", command=output_values_from_the_input_field)
    but.pack()
    root.mainloop()  # Запускаем программу


def output_the_input_field() -> None:
    """Выводим ссылки в поле ввода поле ввода для записи ссылок групп"""
    # Предупреждаем пользователя о вводе ссылок в графическое окно программы
    print("[bold red][+] Введите ссылки чатов в которые будем рассылать сообщения, для вставки в графическое окно "
          "используйте комбинацию клавиш Ctrl + V, обратите внимание что при использование комбинации язык должен "
          "быть переключен на английский")

    root, text = program_window()

    def output_values_from_the_input_field() -> None:
        """Выводим значения с поля ввода (то что ввел пользователь)"""
        res = text.get("1.0", 'end-1c')
        closing_the_input_field()
        with open(f'{folder}/{files}', "w") as res_as:
            res_as.write(res)
        # Записываем данные с файла в базу данных
        with open(f'{folder}/{files}', 'r') as recorded_data:
            name_database = "writing_group_links"
            open_the_db_and_read_the_data(name_database)  # Удаление списка с группами
            write_to_single_column_table(name_database, recorded_data)
        deleting_files_if_available(folder, files)  # Удаляем файл после работы

    def closing_the_input_field() -> None:
        """Закрываем программу"""
        root.destroy()

    # Создаем кнопку по нажатии которой выведется поле ввода. После ввода чатов данные запишутся во временный файл
    but = Button(root, text="Готово", command=output_values_from_the_input_field)
    but.pack()
    root.mainloop()  # Запускаем программу


if __name__ == "__main__":
    output_the_input_field()
    message_entry_window()
