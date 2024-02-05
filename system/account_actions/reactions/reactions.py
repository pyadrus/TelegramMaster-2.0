import re
import sys
import time

from loguru import logger
from rich import print
from telethon import types
from telethon.tl.functions.messages import SendReactionRequest, GetMessagesViewsRequest

from system.actions.subscription.subscription import subscribe_to_group_or_channel
from system.auxiliary_functions.global_variables import console
from system.notification.notification import app_notifications
from system.sqlite_working_tools.sqlite_working_tools import DatabaseHandler
from system.telegram_actions.telegram_actions import connect_to_telegram_account_and_output_name


def users_choice_of_reaction() -> None:
    """Выбираем реакцию для выставления в чате / канале"""
    print("[medium_purple3][!] Давайте выберем какую реакцию будем ставить\n",
          "[magenta][0] Поднятый большой палец 👍\n",
          "[magenta][1] Опущенный большой палец 👎\n",
          "[magenta][2] Красное сердце ❤\n",
          "[magenta][3] Огонь 🔥\n",
          "[magenta][4] Хлопушка 🎉\n",
          "[magenta][5] Лицо, кричащее от страха 😱\n",
          "[magenta][6] Широко улыбающееся лицо 😁\n",
          "[magenta][7] Лицо с открытым ртом и в холодном поту 😢\n",
          "[magenta][8] Фекалии 💩\n",
          "[magenta][9] Аплодирующие руки 👏\n"
          "[magenta][10] Злость 😡\n"
          "[magenta][11] Женщина разводит руками 🤷‍♀️\n"
          "[magenta][12] Человек разводит руками 🤷\n"
          "[magenta][13] Мужчина разводит руками 🤷‍♂️\n"
          "[magenta][14] Космический монстр 👾️\n"
          "[magenta][15] Лицо в темных очках 😎\n"
          "[magenta][16] Ничего не скажу 🙊\n"
          "[magenta][17] Таблетка 💊\n"
          "[magenta][18] Воздушный поцелуй 😘\n"
          "[magenta][19] Единорог 🦄\n"
          "[magenta][20] Сердце со стрелой 💘\n"
          "[magenta][21] Значок круто 🆒\n"
          "[magenta][22] Каменное лицо 🗿\n"
          "[magenta][23] Глупое лицо 🤪\n"
          "[magenta][24] Маникюр 💅\n"
          "[magenta][25] Снеговик ☃️\n"
          "[magenta][26] Елочка 🎄\n"
          "[magenta][27] Дед мороз 🎅\n"
          "[magenta][28] Объятия 🤗\n"
          "[magenta][29] Непечатные выражения 🤬\n"
          "[magenta][30] Тошнота 🤮\n"
          "[magenta][31] Клоун 🤡\n"
          "[magenta][32] Одурманенное лицо 🥴\n"
          "[magenta][33] Влюбленный глаза 😍\n"
          "[magenta][34] Сто балов 💯\n"
          "[magenta][35] Хот-дог 🌭\n"
          "[magenta][36] Высокое напряжение ⚡️\n"
          "[magenta][37] Банан 🍌\n"
          "[magenta][38] Средний палец 🖕\n"
          "[magenta][39] Поцелуй 💋\n"
          "[magenta][40] Глаза 👀\n"
          "[magenta][41] Рукопожатие 🤝\n"
          "[magenta][42] Шампанское 🍾\n"
          "[magenta][43] Кубок 🏆\n"
          "[magenta][44] Зевота 🥱\n"
          "[magenta][45] Голубь мира 🕊\n"
          "[magenta][46] Слезы рекой 😭")

    user_input = console.input("[medium_purple3][+] Введите номер: ")

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
    elif user_input == "11":
        reactions_for_groups_and_messages(reaction_input="🤷‍♀️")  # Женщина разводит руками
    elif user_input == "12":
        reactions_for_groups_and_messages(reaction_input="🤷")  # Человек разводит руками
    elif user_input == "13":
        reactions_for_groups_and_messages(reaction_input="🤷‍♂️")  # Мужчина разводит руками
    elif user_input == "14":
        reactions_for_groups_and_messages(reaction_input="👾️")  # Космический монстр
    elif user_input == "15":
        reactions_for_groups_and_messages(reaction_input="😎")  # Лицо в темных очках
    elif user_input == "16":
        reactions_for_groups_and_messages(reaction_input="🙊")  # Ничего не скажу
    elif user_input == "17":
        reactions_for_groups_and_messages(reaction_input="💊")  # Таблетка
    elif user_input == "18":
        reactions_for_groups_and_messages(reaction_input="😘")  # Воздушный поцелуй
    elif user_input == "19":
        reactions_for_groups_and_messages(reaction_input="🦄")  # Единорог
    elif user_input == "20":
        reactions_for_groups_and_messages(reaction_input="💘")  # Сердце со стрелой
    elif user_input == "21":
        reactions_for_groups_and_messages(reaction_input="🆒")  # Значок круто
    elif user_input == "22":
        reactions_for_groups_and_messages(reaction_input="🗿")  # Каменное лицо
    elif user_input == "23":
        reactions_for_groups_and_messages(reaction_input="🤪")  # Глупое лицо
    elif user_input == "24":
        reactions_for_groups_and_messages(reaction_input="💅")  # Маникюр
    elif user_input == "25":
        reactions_for_groups_and_messages(reaction_input="☃")  # Снеговик
    elif user_input == "26":
        reactions_for_groups_and_messages(reaction_input="🎄")  # Елочка
    elif user_input == "27":
        reactions_for_groups_and_messages(reaction_input="🎅")  # Дед мороз
    elif user_input == "28":
        reactions_for_groups_and_messages(reaction_input="🤗")  # Объятия
    elif user_input == "29":
        reactions_for_groups_and_messages(reaction_input="🤬")  # Непечатные выражения
    elif user_input == "30":
        reactions_for_groups_and_messages(reaction_input="🤮")  # Тошнота
    elif user_input == "31":
        reactions_for_groups_and_messages(reaction_input="🤡")  # Клоун
    elif user_input == "32":
        reactions_for_groups_and_messages(reaction_input="🥴")  # Одурманенное лицо
    elif user_input == "33":
        reactions_for_groups_and_messages(reaction_input="😍")  # Влюбленный глаза
    elif user_input == "34":
        reactions_for_groups_and_messages(reaction_input="💯")  # Сто балов
    elif user_input == "35":
        reactions_for_groups_and_messages(reaction_input="🌭")  # Хот-дог
    elif user_input == "36":
        reactions_for_groups_and_messages(reaction_input="⚡️")  # Высокое напряжение
    elif user_input == "37":
        reactions_for_groups_and_messages(reaction_input="🍌")  # Банан
    elif user_input == "38":
        reactions_for_groups_and_messages(reaction_input="🖕")  # Средний палец
    elif user_input == "39":
        reactions_for_groups_and_messages(reaction_input="💋")  # Поцелуй
    elif user_input == "40":
        reactions_for_groups_and_messages(reaction_input="👀")  # Глаза
    elif user_input == "41":
        reactions_for_groups_and_messages(reaction_input="🤝")  # Рукопожатие
    elif user_input == "42":
        reactions_for_groups_and_messages(reaction_input="🍾")  # Шампанское
    elif user_input == "43":
        reactions_for_groups_and_messages(reaction_input="🏆")  # Кубок
    elif user_input == "44":
        reactions_for_groups_and_messages(reaction_input="🥱")  # Зевота
    elif user_input == "45":
        reactions_for_groups_and_messages(reaction_input="🕊")  # Голубь мира
    elif user_input == "46":
        reactions_for_groups_and_messages(reaction_input="😭")  # Слезы рекой


