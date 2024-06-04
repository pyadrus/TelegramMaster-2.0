import random
import time

import flet as ft
from loguru import logger
from telethon import functions
from telethon import types
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import ChannelParticipantsSearch
from telethon.tl.types import InputPeerEmpty
from telethon.tl.types import UserStatusEmpty
from telethon.tl.types import UserStatusLastMonth
from telethon.tl.types import UserStatusLastWeek
from telethon.tl.types import UserStatusOffline
from telethon.tl.types import UserStatusOnline
from telethon.tl.types import UserStatusRecently

from system.account_actions.subscription.subscription import subscribe_to_group_or_channel
from system.account_actions.subscription.subscription import subscribe_to_the_group_and_send_the_link
from system.auxiliary_functions.global_variables import ConfigReader
from system.sqlite_working_tools.sqlite_working_tools import DatabaseHandler
from system.telegram_actions.telegram_actions import telegram_connect_and_output_name


def parsing_gui(page: ft.Page):
    lv = ft.ListView(expand=10, spacing=1, padding=2, auto_scroll=True)
    page.controls.append(lv)
    page.update()  # Убедитесь, что ListView добавлен на страницу перед запуском цикла

    async def add_items(e):
        # Индикация начала парсинга
        lv.controls.append(ft.Text("Парсинг начался..."))
        page.update()  # Обновите страницу, чтобы сразу показать сообщение

        db_handler = DatabaseHandler()  # Открываем базу с аккаунтами и с выставленными лимитами
        records: list = await db_handler.open_the_db_and_read_the_data_lim(name_database_table="config",
                                                                           number_of_accounts=1)

        lv.controls.append(ft.Text(f"Аккаунтов для парсинга: {len(records)}"))
        page.update()  # Обновите страницу, чтобы сразу показать сообщение

        for row in records:
            await process_telegram_groups(page, lv, row, db_handler)

        # Добавление сообщения о завершении парсинга
        lv.controls.append(ft.Text("Парсинг завершен"))
        page.update()  # Обновление страницы для показа сообщения о завершении

    button = ft.ElevatedButton("Начать парсинг", on_click=add_items)

    page.views.append(
        ft.View(
            "/settings",
            [
                lv,
                ft.Column(),  # Заполнитель для приветствия или другого содержимого (необязательно)
                button,
            ],
        )
    )

    page.update()


async def process_telegram_groups(page, lv, row, db_handler) -> None:
    """
    :param lv: ListView
    :param page: страница
    :param row: строка из таблицы
    :param db_handler: база данных
    """
    # Подключение к Telegram и вывод имя аккаунта в консоль / терминал
    client = await telegram_connect_and_output_name(row, db_handler)
    # Открываем базу с группами для дальнейшего parsing
    records: list = await db_handler.open_and_read_data("writing_group_links")
    for groups in records:  # Поочередно выводим записанные группы
        logger.info(f'[+] Парсинг группы: {groups}')
        lv.controls.append(ft.Text(f"Группа для парсинга: {groups}"))
        page.update()  # Обновите страницу, чтобы сразу показать сообщение
        await subscribe_and_parse_group(page, lv, client, groups, db_handler)
    await db_handler.clean_no_username()  # Чистка списка parsing списка, если нет username
    await db_handler.delete_duplicates(table_name="members",
                                       column_name="id")  # Чистка дублирующих username по столбцу id
    await client.disconnect()  # Разрываем соединение telegram


async def subscribe_and_parse_group(page, lv, client, groups, db_handler) -> None:
    """
    :param lv:  ListView
    :param page:  страница
    :param client: Телеграм клиент
    :param groups: список групп
    :param db_handler: база данных
    """
    groups_wr = await subscribe_to_the_group_and_send_the_link(client, groups)
    lv.controls.append(ft.Text(f"Группа для парсинга: {len(groups_wr)}"))
    page.update()  # Обновите страницу, чтобы сразу показать сообщение
    await group_parsing(page, lv, client, groups_wr, db_handler)  # Parsing групп
    # Удаляем отработанную группу или канал
    await db_handler.delete_row_db(table="writing_group_links", column="writing_group_links", value=groups_wr)


async def group_parsing(page, lv, client, groups_wr, db_handler) -> None:
    """
    Эта функция выполняет парсинг групп, на которые пользователь подписался. Аргумент phone используется декоратором
    @handle_exceptions для отлавливания ошибок и записи их в базу данных user_settings/software_database.db.
    """
    all_participants: list = await parsing_of_users_from_the_selected_group(page, lv, client, groups_wr)
    logger.info(f"[+] Спарсили данные с группы {groups_wr}")

    lv.controls.append(ft.Text(f"[+] Спарсили данные с группы {groups_wr}"))
    page.update()  # Обновите страницу, чтобы сразу показать сообщение

    # Записываем parsing данные в файл user_settings/software_database.db
    entities = all_participants_user(page, lv, all_participants)
    await db_handler.write_parsed_chat_participants_to_db(entities)


