# https://docs.telethon.dev/en/latest/modules/client.html#telethon.client.messages.MessageMethods.sending_messages_via_chats_time(message_text)sage
import sys
import time
from tkinter import *

import schedule  # https://schedule.readthedocs.io/en/stable/index.html
from rich import print
from telethon.errors import *

from system.actions.subscription.subscription import subscribe_to_the_group_and_send_the_link
from system.auxiliary_functions.auxiliary_functions import deleting_files_if_available, \
    we_interrupt_the_code_and_write_the_data_to_the_database
from system.error.telegram_errors import recording_actions_in_the_db
from system.menu.baner import program_version, date_of_program_change
from system.notification.notification import app_notifications
from system.sqlite_working_tools.sqlite_working_tools import open_the_db_and_read_the_data
from system.sqlite_working_tools.sqlite_working_tools import writing_data_to_the_db
from system.telegram_actions.telegram_actions import connect_to_telegram_account_and_output_name

folder, files, name_database_table = "setting_user", "members_group.csv", "writing_group_links"
creating_a_table = """SELECT * from writing_group_links"""
writing_data_to_a_table = """DELETE from writing_group_links where writing_group_links = ?"""


def send_mess() -> None:
    with open("setting_user/message_text.csv", 'r') as chats:
        cursor_members = chats.read()

    sending_messages_via_chats_time(cursor_members)


def sending_messages_via_chats_time(message_text) -> None:
    """Массовая рассылка в чаты"""
    event: str = f"Рассылаем сообщение по чатам Telegram"
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
            records: list = open_the_db_and_read_the_data(name_database_table)
            print(f"[bold red]Всего групп: {len(records)}")
            # Поочередно выводим записанные группы
            for groups in records:
                groups_wr = subscribe_to_the_group_and_send_the_link(client, groups, phone)
                description_action = f"Sending messages to a group: {groups_wr}"
                try:
                    # Рассылаем сообщение по чатам
                    client.send_message(entity=groups_wr, message=message_text)
                    # Работу записываем в лог файл, для удобства слежения, за изменениями
                    actions: str = f"[bold red]Сообщение в группу {groups_wr} написано!"
                    recording_actions_in_the_db(phone, description_action, event, actions)
                except ChannelPrivateError:
                    actions: str = "Указанный канал является приватным, или вам запретили подписываться."
                    recording_actions_in_the_db(phone, description_action, event, actions)
                    writing_data_to_the_db(creating_a_table, writing_data_to_a_table, groups_wr)
                except PeerFloodError:
                    actions: str = "Предупреждение о Flood от Telegram."
                    we_interrupt_the_code_and_write_the_data_to_the_database(actions, phone, description_action, event)
                    break  # Прерываем работу и меняем аккаунт
                except FloodWaitError as e:
                    actions: str = f'Flood! wait for {e.seconds} seconds'
                    recording_actions_in_the_db(phone, description_action, event, actions)
                    print(f'Спим {e.seconds} секунд')
                    time.sleep(e.seconds)
                except UserBannedInChannelError:
                    actions: str = "Вам запрещено отправлять сообщения в супергруппу."
                    we_interrupt_the_code_and_write_the_data_to_the_database(actions, phone, description_action, event)
                    break  # Прерываем работу и меняем аккаунт
                except ChatWriteForbiddenError:
                    actions = "Вам запрещено писать в супергруппу / канал."
                    we_interrupt_the_code_and_write_the_data_to_the_database(actions, phone, description_action, event)
                    break  # Прерываем работу и меняем аккаунт
                except (TypeError, UnboundLocalError):
                    continue  # Записываем ошибку в software_database.db и продолжаем работу
            client.disconnect()  # Разрываем соединение Telegram
        except KeyError:
            sys.exit(1)


