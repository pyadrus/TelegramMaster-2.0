import re
import sys
import time

from rich import print
from telethon.tl.functions.messages import SendReactionRequest

from system.actions.subscription.subscription import subscribe_to_group_or_channel
from system.auxiliary_functions.global_variables import console
from system.notification.notification import app_notifications
from system.sqlite_working_tools.sqlite_working_tools import open_the_db_and_read_the_data
from system.sqlite_working_tools.sqlite_working_tools import open_the_db_and_read_the_data_lim
from system.telegram_actions.telegram_actions import connect_to_telegram_account_and_output_name


def users_choice_of_reaction() -> None:
    """Выбираем реакцию для выставления в чате / канале"""
    print("[bold red][!] Давайте выберем какую реакцию будем ставить\n",
          "[bold green][0] Поднятый большой палец 👍\n",
          "[bold green][1] Опущенный большой палец 👎\n",
          "[bold green][2] Красное сердце ❤\n",
          "[bold green][3] Огонь 🔥\n",
          "[bold green][4] Хлопушка 🎉\n",
          "[bold green][5] Лицо, кричащее от страха 😱\n",
          "[bold green][6] Широко улыбающееся лицо 😁\n",
          "[bold green][7] Лицо с открытым ртом и в холодном поту 😢\n",
          "[bold green][8] Фекалии 💩\n",
          "[bold green][9] Аплодирующие руки 👏\n")
    user_input = console.input("[bold red][+] Введите номер: ")

    if user_input == "0":
        reactions_for_groups_and_messages(reaction_input="👍")  # Поднятый большой палец
    elif user_input == "1":
        reactions_for_groups_and_messages(reaction_input="👎")  # Опущенный большой палец
    elif user_input == "2":
        reactions_for_groups_and_messages(reaction_input="❤")  # Красное сердце
    elif user_input == "3":
        reactions_for_groups_and_messages(reaction_input="🔥")  # Огонь
    elif user_input == "4":
        reactions_for_groups_and_messages(reaction_input="🎉")  # Хлопушка
    elif user_input == "5":
        reactions_for_groups_and_messages(reaction_input="😱")  # Лицо, кричащее от страха
    elif user_input == "6":
        reactions_for_groups_and_messages(reaction_input="😁")  # Широко улыбающееся лицо
    elif user_input == "7":
        reactions_for_groups_and_messages(reaction_input="😢")  # Лицо с открытым ртом и в холодном поту
    elif user_input == "8":
        reactions_for_groups_and_messages(reaction_input="💩")  # Фекалии
    elif user_input == "9":
        reactions_for_groups_and_messages(reaction_input="👏")  # Аплодирующие руки


def reactions_for_groups_and_messages(reaction_input) -> None:
    """Вводим ссылку на группу и ссылку на сообщение"""
    chat = console.input("[bold red][+] Введите ссылку на группу / канал: ")  # Ссылка на группу или канал
    message = console.input("[bold red][+] Введите ссылку на сообщение или пост: ")  # Ссылка на сообщение
    # Преобразовываем в номер сообщения, с помощью регулярных выражений
    message_number = re.sub(f'{chat}/', '', f"{message}")
    records: list = choosing_a_number_of_reactions()  # Выбираем лимиты для аккаунтов
    send_reaction_request(records, chat, int(message_number), reaction_input)  # Ставим реакцию на пост, сообщение


def choosing_a_number_of_reactions() -> list:
    """Выбираем лимиты для аккаунтов"""
    print("[bold red]Введите количество с которых будут поставлены реакции")
    # Открываем базу данных для работы с аккаунтами setting_user/software_database.db
    records: list = open_the_db_and_read_the_data(name_database_table="config")
    # Количество аккаунтов на данный момент в работе
    print(f"[bold red]Всего accounts: {len(records)}")
    # Открываем базу данных для работы с аккаунтами setting_user/software_database.db
    number_of_accounts = console.input("[bold red][+] Введите количество аккаунтов для выставления реакций: ")
    records: list = open_the_db_and_read_the_data_lim(name_database_table="config",
                                                      number_of_accounts=int(number_of_accounts))
    return records


def send_reaction_request(records, chat, message, reaction_input):
    """Ставим реакции на сообщения"""
    for row in records:
        # Подключение к Telegram и вывод имя аккаунта в консоль / терминал
        client, phone = connect_to_telegram_account_and_output_name(row)
        try:
            subscribe_to_group_or_channel(client, chat, phone)  # Подписываемся на группу
            client(SendReactionRequest(chat, message, reaction=f'{reaction_input}'))  # Ставим реакцию
            time.sleep(1)
        except KeyError:
            sys.exit(1)
        finally:
            client.disconnect()  # Разрываем соединение Telegram
    app_notifications(notification_text=f"Работа с группой {chat} окончена!") # Выводим уведомление


if __name__ == "__main__":
    users_choice_of_reaction()