async def parsing_of_users_from_the_selected_group(page, lv, client, target_group) -> list:
    """Собираем данные user и записываем в файл members.db (создание нового файла members.db)"""
    logger.info("[+] Ищем участников... Сохраняем в файл software_database.db...")
    lv.controls.append(ft.Text("[+] Ищем участников... Сохраняем в файл software_database.db..."))
    page.update()  # Обновите страницу, чтобы сразу показать сообщение
    all_participants: list = []
    while_condition = True
    my_filter = ChannelParticipantsSearch("")
    offset = 0
    while while_condition:
        try:
            participants = await client(GetParticipantsRequest(channel=target_group, offset=offset, filter=my_filter, limit=200, hash=0))

            lv.controls.append(ft.Text(participants))
            page.update()  # Обновите страницу, чтобы сразу показать сообщение

            all_participants.extend(participants.users)
            offset += len(participants.users)
            if len(participants.users) < 1:
                while_condition = False
        except TypeError:
            logger.info(f'Ошибка parsing: не верное имя или cсылка {target_group} не является группой / каналом: {target_group}')
            time.sleep(2)
            break
    return all_participants


def all_participants_user(page, lv, all_participants) -> list:
    """Формируем список user_settings/software_database.db"""
    entities = []  # Создаем словарь
    for user in all_participants:

        lv.controls.append(ft.Text(f"{user}"))
        page.update()  # Обновите страницу, чтобы сразу показать сообщение

        getting_user_data(user, entities)
    return entities  # Возвращаем словарь пользователей


def getting_user_data(user, entities) -> None:
    """Получаем данные пользователя"""
    username = user.username if user.username else "NONE"
    user_phone = user.phone if user.phone else "Номер телефона скрыт"
    first_name = user.first_name if user.first_name else ""
    last_name = user.last_name if user.last_name else ""
    photos_id = ("Пользователь с фото" if isinstance(user.photo, types.UserProfilePhoto) else "Пользователь без фото")
    online_at = "Был(а) недавно"
    # Статусы пользователя https://core.telegram.org/type/UserStatus
    if isinstance(user.status, (
            UserStatusRecently, UserStatusOffline, UserStatusLastWeek, UserStatusLastMonth, UserStatusOnline,
            UserStatusEmpty)):
        if isinstance(user.status, UserStatusOffline):
            online_at = user.status.was_online
        if isinstance(user.status, UserStatusRecently):
            online_at = "Был(а) недавно"
        if isinstance(user.status, UserStatusLastWeek):
            online_at = "Был(а) на этой неделе"
        if isinstance(user.status, UserStatusLastMonth):
            online_at = "Был(а) в этом месяце"
        if isinstance(user.status, UserStatusOnline):
            online_at = user.status.expires
        if isinstance(user.status, UserStatusEmpty):
            online_at = "статус пользователя еще не определен"
    user_premium = "Пользователь с premium" if user.premium else ""

    entities.append(
        [username, user.id, user.access_hash, first_name, last_name, user_phone, online_at, photos_id, user_premium])


def getting_active_user_data(user):
    """Получаем данные пользователя"""
    username = user.username if user.username else "NONE"
    user_phone = user.phone if user.phone else "Номер телефона скрыт"
    first_name = user.first_name if user.first_name else ""
    last_name = user.last_name if user.last_name else ""
    photos_id = ("Пользователь с фото" if isinstance(user.photo, types.UserProfilePhoto) else "Пользователь без фото")
    online_at = "Был(а) недавно"
    # Статусы пользователя https://core.telegram.org/type/UserStatus
    if isinstance(user.status, (
            UserStatusRecently, UserStatusOffline, UserStatusLastWeek, UserStatusLastMonth, UserStatusOnline,
            UserStatusEmpty)):
        if isinstance(user.status, UserStatusOffline):
            online_at = user.status.was_online
        if isinstance(user.status, UserStatusRecently):
            online_at = "Был(а) недавно"
        if isinstance(user.status, UserStatusLastWeek):
            online_at = "Был(а) на этой неделе"
        if isinstance(user.status, UserStatusLastMonth):
            online_at = "Был(а) в этом месяце"
        if isinstance(user.status, UserStatusOnline):
            online_at = user.status.expires
        if isinstance(user.status, UserStatusEmpty):
            online_at = "статус пользователя еще не определен"
    user_premium = "Пользователь с premium" if user.premium else ""

    entity = (username, user.id, user.access_hash,
              first_name, last_name, user_phone,
              online_at, photos_id, user_premium)

    return entity