def reactions_for_groups_and_messages(reaction_input) -> None:
    """Вводим ссылку на группу и ссылку на сообщение"""
    chat = console.input("[medium_purple3][+] Введите ссылку на группу / канал: ")  # Ссылка на группу или канал
    message = console.input("[medium_purple3][+] Введите ссылку на сообщение или пост: ")  # Ссылка на сообщение
    records: list = choosing_a_number_of_reactions()  # Выбираем лимиты для аккаунтов
    send_reaction_request(records, chat, message, reaction_input)  # Ставим реакцию на пост, сообщение


def choosing_a_number_of_reactions() -> list:
    """Выбираем лимиты для аккаунтов"""
    print("[medium_purple3]Введите количество с которых будут поставлены реакции")
    # Открываем базу данных для работы с аккаунтами user_settings/software_database.db
    db_handler = DatabaseHandler()
    records: list = db_handler.open_and_read_data("config")
    # Количество аккаунтов на данный момент в работе
    print(f"[medium_purple3]Всего accounts: {len(records)}")
    # Открываем базу данных для работы с аккаунтами user_settings/software_database.db
    number_of_accounts = console.input("[medium_purple3][+] Введите количество аккаунтов для выставления реакций: ")
    records: list = db_handler.open_the_db_and_read_the_data_lim(name_database_table="config",
                                                                 number_of_accounts=int(number_of_accounts))
    return records


