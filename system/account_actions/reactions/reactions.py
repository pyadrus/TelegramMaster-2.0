import io
import json
import random
import sys
import time

import flet as ft  # Импортируем библиотеку flet
from loguru import logger  # Импортируем библиотеку loguru для логирования
from rich import print  # Импортируем библиотеку rich для красивого отображения текста в терминале / консолей (цветного)
from telethon import TelegramClient
from telethon import events, types
from telethon.errors import *
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import SendReactionRequest, GetMessagesViewsRequest

from system.account_actions.creating.account_registration import telegram_connects
from system.account_actions.subscription.subscription import subscribe_to_group_or_channel
from system.auxiliary_functions.auxiliary_functions import find_files, read_json_file
from system.auxiliary_functions.global_variables import console
from system.notification.notification import app_notifications
from system.proxy.checking_proxy import reading_proxy_data_from_the_database
from system.telegram_actions.telegram_actions import telegram_connect_and_output_name

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


async def reactions_for_groups_and_messages_test(number, chat, db_handler) -> None:
    """Вводим ссылку на группу и ссылку на сообщение"""
    # Открываем базу данных для работы с аккаунтами user_settings/software_database.db
    records: list = db_handler.open_and_read_data("config")
    # Количество аккаунтов на данный момент в работе
    print(f"[medium_purple3]Всего accounts: {len(records)}")
    number_of_accounts = read_json_file(filename='user_settings/reactions/number_accounts.json')
    logger.info(f'Всего реакций на пост: {number_of_accounts}')
    records: list = db_handler.open_the_db_and_read_the_data_lim(name_database_table="config",
                                                                 number_of_accounts=int(number_of_accounts))
    for row in records:
        # Подключение к Telegram и вывод имени аккаунта в консоль / терминал
        proxy = reading_proxy_data_from_the_database(db_handler)  # Proxy IPV6 - НЕ РАБОТАЮТ
        client = TelegramClient(f"user_settings/accounts/{row[2]}", int(row[0]), row[1],
                                system_version="4.16.30-vxCUSTOM", proxy=proxy)
        await client.connect()  # Подсоединяемся к Telegram
        try:
            await client(JoinChannelRequest(chat))  # Подписываемся на канал / группу
            time.sleep(5)
            reaction_input = read_json_file(filename='user_settings/reactions/reactions.json')

            random_value = random.choice(reaction_input)  # Выбираем случайное значение из списка
            logger.info(random_value)
            await client(SendReactionRequest(peer=chat, msg_id=int(number),
                                             reaction=[types.ReactionEmoji(emoticon=f'{random_value}')]))
            time.sleep(1)
        except KeyError:
            sys.exit(1)
        except Exception as e:
            logger.exception(e)
            print("[medium_purple3][!] Произошла ошибка, для подробного изучения проблемы просмотрите файл log.log")
        finally:
            client.disconnect()

    app_notifications(notification_text=f"Работа с группой {chat} окончена!")


def writing_names_found_files_to_the_db_config_reactions(db_handler) -> None:
    """Запись названий найденных файлов в базу данных"""
    db_handler.cleaning_db(name_database_table="config_reactions")  # Call the method on the instance
    records = find_files(directory_path="user_settings/reactions/accounts", extension='session')
    for entities in records:
        print(f"Записываем данные аккаунта {entities} в базу данных")
        db_handler.write_data_to_db("CREATE TABLE IF NOT EXISTS config_reactions (id, hash, phone)",
                                    "INSERT INTO config_reactions (id, hash, phone) VALUES (?, ?, ?)", entities)


def setting_reactions(db_handler):
    """Выставление реакций на новые посты"""
    writing_names_found_files_to_the_db_config_reactions(db_handler)

    # Открываем базу данных для работы с аккаунтами user_settings/software_database.db
    records_ac: list = db_handler.open_and_read_data("config_reactions")
    # Количество аккаунтов на данный момент в работе
    print(f"[medium_purple3]Всего accounts: {len(records_ac)}")
    records_ac_json = read_json_file(filename='user_settings/reactions/number_accounts.json')
    logger.info(records_ac_json)
    records: list = db_handler.open_the_db_and_read_the_data_lim(name_database_table="config_reactions",
                                                                 number_of_accounts=int(records_ac_json))
    logger.info(records)
    for row in records:
        client = telegram_connects(db_handler, session=f"user_settings/reactions/accounts/{row[2]}")
        chat = read_json_file(filename='user_settings/reactions/link_channel.json')
        logger.info(chat)
        client(JoinChannelRequest(chat))  # Подписываемся на канал / группу

        @client.on(events.NewMessage(chats=chat))
        async def handler(event):
            message = event.message  # Получаем сообщение из события
            message_id = message.id  # Получаем id сообщение
            logger.info(f"Идентификатор сообщения: {message_id}, {message}")
            # Проверяем, является ли сообщение постом и не является ли оно нашим
            if message.post and not message.out:
                await reactions_for_groups_and_messages_test(message_id, chat, db_handler)

    client.run_until_disconnected()  # Запуск клиента