async def choosing_a_group_from_the_subscribed_ones_for_parsing(page, lv, db_handler) -> None:
    """Выбираем группу из подписанных для parsing"""
    records: list = db_handler.open_the_db_and_read_the_data_lim(name_database_table="config", number_of_accounts=1)
    for row in records:
        # Подключение к Telegram и вывод имя аккаунта в консоль / терминал
        client, phone = telegram_connect_and_output_name(row, db_handler)
        tg_tar = output_a_list_of_groups_new(client)
        all_participants_list = await parsing_of_users_from_the_selected_group(page, lv, client, tg_tar)
        # Записываем parsing данные в файл user_settings/software_database.db
        entities = all_participants_user(page, lv, all_participants_list)
        db_handler.write_parsed_chat_participants_to_db(entities)
        db_handler.clean_no_username()  # Чистка списка parsing списка, если нет username
        db_handler.delete_duplicates(table_name="members",
                                     column_name="id")  # Чистка дублирующих username по столбцу id
        client.disconnect()  # Разрываем соединение telegram


def output_a_list_of_groups_new(client):
    """Выводим список групп, выбираем группу, которую будем parsing user с группы telegram"""
    chats = []
    last_date = None
    groups = []
    result = client(GetDialogsRequest(offset_date=last_date, offset_id=0,
                                      offset_peer=InputPeerEmpty(), limit=200, hash=0))
    chats.extend(result.chats)
    for chat in chats:
        try:
            if chat.megagroup:
                groups.append(chat)
        except Exception as e:
            logger.info(f'Ошибка parsing: {e}')  # Ошибка при parsing группы telegram, выводим ошибку
            continue  # Записываем ошибку в software_database.db и продолжаем работу
    i = 0
    for g in groups:
        logger.info(f"[{str(i)}] - {g.title}")
        i += 1
    logger.info("")
    g_index = input("[+] Введите номер : ")
    target_group = groups[int(g_index)]
    return target_group


"""Parsing активных участников группы"""


async def we_get_the_data_of_the_group_members_who_wrote_messages(client, chat, limit_active_user) -> None:
    """
    Получаем данные участников группы которые писали сообщения
    :param client: клиент Telegram
    :param chat: ссылка на чат
    :param limit_active_user: лимит активных участников
    """
    for message in client.iter_messages(chat, limit=int(limit_active_user)):
        from_user = client.get_entity(message.from_id.user_id)  # Получаем отправителя по ИД
        configs_reader = ConfigReader()
        # time_activity_user_1, time_activity_user_2 = configs_reader.get_time_activity_user()
        # display_progress_bar(time_activity_user_1, time_activity_user_2, "Выполнение задачи...")
        entities = getting_active_user_data(from_user)
        logger.info(entities)
        db_handler = DatabaseHandler()
        await db_handler.write_parsed_chat_participants_to_db_active(entities)


async def parsing_of_active_participants(chat_input, limit_active_user) -> None:
    """
    Parsing участников, которые пишут в чат (активных участников)

    :param chat_input: ссылка на чат
    :param limit_active_user: лимит активных участников
    """
    # Открываем базу с аккаунтами и с выставленными лимитами
    db_handler = DatabaseHandler()
    records: list = await db_handler.open_the_db_and_read_the_data_lim(name_database_table="config",
                                                                       number_of_accounts=1)
    for row in records:
        # Подключение к Telegram и вывод имя аккаунта в консоль / терминал
        client, phone = telegram_connect_and_output_name(row, db_handler)
        # Подписываемся на чат, с которого будем parsing активных участников
        await subscribe_to_group_or_channel(client, chat_input)
        configs_reader = ConfigReader()
        time_activity_user_1, time_activity_user_2 = configs_reader.get_time_activity_user()
        time.sleep(time_activity_user_2)
        await we_get_the_data_of_the_group_members_who_wrote_messages(client, chat_input, limit_active_user)
        client.disconnect()  # Разрываем соединение telegram
    await db_handler.clean_no_username()  # Чистка списка parsing списка, если нет username
    await db_handler.delete_duplicates(table_name="members",
                                       column_name="id")  # Чистка дублирующих username по столбцу id


"""Работа с номерами телефонов"""


def we_record_phone_numbers_in_the_db(db_handler) -> None:
    """Записываем номера телефонов в базу данных"""
    logger.info("Контакты которые были добавлены в телефонную книгу, будем записывать с файл "
                "software_database.db, в папке user_settings")
    # Вводим имя файла с которым будем работать
    file_name_input = input("[+] Введите имя файла с контактами, в папке contacts, имя вводим без txt: ")
    # Открываем файл с которым будем работать
    with open(f"user_settings/{file_name_input}.txt", "r") as file_contact:
        for line in file_contact.readlines():
            logger.info(line.strip())
            # strip() - удаляет с конца и начала строки лишние пробелы, в том числе символ окончания строки
            lines = line.strip()
            entities = [lines]
            db_handler.write_data_to_db("CREATE TABLE IF NOT EXISTS contact(phone)",
                                        "INSERT INTO contact(phone) VALUES (?)", entities)