def send_reaction_request(records, chat, message_url, reaction_input) -> None:
    """Ставим реакции на сообщения"""
    for row in records:
        # Подключение к Telegram и вывод имени аккаунта в консоль / терминал
        client, phone = connect_to_telegram_account_and_output_name(row)
        try:
            subscribe_to_group_or_channel(client, chat, phone)  # Подписываемся на группу
            number = re.search(r'/(\d+)$', message_url).group(1)
            time.sleep(5)
            client(SendReactionRequest(peer=chat, msg_id=int(number),
                                       reaction=[types.ReactionEmoji(emoticon=f'{reaction_input}')]))
            time.sleep(1)
        except KeyError:
            sys.exit(1)
        except Exception as e:
            logger.exception(e)
            print("[medium_purple3][!] Произошла ошибка, для подробного изучения проблемы просмотрите файл log.log")
        finally:
            client.disconnect()

    app_notifications(notification_text=f"Работа с группой {chat} окончена!")


def viewing_posts() -> None:
    """Накрутка просмотров постов"""
    chat = console.input("[medium_purple3][+] Введите ссылку на канал: ")  # Ссылка на группу или канал
    db_handler = DatabaseHandler()
    records: list = db_handler.open_and_read_data("config")
    # Количество аккаунтов на данный момент в работе
    print(f"[medium_purple3]Всего accounts: {len(records)}")
    # Открываем базу данных для работы с аккаунтами user_settings/software_database.db
    number_of_accounts = console.input("[medium_purple3][+] Введите количество аккаунтов для просмотра постов: ")
    records: list = db_handler.open_the_db_and_read_the_data_lim(name_database_table="config",
                                                                 number_of_accounts=int(number_of_accounts))
    for row in records:
        # Подключение к Telegram и вывод имени аккаунта в консоль / терминал
        client, phone = connect_to_telegram_account_and_output_name(row)
        try:
            subscribe_to_group_or_channel(client, chat, phone)  # Подписываемся на группу
            channel = client.get_entity(chat)  # Получение информации о канале
            time.sleep(5)
            posts = client.get_messages(channel, limit=10)  # Получение последних 10 постов из канала
            for post in posts:  # Вывод информации о постах
                post_link = f"{chat}/{post.id}"  # Ссылка на пост
                print("Ссылка на пост:", post_link)
                print(f"Date: {post.date}\nText: {post.text}\n")
                number = re.search(r"/(\d+)$", post_link).group(1)
                time.sleep(5)
                client(GetMessagesViewsRequest(peer=channel, id=[int(number)], increment=True))
        except KeyError:
            sys.exit(1)
        except Exception as e:
            logger.exception(e)
            print("[medium_purple3][!] Произошла ошибка, для подробного изучения проблемы просмотрите файл log.log")
        finally:
            client.disconnect()

    app_notifications(notification_text=f"Работа с каналом {chat} окончена!")


if __name__ == "__main__":
    users_choice_of_reaction()
    viewing_posts()