def mesage_time() -> None:
    print(" ", "[bold green]Давайте настроим количество сообщений, и время отправки сообщений, работы будет много, "
          "но мы справимся",
          " ", sep="\n")
    print("[bold green]Давайте выберем, сколько сообщений в час, мы будем отправлять", " ",
          "[bold green][1[bold green]] - 1 сообщение в час",
          "[bold green][2[bold green]] - 2 сообщение в час",
          "[bold green][3[bold green]] - 3 сообщение в час",
          "[bold green][4[bold green]] - 4 сообщение в час",
          "[bold green][5[bold green]] - 5 сообщение в час", " ", sep="\n")
    user_input_mes_hour: str = input("[+] Введите от 1 до 5: ")

    # Пишем сообщения 1 раз в час
    if user_input_mes_hour == "1":
        print("[bold red]Пишем сообщения 1 раз в час")
        # Вводим часы и минуты, повторяем до тех пор, пока не будет нужное количество
        user_input_minute_1: str = input("[+] Введите минуты, публикации: ")
        # Отправляем сообщения по времени
        schedule.every().day.at(f"00:{user_input_minute_1}").do(send_mess)

        schedule.every().day.at(f"01:{user_input_minute_1}").do(send_mess)

        schedule.every().day.at(f"02:{user_input_minute_1}").do(send_mess)

        schedule.every().day.at(f"03:{user_input_minute_1}").do(send_mess)

        schedule.every().day.at(f"04:{user_input_minute_1}").do(send_mess)

        schedule.every().day.at(f"05:{user_input_minute_1}").do(send_mess)

        schedule.every().day.at(f"06:{user_input_minute_1}").do(send_mess)

        schedule.every().day.at(f"07:{user_input_minute_1}").do(send_mess)

        schedule.every().day.at(f"08:{user_input_minute_1}").do(send_mess)

        schedule.every().day.at(f"09:{user_input_minute_1}").do(send_mess)

        schedule.every().day.at(f"10:{user_input_minute_1}").do(send_mess)

        schedule.every().day.at(f"11:{user_input_minute_1}").do(send_mess)

        schedule.every().day.at(f"12:{user_input_minute_1}").do(send_mess)

        schedule.every().day.at(f"13:{user_input_minute_1}").do(send_mess)

        schedule.every().day.at(f"14:{user_input_minute_1}").do(send_mess)

        schedule.every().day.at(f"15:{user_input_minute_1}").do(send_mess)

        schedule.every().day.at(f"16:{user_input_minute_1}").do(send_mess)

        schedule.every().day.at(f"17:{user_input_minute_1}").do(send_mess)

        schedule.every().day.at(f"18:{user_input_minute_1}").do(send_mess)

        schedule.every().day.at(f"19:{user_input_minute_1}").do(send_mess)

        schedule.every().day.at(f"20:{user_input_minute_1}").do(send_mess)

        schedule.every().day.at(f"21:{user_input_minute_1}").do(send_mess)

        schedule.every().day.at(f"22:{user_input_minute_1}").do(send_mess)

        schedule.every().day.at(f"23:{user_input_minute_1}").do(send_mess)

    # Пишем сообщения 2 раза в час
    elif user_input_mes_hour == "2":
        print("[bold red]Пишем сообщения 2 раза в час")
        # Вводим часы и минуты, повторяем до тех пор, пока не будет нужное количество
        user_input_minute_1: str = input("[+] Введите минуты, публикации: ")
        user_input_minute_2: str = input("[+] Введите минуты, публикации: ")
        # Отправляем сообщения по времени
        schedule.every().day.at(f"00:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"00:{user_input_minute_2}").do(send_mess)

        schedule.every().day.at(f"01:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"01:{user_input_minute_2}").do(send_mess)

        schedule.every().day.at(f"02:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"02:{user_input_minute_2}").do(send_mess)

        schedule.every().day.at(f"03:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"03:{user_input_minute_2}").do(send_mess)

        schedule.every().day.at(f"04:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"04:{user_input_minute_2}").do(send_mess)

        schedule.every().day.at(f"05:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"05:{user_input_minute_2}").do(send_mess)

        schedule.every().day.at(f"06:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"06:{user_input_minute_2}").do(send_mess)

        schedule.every().day.at(f"07:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"07:{user_input_minute_2}").do(send_mess)

        schedule.every().day.at(f"08:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"08:{user_input_minute_2}").do(send_mess)

        schedule.every().day.at(f"09:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"09:{user_input_minute_2}").do(send_mess)

        schedule.every().day.at(f"10:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"10:{user_input_minute_2}").do(send_mess)

        schedule.every().day.at(f"11:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"11:{user_input_minute_2}").do(send_mess)

        schedule.every().day.at(f"12:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"12:{user_input_minute_2}").do(send_mess)

        schedule.every().day.at(f"13:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"13:{user_input_minute_2}").do(send_mess)

        schedule.every().day.at(f"14:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"14:{user_input_minute_2}").do(send_mess)

        schedule.every().day.at(f"15:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"15:{user_input_minute_2}").do(send_mess)

        schedule.every().day.at(f"16:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"16:{user_input_minute_2}").do(send_mess)

        schedule.every().day.at(f"17:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"17:{user_input_minute_2}").do(send_mess)

        schedule.every().day.at(f"18:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"18:{user_input_minute_2}").do(send_mess)

        schedule.every().day.at(f"19:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"19:{user_input_minute_2}").do(send_mess)

        schedule.every().day.at(f"20:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"20:{user_input_minute_2}").do(send_mess)

        schedule.every().day.at(f"21:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"21:{user_input_minute_2}").do(send_mess)

        schedule.every().day.at(f"22:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"22:{user_input_minute_2}").do(send_mess)

        schedule.every().day.at(f"23:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"23:{user_input_minute_2}").do(send_mess)

    # Пишем сообщения 3 раза в час
    elif user_input_mes_hour == "3":
        print("[bold red]Пишем сообщения 3 раза в час")
        # Вводим часы и минуты, повторяем до тех пор, пока не будет нужное количество
        user_input_minute_1: str = input("[+] Введите минуты, публикации: ")
        user_input_minute_2: str = input("[+] Введите минуты, публикации: ")
        user_input_minute_3: str = input("[+] Введите минуты, публикации: ")
        # Отправляем сообщения по времени
        schedule.every().day.at(f"00:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"00:{user_input_minute_2}").do(send_mess)
        schedule.every().day.at(f"00:{user_input_minute_3}").do(send_mess)

        schedule.every().day.at(f"01:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"01:{user_input_minute_2}").do(send_mess)
        schedule.every().day.at(f"01:{user_input_minute_3}").do(send_mess)

        schedule.every().day.at(f"02:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"02:{user_input_minute_2}").do(send_mess)
        schedule.every().day.at(f"02:{user_input_minute_3}").do(send_mess)

        schedule.every().day.at(f"03:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"03:{user_input_minute_2}").do(send_mess)
        schedule.every().day.at(f"03:{user_input_minute_3}").do(send_mess)

        schedule.every().day.at(f"04:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"04:{user_input_minute_2}").do(send_mess)
        schedule.every().day.at(f"04:{user_input_minute_3}").do(send_mess)

        schedule.every().day.at(f"05:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"05:{user_input_minute_2}").do(send_mess)
        schedule.every().day.at(f"05:{user_input_minute_3}").do(send_mess)

        schedule.every().day.at(f"06:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"06:{user_input_minute_2}").do(send_mess)
        schedule.every().day.at(f"06:{user_input_minute_3}").do(send_mess)

        schedule.every().day.at(f"07:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"07:{user_input_minute_2}").do(send_mess)
        schedule.every().day.at(f"07:{user_input_minute_3}").do(send_mess)

        schedule.every().day.at(f"08:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"08:{user_input_minute_2}").do(send_mess)
        schedule.every().day.at(f"08:{user_input_minute_3}").do(send_mess)

        schedule.every().day.at(f"09:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"09:{user_input_minute_2}").do(send_mess)
        schedule.every().day.at(f"09:{user_input_minute_3}").do(send_mess)

        schedule.every().day.at(f"10:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"10:{user_input_minute_2}").do(send_mess)
        schedule.every().day.at(f"10:{user_input_minute_3}").do(send_mess)

        schedule.every().day.at(f"11:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"11:{user_input_minute_2}").do(send_mess)
        schedule.every().day.at(f"11:{user_input_minute_3}").do(send_mess)

        schedule.every().day.at(f"12:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"12:{user_input_minute_2}").do(send_mess)
        schedule.every().day.at(f"12:{user_input_minute_3}").do(send_mess)

        schedule.every().day.at(f"13:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"13:{user_input_minute_2}").do(send_mess)
        schedule.every().day.at(f"13:{user_input_minute_3}").do(send_mess)

        schedule.every().day.at(f"14:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"14:{user_input_minute_2}").do(send_mess)
        schedule.every().day.at(f"14:{user_input_minute_3}").do(send_mess)

        schedule.every().day.at(f"15:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"15:{user_input_minute_2}").do(send_mess)
        schedule.every().day.at(f"15:{user_input_minute_3}").do(send_mess)

        schedule.every().day.at(f"16:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"16:{user_input_minute_2}").do(send_mess)
        schedule.every().day.at(f"16:{user_input_minute_3}").do(send_mess)

        schedule.every().day.at(f"17:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"17:{user_input_minute_2}").do(send_mess)
        schedule.every().day.at(f"17:{user_input_minute_3}").do(send_mess)

        schedule.every().day.at(f"18:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"18:{user_input_minute_2}").do(send_mess)
        schedule.every().day.at(f"18:{user_input_minute_3}").do(send_mess)

        schedule.every().day.at(f"19:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"19:{user_input_minute_2}").do(send_mess)
        schedule.every().day.at(f"19:{user_input_minute_3}").do(send_mess)

        schedule.every().day.at(f"20:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"20:{user_input_minute_2}").do(send_mess)
        schedule.every().day.at(f"20:{user_input_minute_3}").do(send_mess)

        schedule.every().day.at(f"21:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"21:{user_input_minute_2}").do(send_mess)
        schedule.every().day.at(f"21:{user_input_minute_3}").do(send_mess)

        schedule.every().day.at(f"22:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"22:{user_input_minute_2}").do(send_mess)
        schedule.every().day.at(f"22:{user_input_minute_3}").do(send_mess)

        schedule.every().day.at(f"23:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"23:{user_input_minute_2}").do(send_mess)
        schedule.every().day.at(f"23:{user_input_minute_3}").do(send_mess)

    # Пишем сообщения 4 раза в час
    elif user_input_mes_hour == "4":
        print("[bold red]Пишем сообщения 4 раза в час")
        # Вводим часы и минуты, повторяем до тех пор, пока не будет нужное количество
        user_input_minute_1: str = input("[+] Введите минуты, публикации: ")
        user_input_minute_2: str = input("[+] Введите минуты, публикации: ")
        user_input_minute_3: str = input("[+] Введите минуты, публикации: ")
        user_input_minute_4: str = input("[+] Введите минуты, публикации: ")
        # Отправляем сообщения по времени
        schedule.every().day.at(f"00:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"00:{user_input_minute_2}").do(send_mess)
        schedule.every().day.at(f"00:{user_input_minute_3}").do(send_mess)
        schedule.every().day.at(f"00:{user_input_minute_4}").do(send_mess)

        schedule.every().day.at(f"01:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"01:{user_input_minute_2}").do(send_mess)
        schedule.every().day.at(f"01:{user_input_minute_3}").do(send_mess)
        schedule.every().day.at(f"01:{user_input_minute_4}").do(send_mess)

        schedule.every().day.at(f"02:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"02:{user_input_minute_2}").do(send_mess)
        schedule.every().day.at(f"02:{user_input_minute_3}").do(send_mess)
        schedule.every().day.at(f"02:{user_input_minute_4}").do(send_mess)

        schedule.every().day.at(f"03:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"03:{user_input_minute_2}").do(send_mess)
        schedule.every().day.at(f"03:{user_input_minute_3}").do(send_mess)
        schedule.every().day.at(f"03:{user_input_minute_4}").do(send_mess)

        schedule.every().day.at(f"04:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"04:{user_input_minute_2}").do(send_mess)
        schedule.every().day.at(f"04:{user_input_minute_3}").do(send_mess)
        schedule.every().day.at(f"04:{user_input_minute_4}").do(send_mess)

        schedule.every().day.at(f"05:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"05:{user_input_minute_2}").do(send_mess)
        schedule.every().day.at(f"05:{user_input_minute_3}").do(send_mess)
        schedule.every().day.at(f"05:{user_input_minute_4}").do(send_mess)

        schedule.every().day.at(f"06:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"06:{user_input_minute_2}").do(send_mess)
        schedule.every().day.at(f"06:{user_input_minute_3}").do(send_mess)
        schedule.every().day.at(f"06:{user_input_minute_4}").do(send_mess)

        schedule.every().day.at(f"07:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"07:{user_input_minute_2}").do(send_mess)
        schedule.every().day.at(f"07:{user_input_minute_3}").do(send_mess)
        schedule.every().day.at(f"07:{user_input_minute_4}").do(send_mess)

        schedule.every().day.at(f"08:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"08:{user_input_minute_2}").do(send_mess)
        schedule.every().day.at(f"08:{user_input_minute_3}").do(send_mess)
        schedule.every().day.at(f"08:{user_input_minute_4}").do(send_mess)

        schedule.every().day.at(f"09:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"09:{user_input_minute_2}").do(send_mess)
        schedule.every().day.at(f"09:{user_input_minute_3}").do(send_mess)
        schedule.every().day.at(f"09:{user_input_minute_4}").do(send_mess)

        schedule.every().day.at(f"10:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"10:{user_input_minute_2}").do(send_mess)
        schedule.every().day.at(f"10:{user_input_minute_3}").do(send_mess)
        schedule.every().day.at(f"10:{user_input_minute_4}").do(send_mess)

        schedule.every().day.at(f"11:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"11:{user_input_minute_2}").do(send_mess)
        schedule.every().day.at(f"11:{user_input_minute_3}").do(send_mess)
        schedule.every().day.at(f"11:{user_input_minute_4}").do(send_mess)

        schedule.every().day.at(f"12:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"12:{user_input_minute_2}").do(send_mess)
        schedule.every().day.at(f"12:{user_input_minute_3}").do(send_mess)
        schedule.every().day.at(f"12:{user_input_minute_4}").do(send_mess)

        schedule.every().day.at(f"13:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"13:{user_input_minute_2}").do(send_mess)
        schedule.every().day.at(f"13:{user_input_minute_3}").do(send_mess)
        schedule.every().day.at(f"13:{user_input_minute_4}").do(send_mess)

        schedule.every().day.at(f"14:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"14:{user_input_minute_2}").do(send_mess)
        schedule.every().day.at(f"14:{user_input_minute_3}").do(send_mess)
        schedule.every().day.at(f"14:{user_input_minute_4}").do(send_mess)

        schedule.every().day.at(f"15:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"15:{user_input_minute_2}").do(send_mess)
        schedule.every().day.at(f"15:{user_input_minute_3}").do(send_mess)
        schedule.every().day.at(f"15:{user_input_minute_4}").do(send_mess)

        schedule.every().day.at(f"16:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"16:{user_input_minute_2}").do(send_mess)
        schedule.every().day.at(f"16:{user_input_minute_3}").do(send_mess)
        schedule.every().day.at(f"16:{user_input_minute_4}").do(send_mess)

        schedule.every().day.at(f"17:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"17:{user_input_minute_2}").do(send_mess)
        schedule.every().day.at(f"17:{user_input_minute_3}").do(send_mess)
        schedule.every().day.at(f"17:{user_input_minute_4}").do(send_mess)

        schedule.every().day.at(f"18:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"18:{user_input_minute_2}").do(send_mess)
        schedule.every().day.at(f"18:{user_input_minute_3}").do(send_mess)
        schedule.every().day.at(f"18:{user_input_minute_4}").do(send_mess)

        schedule.every().day.at(f"19:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"19:{user_input_minute_2}").do(send_mess)
        schedule.every().day.at(f"19:{user_input_minute_3}").do(send_mess)
        schedule.every().day.at(f"19:{user_input_minute_4}").do(send_mess)

        schedule.every().day.at(f"20:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"20:{user_input_minute_2}").do(send_mess)
        schedule.every().day.at(f"20:{user_input_minute_3}").do(send_mess)
        schedule.every().day.at(f"20:{user_input_minute_4}").do(send_mess)

        schedule.every().day.at(f"21:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"21:{user_input_minute_2}").do(send_mess)
        schedule.every().day.at(f"21:{user_input_minute_3}").do(send_mess)
        schedule.every().day.at(f"21:{user_input_minute_4}").do(send_mess)

        schedule.every().day.at(f"22:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"22:{user_input_minute_2}").do(send_mess)
        schedule.every().day.at(f"22:{user_input_minute_3}").do(send_mess)
        schedule.every().day.at(f"22:{user_input_minute_4}").do(send_mess)

        schedule.every().day.at(f"23:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"23:{user_input_minute_2}").do(send_mess)
        schedule.every().day.at(f"23:{user_input_minute_3}").do(send_mess)
        schedule.every().day.at(f"23:{user_input_minute_4}").do(send_mess)

    # Пишем сообщения 5 раз в час
    elif user_input_mes_hour == "5":
        print("[bold red]Пишем сообщения 5 раза в час")
        # Вводим часы и минуты, повторяем до тех пор, пока не будет нужное количество
        user_input_minute_1: str = input("[+] Введите минуты, публикации: ")
        user_input_minute_2: str = input("[+] Введите минуты, публикации: ")
        user_input_minute_3: str = input("[+] Введите минуты, публикации: ")
        user_input_minute_4: str = input("[+] Введите минуты, публикации: ")
        user_input_minute_5: str = input("[+] Введите минуты, публикации: ")
        # Отправляем сообщения по времени

        schedule.every().day.at(f"00:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"00:{user_input_minute_2}").do(send_mess)
        schedule.every().day.at(f"00:{user_input_minute_3}").do(send_mess)
        schedule.every().day.at(f"00:{user_input_minute_4}").do(send_mess)
        schedule.every().day.at(f"00:{user_input_minute_5}").do(send_mess)

        schedule.every().day.at(f"01:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"01:{user_input_minute_2}").do(send_mess)
        schedule.every().day.at(f"01:{user_input_minute_3}").do(send_mess)
        schedule.every().day.at(f"01:{user_input_minute_4}").do(send_mess)
        schedule.every().day.at(f"01:{user_input_minute_5}").do(send_mess)

        schedule.every().day.at(f"02:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"02:{user_input_minute_2}").do(send_mess)
        schedule.every().day.at(f"02:{user_input_minute_3}").do(send_mess)
        schedule.every().day.at(f"02:{user_input_minute_4}").do(send_mess)
        schedule.every().day.at(f"02:{user_input_minute_5}").do(send_mess)

        schedule.every().day.at(f"03:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"03:{user_input_minute_2}").do(send_mess)
        schedule.every().day.at(f"03:{user_input_minute_3}").do(send_mess)
        schedule.every().day.at(f"03:{user_input_minute_4}").do(send_mess)
        schedule.every().day.at(f"03:{user_input_minute_5}").do(send_mess)

        schedule.every().day.at(f"04:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"04:{user_input_minute_2}").do(send_mess)
        schedule.every().day.at(f"04:{user_input_minute_3}").do(send_mess)
        schedule.every().day.at(f"04:{user_input_minute_4}").do(send_mess)
        schedule.every().day.at(f"04:{user_input_minute_5}").do(send_mess)

        schedule.every().day.at(f"05:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"05:{user_input_minute_2}").do(send_mess)
        schedule.every().day.at(f"05:{user_input_minute_3}").do(send_mess)
        schedule.every().day.at(f"05:{user_input_minute_4}").do(send_mess)
        schedule.every().day.at(f"05:{user_input_minute_5}").do(send_mess)

        schedule.every().day.at(f"06:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"06:{user_input_minute_2}").do(send_mess)
        schedule.every().day.at(f"06:{user_input_minute_3}").do(send_mess)
        schedule.every().day.at(f"06:{user_input_minute_4}").do(send_mess)
        schedule.every().day.at(f"06:{user_input_minute_5}").do(send_mess)

        schedule.every().day.at(f"07:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"07:{user_input_minute_2}").do(send_mess)
        schedule.every().day.at(f"07:{user_input_minute_3}").do(send_mess)
        schedule.every().day.at(f"07:{user_input_minute_4}").do(send_mess)
        schedule.every().day.at(f"07:{user_input_minute_5}").do(send_mess)

        schedule.every().day.at(f"08:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"08:{user_input_minute_2}").do(send_mess)
        schedule.every().day.at(f"08:{user_input_minute_3}").do(send_mess)
        schedule.every().day.at(f"08:{user_input_minute_4}").do(send_mess)
        schedule.every().day.at(f"08:{user_input_minute_5}").do(send_mess)

        schedule.every().day.at(f"09:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"09:{user_input_minute_2}").do(send_mess)
        schedule.every().day.at(f"09:{user_input_minute_3}").do(send_mess)
        schedule.every().day.at(f"09:{user_input_minute_4}").do(send_mess)
        schedule.every().day.at(f"09:{user_input_minute_5}").do(send_mess)

        schedule.every().day.at(f"10:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"10:{user_input_minute_2}").do(send_mess)
        schedule.every().day.at(f"10:{user_input_minute_3}").do(send_mess)
        schedule.every().day.at(f"10:{user_input_minute_4}").do(send_mess)
        schedule.every().day.at(f"10:{user_input_minute_5}").do(send_mess)

        schedule.every().day.at(f"11:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"11:{user_input_minute_2}").do(send_mess)
        schedule.every().day.at(f"11:{user_input_minute_3}").do(send_mess)
        schedule.every().day.at(f"11:{user_input_minute_4}").do(send_mess)
        schedule.every().day.at(f"11:{user_input_minute_5}").do(send_mess)

        schedule.every().day.at(f"12:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"12:{user_input_minute_2}").do(send_mess)
        schedule.every().day.at(f"12:{user_input_minute_3}").do(send_mess)
        schedule.every().day.at(f"12:{user_input_minute_4}").do(send_mess)
        schedule.every().day.at(f"12:{user_input_minute_5}").do(send_mess)

        schedule.every().day.at(f"13:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"13:{user_input_minute_2}").do(send_mess)
        schedule.every().day.at(f"13:{user_input_minute_3}").do(send_mess)
        schedule.every().day.at(f"13:{user_input_minute_4}").do(send_mess)
        schedule.every().day.at(f"13:{user_input_minute_5}").do(send_mess)

        schedule.every().day.at(f"14:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"14:{user_input_minute_2}").do(send_mess)
        schedule.every().day.at(f"14:{user_input_minute_3}").do(send_mess)
        schedule.every().day.at(f"14:{user_input_minute_4}").do(send_mess)
        schedule.every().day.at(f"14:{user_input_minute_5}").do(send_mess)

        schedule.every().day.at(f"15:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"15:{user_input_minute_2}").do(send_mess)
        schedule.every().day.at(f"15:{user_input_minute_3}").do(send_mess)
        schedule.every().day.at(f"15:{user_input_minute_4}").do(send_mess)
        schedule.every().day.at(f"15:{user_input_minute_5}").do(send_mess)

        schedule.every().day.at(f"16:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"16:{user_input_minute_2}").do(send_mess)
        schedule.every().day.at(f"16:{user_input_minute_3}").do(send_mess)
        schedule.every().day.at(f"16:{user_input_minute_4}").do(send_mess)
        schedule.every().day.at(f"16:{user_input_minute_5}").do(send_mess)

        schedule.every().day.at(f"17:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"17:{user_input_minute_2}").do(send_mess)
        schedule.every().day.at(f"17:{user_input_minute_3}").do(send_mess)
        schedule.every().day.at(f"17:{user_input_minute_4}").do(send_mess)
        schedule.every().day.at(f"17:{user_input_minute_5}").do(send_mess)

        schedule.every().day.at(f"18:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"18:{user_input_minute_2}").do(send_mess)
        schedule.every().day.at(f"18:{user_input_minute_3}").do(send_mess)
        schedule.every().day.at(f"18:{user_input_minute_4}").do(send_mess)
        schedule.every().day.at(f"18:{user_input_minute_5}").do(send_mess)

        schedule.every().day.at(f"19:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"19:{user_input_minute_2}").do(send_mess)
        schedule.every().day.at(f"19:{user_input_minute_3}").do(send_mess)
        schedule.every().day.at(f"19:{user_input_minute_4}").do(send_mess)
        schedule.every().day.at(f"19:{user_input_minute_5}").do(send_mess)

        schedule.every().day.at(f"20:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"20:{user_input_minute_2}").do(send_mess)
        schedule.every().day.at(f"20:{user_input_minute_3}").do(send_mess)
        schedule.every().day.at(f"20:{user_input_minute_4}").do(send_mess)
        schedule.every().day.at(f"20:{user_input_minute_5}").do(send_mess)

        schedule.every().day.at(f"21:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"21:{user_input_minute_2}").do(send_mess)
        schedule.every().day.at(f"21:{user_input_minute_3}").do(send_mess)
        schedule.every().day.at(f"21:{user_input_minute_4}").do(send_mess)
        schedule.every().day.at(f"21:{user_input_minute_5}").do(send_mess)

        schedule.every().day.at(f"22:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"22:{user_input_minute_2}").do(send_mess)
        schedule.every().day.at(f"22:{user_input_minute_3}").do(send_mess)
        schedule.every().day.at(f"22:{user_input_minute_4}").do(send_mess)
        schedule.every().day.at(f"22:{user_input_minute_5}").do(send_mess)

        schedule.every().day.at(f"23:{user_input_minute_1}").do(send_mess)
        schedule.every().day.at(f"23:{user_input_minute_2}").do(send_mess)
        schedule.every().day.at(f"23:{user_input_minute_3}").do(send_mess)
        schedule.every().day.at(f"23:{user_input_minute_4}").do(send_mess)
        schedule.every().day.at(f"23:{user_input_minute_5}").do(send_mess)

    else:
        print("Ошибка выбора!")

    while True:
        schedule.run_pending()
        time.sleep(1)


def message_entry_window_time() -> None:
    """Выводим поле ввода для ввода текста сообщения"""
    # Предупреждаем пользователя о вводе ссылок в графическое окно программы
    print("[bold red][+] Введите текст который будем рассылать по чатам, для вставки в графическое окно готового "
          "текста используйте комбинацию клавиш Ctrl + V, обратите внимание что при использование комбинации язык "
          "должен быть переключен на английский")

    # Создаем программу
    root = Tk()
    root.title(f"Telegram_BOT_SMM: {program_version} от {date_of_program_change}")
    # Создаем окно ввода текста, width=50, height=25 выбираем размер программы
    text = Text(width=50, height=25)
    # Создаем поле ввода
    text.pack()

    def output_values_from_the_input_field() -> None:
        """Выводим значения с поля ввода (то что ввел пользователь)"""
        message_text = text.get("1.0", 'end-1c')
        closing_the_input_field()

        folder, file = "setting_user", "message_text.csv"

        deleting_files_if_available(folder, file)

        with open(f'{folder}/{file}', "w") as res_as:
            res_as.write(message_text)

    def closing_the_input_field() -> None:
        """Закрываем программу"""
        root.destroy()

    # Создаем кнопку по нажатии которой выведется поле ввода. После ввода чатов данные запишутся во временный файл
    but = Button(root, text="Готово", command=output_values_from_the_input_field)
    but.pack()
    # Запускаем программу
    root.mainloop()


if __name__ == "__main__":
    message_entry_window_time()