def show_account_contact_list(db_handler) -> None:
    """Показать список контактов аккаунтов и запись результатов в файл"""
    # Открываем базу данных для работы с аккаунтами user_settings/software_database.db
    records: list = db_handler.open_and_read_data("config")
    for row in records:
        # Подключение к Telegram и вывод имя аккаунта в консоль / терминал
        client, phone = telegram_connect_and_output_name(row, db_handler)
        parsing_and_recording_contacts_in_the_database(client, db_handler)
        client.disconnect()  # Разрываем соединение telegram


def parsing_and_recording_contacts_in_the_database(client, db_handler) -> None:
    """Парсинг и запись контактов в базу данных"""
    entities = []  # Создаем список сущностей
    all_participants = get_and_parse_contacts(client)
    for contact in all_participants:  # Выводим результат parsing
        getting_user_data(contact, entities)
    db_handler.write_parsed_chat_participants_to_db(entities)


def we_get_the_account_id(client, db_handler) -> None:
    """Получаем id аккаунта"""
    entities = []  # Создаем список сущностей
    all_participants = get_and_parse_contacts(client)
    for user in all_participants:  # Выводим результат parsing
        getting_user_data(user, entities)
        we_show_and_delete_the_contact_of_the_phone_book(client, user)
    db_handler.write_parsed_chat_participants_to_db(entities)


def get_and_parse_contacts(client) -> list:
    all_participants: list = []
    result = client(functions.contacts.GetContactsRequest(hash=0))
    logger.info(result)  # Печатаем результат
    all_participants.extend(result.users)
    return all_participants


def we_show_and_delete_the_contact_of_the_phone_book(client, user) -> None:
    """Показываем и удаляем контакт телефонной книги"""
    client(functions.contacts.DeleteContactsRequest(id=[user.id]))
    logger.info("Подождите 2 - 4 секунды")
    time.sleep(random.randrange(2, 3, 4))  # Спим для избежания ошибки о flood


def delete_contact(db_handler) -> None:
    """Удаляем контакты с аккаунтов"""
    records: list = db_handler.open_and_read_data("config")
    for row in records:
        # Подключение к Telegram и вывод имя аккаунта в консоль / терминал
        client, phone = telegram_connect_and_output_name(row, db_handler)
        we_get_the_account_id(client, db_handler)
        client.disconnect()  # Разрываем соединение telegram


def inviting_contact(db_handler) -> None:
    """Добавление данных в телефонную книгу с последующим формированием списка software_database.db, для inviting"""
    # Открываем базу данных для работы с аккаунтами user_settings/software_database.db
    records: list = db_handler.open_and_read_data("config")
    logger.info(f"Всего accounts: {len(records)}")
    for row in records:
        # Подключение к Telegram и вывод имя аккаунта в консоль / терминал
        client, phone = telegram_connect_and_output_name(row, db_handler)
        adding_a_contact_to_the_phone_book(client, db_handler)


def adding_a_contact_to_the_phone_book(client, db_handler) -> None:
    """Добавляем контакт в телефонную книгу"""

    records: list = db_handler.open_and_read_data("contact")
    logger.info(f"Всего номеров: {len(records)}")
    entities = []  # Создаем список сущностей
    for rows in records:
        user = {"phone": rows[0]}
        phone = user["phone"]
        # Добавляем контакт в телефонную книгу
        client(functions.contacts.ImportContactsRequest(contacts=[types.InputPhoneContact(client_id=0,
                                                                                          phone=phone,
                                                                                          first_name="Номер",
                                                                                          last_name=phone)]))
        try:
            # Получаем данные номера телефона https://docs.telethon.dev/en/stable/concepts/entities.html
            contact = client.get_entity(phone)
            getting_user_data(contact, entities)
            logger.info(f"[+] Контакт с добавлен в телефонную книгу!")
            time.sleep(4)
            # Запись результатов parsing в файл members_contacts.db, для дальнейшего inviting
            # После работы с номером телефона, программа удаляет номер со списка
            db_handler.delete_row_db(table="contact", column="phone", value=user["phone"])
        except ValueError:
            logger.info(
                f"[+] Контакт с номером {phone} не зарегистрирован или отсутствует возможность добавить в телефонную книгу!")
            # После работы с номером телефона, программа удаляет номер со списка
            db_handler.delete_row_db(table="contact", column="phone", value=user["phone"])
    client.disconnect()  # Разрываем соединение telegram
    db_handler.write_parsed_chat_participants_to_db(entities)
    db_handler.clean_no_username()  # Чистка списка parsing списка, если нет username
