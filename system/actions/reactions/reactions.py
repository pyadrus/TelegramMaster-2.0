import re
import sys
import time

import emoji
from rich import print
from rich.console import Console
from telethon.tl.functions.messages import SendReactionRequest

from system.actions.subscription.subscription import subscribe_to_group_or_channel
from system.notification.notification import app_notifications
from system.sqlite_working_tools.sqlite_working_tools import open_the_db_and_read_the_data
from system.sqlite_working_tools.sqlite_working_tools import open_the_db_and_read_the_data_lim
from system.telegram_actions.telegram_actions import connect_to_telegram_account_and_output_name

console = Console()

# Реакции pip install --upgrade --force-reinstall https://github.com/LonamiWebs/Telethon/archive/v1.24.zip
# https://pypi.org/project/newthon/


"""
Сайты со смайлами
https://unicode-table.com/ru/
https://emojis.wiki/ru/
"""


def users_choice_of_reaction() -> None:
    """Выбираем реакцию для выставления в чате / канале"""
    print("[bold red][!] Давайте выберем какую реакцию будем ставить")
    # Перечисляем варианты реакций
    print(emoji.emojize("[bold green][0] Поднятый большой палец :thumbs_up:"))
    print(emoji.emojize("[bold green][1] Опущенный большой палец :thumbs_down:"))
    print(emoji.emojize("[bold green][2] Красное сердце :red_heart:"))
    print(emoji.emojize("[bold green][3] Огонь :fire:"))
    print(emoji.emojize("[bold green][4] Хлопушка :party_popper:"))
    print(emoji.emojize("[bold green][5] Лицо, кричащее от страха :face_screaming_in_fear:"))
    print(emoji.emojize(
        "[bold green][6] Широко улыбающееся лицо с улыбающимися глазами :beaming_face_with_smiling_eyes:"))
    print(emoji.emojize("[bold green][7] Лицо с открытым ртом и в холодном поту :crying_face:"))
    print(emoji.emojize("[bold green][8] Фекалии :pile_of_poo:"))
    print(emoji.emojize("[bold green][9] Аплодирующие руки :clapping_hands:"))

    user_input = console.input("[bold red][+] Введите номер: ")

    if user_input == "0":
        thumbs_up = "👍"  # Поднятый большой палец
        reactions_for_groups_and_messages(thumbs_up)
    elif user_input == "1":
        thumbs_down = "👎"  # Опущенный большой палец
        reactions_for_groups_and_messages(thumbs_down)
    elif user_input == "2":
        red_heart = "❤"  # Красное сердце
        reactions_for_groups_and_messages(red_heart)
    elif user_input == "3":
        fire = "🔥"  # Огонь
        reactions_for_groups_and_messages(fire)
    elif user_input == "4":
        party_popper = "🎉"  # Хлопушка
        reactions_for_groups_and_messages(party_popper)
    elif user_input == "5":
        face_screaming_in_fear = "😱"  # Лицо, кричащее от страха
        reactions_for_groups_and_messages(face_screaming_in_fear)
    elif user_input == "6":
        beaming_face_with_smiling_eyes = "😁"  # Широко улыбающееся лицо с улыбающимися глазами
        reactions_for_groups_and_messages(beaming_face_with_smiling_eyes)
    elif user_input == "7":
        crying_face = "😢"  # Лицо с открытым ртом и в холодном поту
        reactions_for_groups_and_messages(crying_face)
    elif user_input == "8":
        pile_of_poo = "💩"  # Фекалии
        reactions_for_groups_and_messages(pile_of_poo)
    elif user_input == "9":
        clapping_hands = "👏"  # Аплодирующие руки
        reactions_for_groups_and_messages(clapping_hands)


def reactions_for_groups_and_messages(reaction_input) -> None:
    """Вводим ссылку на группу и ссылку на сообщение"""

    # Ссылка на группу или канал
    chat = console.input("[bold red][+] Введите ссылку на группу / канал: ")
    # Ссылка на сообщение введенное пользователем
    message = console.input("[bold red][+] Введите ссылку на сообщение или пост: ")
    # Ссылка на группу или канал с добавлением символа /
    chat_mod = f"{chat}/"
    # Преобразовываем в номер сообщения, с помощью регулярных выражений
    message_number = re.sub(f'{chat_mod}', '', f"{message}")
    # Выбираем лимиты для аккаунтов
    records: list = choosing_a_number_of_reactions()
    # Ставим реакцию на пост, сообщение
    send_reaction_request(records, chat, int(message_number), reaction_input)


def choosing_a_number_of_reactions() -> list:
    """Выбираем лимиты для аккаунтов"""
    print("[bold red]Введите количество с которых будут поставлены реакции")
    # Открываем базу данных для работы с аккаунтами setting_user/software_database.db
    records: list = open_the_db_and_read_the_data(name_database_table="config")
    # Количество аккаунтов на данный момент в работе
    print(f"[bold red]Всего accounts: {len(records)}")
    # Открываем базу данных для работы с аккаунтами setting_user/software_database.db
    number_of_accounts = console.input("[bold red][+] Введите количество аккаунтов для выставления реакций: ")
    records: list = open_the_db_and_read_the_data_lim(name_database_table="config", number_of_accounts=int(number_of_accounts))
    return records


def send_reaction_request(records, chat, message, reaction_input):
    """Ставим реакции на сообщения"""
    for row in records:
        # Подключение к Telegram и вывод имя аккаунта в консоль / терминал
        client, phone = connect_to_telegram_account_and_output_name(row)
        try:
            # Подписываемся на группу
            subscribe_to_group_or_channel(client, chat, phone)
            # Ставим реакцию
            client(SendReactionRequest(chat, message, reaction=f'{reaction_input}'))
            time.sleep(1)
        except KeyError:
            sys.exit(1)
        finally:
            client.disconnect()  # Разрываем соединение Telegram
    # Выводим уведомление, если операционная система windows 7, то выводим уведомление в консоль
    app_notifications(notification_text=f"Работа с группой {chat} окончена!")


if __name__ == "__main__":
    users_choice_of_reaction()