def save_reactions(reactions, path_to_the_file):
    with open(path_to_the_file, 'w', encoding='utf-8') as file:
        json.dump(reactions, file, ensure_ascii=False, indent=4)


def record_the_number_of_accounts(page: ft.Page):
    """Запись количества аккаунтов проставляющих реакции"""
    smaller_time = ft.TextField(label="Введите количество реакций", autofocus=True)

    def btn_click(e) -> None:
        try:
            # page.update()
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
        link_text = smaller_time.value  # Extract the text value from the TextField
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


def users_choice_of_reaction(db_handler) -> None:
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
        reactions_for_groups_and_messages(reaction_input="👍", db_handler=db_handler)  # Поднятый большой палец
    elif user_input == "1":
        reactions_for_groups_and_messages(reaction_input="👎", db_handler=db_handler)  # Опущенный большой палец
    elif user_input == "2":
        reactions_for_groups_and_messages(reaction_input="❤", db_handler=db_handler)  # Красное сердце
    elif user_input == "3":
        reactions_for_groups_and_messages(reaction_input="🔥", db_handler=db_handler)  # Огонь
    elif user_input == "4":
        reactions_for_groups_and_messages(reaction_input="🎉", db_handler=db_handler)  # Хлопушка
    elif user_input == "5":
        reactions_for_groups_and_messages(reaction_input="😱", db_handler=db_handler)  # Лицо, кричащее от страха
    elif user_input == "6":
        reactions_for_groups_and_messages(reaction_input="😁", db_handler=db_handler)  # Широко улыбающееся лицо
    elif user_input == "7":
        reactions_for_groups_and_messages(reaction_input="😢",
                                          db_handler=db_handler)  # Лицо с открытым ртом и в холодном поту
    elif user_input == "8":
        reactions_for_groups_and_messages(reaction_input="💩", db_handler=db_handler)  # Фекалии
    elif user_input == "9":
        reactions_for_groups_and_messages(reaction_input="👏", db_handler=db_handler)  # Аплодирующие руки
    elif user_input == "11":
        reactions_for_groups_and_messages(reaction_input="🤷‍♀️", db_handler=db_handler)  # Женщина разводит руками
    elif user_input == "12":
        reactions_for_groups_and_messages(reaction_input="🤷", db_handler=db_handler)  # Человек разводит руками
    elif user_input == "13":
        reactions_for_groups_and_messages(reaction_input="🤷‍♂️", db_handler=db_handler)  # Мужчина разводит руками
    elif user_input == "14":
        reactions_for_groups_and_messages(reaction_input="👾️", db_handler=db_handler)  # Космический монстр
    elif user_input == "15":
        reactions_for_groups_and_messages(reaction_input="😎", db_handler=db_handler)  # Лицо в темных очках
    elif user_input == "16":
        reactions_for_groups_and_messages(reaction_input="🙊", db_handler=db_handler)  # Ничего не скажу
    elif user_input == "17":
        reactions_for_groups_and_messages(reaction_input="💊", db_handler=db_handler)  # Таблетка
    elif user_input == "18":
        reactions_for_groups_and_messages(reaction_input="😘", db_handler=db_handler)  # Воздушный поцелуй
    elif user_input == "19":
        reactions_for_groups_and_messages(reaction_input="🦄", db_handler=db_handler)  # Единорог
    elif user_input == "20":
        reactions_for_groups_and_messages(reaction_input="💘", db_handler=db_handler)  # Сердце со стрелой
    elif user_input == "21":
        reactions_for_groups_and_messages(reaction_input="🆒", db_handler=db_handler)  # Значок круто
    elif user_input == "22":
        reactions_for_groups_and_messages(reaction_input="🗿", db_handler=db_handler)  # Каменное лицо
    elif user_input == "23":
        reactions_for_groups_and_messages(reaction_input="🤪", db_handler=db_handler)  # Глупое лицо
    elif user_input == "24":
        reactions_for_groups_and_messages(reaction_input="💅", db_handler=db_handler)  # Маникюр
    elif user_input == "25":
        reactions_for_groups_and_messages(reaction_input="☃", db_handler=db_handler)  # Снеговик
    elif user_input == "26":
        reactions_for_groups_and_messages(reaction_input="🎄", db_handler=db_handler)  # Елочка
    elif user_input == "27":
        reactions_for_groups_and_messages(reaction_input="🎅", db_handler=db_handler)  # Дед мороз
    elif user_input == "28":
        reactions_for_groups_and_messages(reaction_input="🤗", db_handler=db_handler)  # Объятия
    elif user_input == "29":
        reactions_for_groups_and_messages(reaction_input="🤬", db_handler=db_handler)  # Непечатные выражения
    elif user_input == "30":
        reactions_for_groups_and_messages(reaction_input="🤮", db_handler=db_handler)  # Тошнота
    elif user_input == "31":
        reactions_for_groups_and_messages(reaction_input="🤡", db_handler=db_handler)  # Клоун
    elif user_input == "32":
        reactions_for_groups_and_messages(reaction_input="🥴", db_handler=db_handler)  # Одурманенное лицо
    elif user_input == "33":
        reactions_for_groups_and_messages(reaction_input="😍", db_handler=db_handler)  # Влюбленный глаза
    elif user_input == "34":
        reactions_for_groups_and_messages(reaction_input="💯", db_handler=db_handler)  # Сто балов
    elif user_input == "35":
        reactions_for_groups_and_messages(reaction_input="🌭", db_handler=db_handler)  # Хот-дог
    elif user_input == "36":
        reactions_for_groups_and_messages(reaction_input="⚡️", db_handler=db_handler)  # Высокое напряжение
    elif user_input == "37":
        reactions_for_groups_and_messages(reaction_input="🍌", db_handler=db_handler)  # Банан
    elif user_input == "38":
        reactions_for_groups_and_messages(reaction_input="🖕", db_handler=db_handler)  # Средний палец
    elif user_input == "39":
        reactions_for_groups_and_messages(reaction_input="💋", db_handler=db_handler)  # Поцелуй
    elif user_input == "40":
        reactions_for_groups_and_messages(reaction_input="👀", db_handler=db_handler)  # Глаза
    elif user_input == "41":
        reactions_for_groups_and_messages(reaction_input="🤝", db_handler=db_handler)  # Рукопожатие
    elif user_input == "42":
        reactions_for_groups_and_messages(reaction_input="🍾", db_handler=db_handler)  # Шампанское
    elif user_input == "43":
        reactions_for_groups_and_messages(reaction_input="🏆", db_handler=db_handler)  # Кубок
    elif user_input == "44":
        reactions_for_groups_and_messages(reaction_input="🥱", db_handler=db_handler)  # Зевота
    elif user_input == "45":
        reactions_for_groups_and_messages(reaction_input="🕊", db_handler=db_handler)  # Голубь мира
    elif user_input == "46":
        reactions_for_groups_and_messages(reaction_input="😭", db_handler=db_handler)  # Слезы рекой


