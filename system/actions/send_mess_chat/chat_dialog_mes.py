import time
from tkinter import *

import schedule
from rich import print
from telethon.errors import *

from system.actions.send_mess_chat.chat_dialog import connecting_to_a_telegram_account_and_creating_a_list_of_groups
from system.actions.subscription.subscription import subscribe_to_the_group_and_send_the_link
from system.auxiliary_functions.auxiliary_functions import deleting_files_if_available
from system.auxiliary_functions.auxiliary_functions import record_and_interrupt
from system.error.telegram_errors import record_account_actions
from system.menu.gui_program import program_window
from system.sqlite_working_tools.sqlite_working_tools import write_data_to_db

folder, files = "setting_user", "members_group.csv"
creating_a_table = """SELECT * from writing_group_links"""
writing_data_to_a_table = """DELETE from writing_group_links where writing_group_links = ?"""
event: str = f"Рассылаем сообщение по чатам Telegram"


def send_mess() -> None:
    with open("setting_user/message_text.csv", 'r') as chats:
        cursor_members = chats.read()
    sending_messages_via_chats_time(cursor_members)


def sending_messages_via_chats_time(message_text) -> None:
    """Массовая рассылка в чаты"""
    client, phone, records = connecting_to_a_telegram_account_and_creating_a_list_of_groups()
    for groups in records:
        groups_wr = subscribe_to_the_group_and_send_the_link(client, groups, phone)
        description_action = f"Sending messages to a group: {groups_wr}"
        try:
            # Рассылаем сообщение по чатам
            client.send_message(entity=groups_wr, message=message_text)
            # Работу записываем в лог файл, для удобства слежения, за изменениями
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


def message_time() -> None:
    """
    Пишем сообщения от 1 до 5 раз в ча
    Метод every() модуля schedule, чтобы указать, что задача должна выполняться каждый день
    Метод at() для указания времени выполнения задачи, используя текущий час и значение минут, указанные пользователем
    Метод do() для указания функции, которую нужно вызвать в указанное время
    """
    print("[bold green]Сколько сообщений в час, мы будем отправлять\n",
          "[bold green][1[bold green]] - 1 сообщение в час\n",
          "[bold green][2[bold green]] - 2 сообщение в час\n",
          "[bold green][3[bold green]] - 3 сообщение в час\n",
          "[bold green][4[bold green]] - 4 сообщение в час\n",
          "[bold green][5[bold green]] - 5 сообщение в час\n", )
    user_input_mes_hour: str = input("[+] Введите от 1 до 5: ")
    if user_input_mes_hour == "1":  # Пишем сообщения 1 раз в час
        # Выводим на экран сообщение о том, что сообщения будут публиковаться раз в час
        print("[bold red]Пишем сообщения 1 раз в час")
        # Получаем от пользователя значение минут для публикации сообщений
        user_input_minute_1 = input("[+] Введите минуты, публикации: ")
        # Создаем расписание на каждый час с помощью цикла for
        for hour in range(24):
            schedule.every().day.at(f"{hour:02d}:{user_input_minute_1}").do(send_mess)
    elif user_input_mes_hour == "2":  # Пишем сообщения 2 раза в час
        print("[bold red]Пишем сообщения 2 раза в час")
        user_input_minute_1 = input("[+] Введите минуты, публикации: ")
        user_input_minute_2 = input("[+] Введите минуты, публикации: ")
        # Перебираем часы от 0 до 23
        for hour in range(24):
            schedule.every().day.at(f"{hour:02d}:{user_input_minute_1}").do(send_mess)
            schedule.every().day.at(f"{hour:02d}:{user_input_minute_2}").do(send_mess)
    elif user_input_mes_hour == "3":  # Пишем сообщения 3 раза в час
        print("[bold red]Пишем сообщения 3 раза в час")
        # Вводим часы и минуты, повторяем до тех пор, пока не будет нужное количество
        user_input_minute_1: str = input("[+] Введите минуты, публикации: ")
        user_input_minute_2: str = input("[+] Введите минуты, публикации: ")
        user_input_minute_3: str = input("[+] Введите минуты, публикации: ")
        # Перебираем часы от 0 до 23
        for hour in range(24):
            schedule.every().day.at(f"{hour:02d}:{user_input_minute_1}").do(send_mess)
            schedule.every().day.at(f"{hour:02d}:{user_input_minute_2}").do(send_mess)
            schedule.every().day.at(f"{hour:02d}:{user_input_minute_3}").do(send_mess)
    elif user_input_mes_hour == "4":  # Пишем сообщения 4 раза в час
        print("[bold red]Пишем сообщения 4 раза в час")
        # Вводим часы и минуты, повторяем до тех пор, пока не будет нужное количество
        user_input_minute_1: str = input("[+] Введите минуты, публикации: ")
        user_input_minute_2: str = input("[+] Введите минуты, публикации: ")
        user_input_minute_3: str = input("[+] Введите минуты, публикации: ")
        user_input_minute_4: str = input("[+] Введите минуты, публикации: ")
        # Перебираем часы от 0 до 23
        for hour in range(24):
            schedule.every().day.at(f"{hour:02d}:{user_input_minute_1}").do(send_mess)
            schedule.every().day.at(f"{hour:02d}:{user_input_minute_2}").do(send_mess)
            schedule.every().day.at(f"{hour:02d}:{user_input_minute_3}").do(send_mess)
            schedule.every().day.at(f"{hour:02d}:{user_input_minute_4}").do(send_mess)
    elif user_input_mes_hour == "5":  # Пишем сообщения 5 раз в час
        print("[bold red]Пишем сообщения 5 раза в час")
        # Вводим часы и минуты, повторяем до тех пор, пока не будет нужное количество
        user_input_minute_1: str = input("[+] Введите минуты, публикации: ")
        user_input_minute_2: str = input("[+] Введите минуты, публикации: ")
        user_input_minute_3: str = input("[+] Введите минуты, публикации: ")
        user_input_minute_4: str = input("[+] Введите минуты, публикации: ")
        user_input_minute_5: str = input("[+] Введите минуты, публикации: ")
        # Перебираем часы от 0 до 23
        for hour in range(24):
            schedule.every().day.at(f"{hour:02d}:{user_input_minute_1}").do(send_mess)
            schedule.every().day.at(f"{hour:02d}:{user_input_minute_2}").do(send_mess)
            schedule.every().day.at(f"{hour:02d}:{user_input_minute_3}").do(send_mess)
            schedule.every().day.at(f"{hour:02d}:{user_input_minute_4}").do(send_mess)
            schedule.every().day.at(f"{hour:02d}:{user_input_minute_5}").do(send_mess)
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

    root, text = program_window()

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
    root.mainloop()  # Запускаем программу


if __name__ == "__main__":
    message_entry_window_time()