def reactions_for_groups_and_messages(reaction_input, db_handler) -> None:
    """Вводим ссылку на группу и ссылку на сообщение"""
    chat = console.input("[medium_purple3][+] Введите ссылку на группу / канал: ")  # Ссылка на группу или канал
    message = console.input("[medium_purple3][+] Введите ссылку на сообщение или пост: ")  # Ссылка на сообщение
    records: list = choosing_a_number_of_reactions(db_handler)  # Выбираем лимиты для аккаунтов
    send_reaction_request(records, chat, message, reaction_input, db_handler)  # Ставим реакцию на пост, сообщение


def choosing_a_number_of_reactions(db_handler) -> list:
    """Выбираем лимиты для аккаунтов"""
    print("[medium_purple3]Введите количество с которых будут поставлены реакции")
    # Открываем базу данных для работы с аккаунтами user_settings/software_database.db
    records: list = db_handler.open_and_read_data("config")
    # Количество аккаунтов на данный момент в работе
    print(f"[medium_purple3]Всего accounts: {len(records)}")
    # Открываем базу данных для работы с аккаунтами user_settings/software_database.db
    number_of_accounts = console.input("[medium_purple3][+] Введите количество аккаунтов для выставления реакций: ")
    records: list = db_handler.open_the_db_and_read_the_data_lim(name_database_table="config",
                                                                 number_of_accounts=int(number_of_accounts))
    return records


def send_reaction_request(records, chat, message_url, reaction_input, db_handler) -> None:
    """Ставим реакции на сообщения"""
    for row in records:
        # Подключение к Telegram и вывод имени аккаунта в консоль / терминал
        client, phone = telegram_connect_and_output_name(row, db_handler)
        try:
            subscribe_to_group_or_channel(client, chat, phone, db_handler)  # Подписываемся на группу
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


def viewing_posts(db_handler) -> None:
    """Накрутка просмотров постов"""
    chat = console.input("[medium_purple3][+] Введите ссылку на канал: ")  # Ссылка на группу или канал
    records: list = db_handler.open_and_read_data("config")
    # Количество аккаунтов на данный момент в работе
    print(f"[medium_purple3]Всего accounts: {len(records)}")
    # Открываем базу данных для работы с аккаунтами user_settings/software_database.db
    number_of_accounts = console.input("[medium_purple3][+] Введите количество аккаунтов для просмотра постов: ")
    records: list = db_handler.open_the_db_and_read_the_data_lim(name_database_table="config",
                                                                 number_of_accounts=int(number_of_accounts))
    for row in records:
        # Подключение к Telegram и вывод имени аккаунта в консоль / терминал
        client, phone = telegram_connect_and_output_name(row, db_handler)
        try:
            subscribe_to_group_or_channel(client, chat, phone, db_handler)  # Подписываемся на группу
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
    reaction_gui()
