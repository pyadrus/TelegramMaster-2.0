import random
import time

from loguru import logger
from rich import print
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

from system.account_actions.subscription.subscription import subscribe_to_the_group_and_send_the_link, \
    subscribe_to_group_or_channel
from system.auxiliary_functions.auxiliary_functions import display_progress_bar
from system.auxiliary_functions.global_variables import console, time_activity_user_1, time_activity_user_2
from system.notification.notification import app_notifications
from system.telegram_actions.telegram_actions import telegram_connect_and_output_name


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


def all_participants_user(all_participants) -> list:
    """Формируем список user_settings/software_database.db"""
    entities = []  # Создаем словарь
    for user in all_participants:
        getting_user_data(user, entities)
    return entities  # Возвращаем словарь пользователей


def parsing_mass_parsing_of_groups(db_handler) -> None:
    """Parsing групп, ввод в графическое окно списка групп"""
    # Открываем базу с аккаунтами и с выставленными лимитами
    records: list = db_handler.open_the_db_and_read_the_data_lim(name_database_table="config", number_of_accounts=1)
    for row in records:
        # Подключение к Telegram и вывод имя аккаунта в консоль / терминал
        client, phone = telegram_connect_and_output_name(row, db_handler)
        # Открываем базу с группами для дальнейшего parsing
        records: list = db_handler.open_and_read_data("writing_group_links")
        for groups in records:  # Поочередно выводим записанные группы
            groups_wr = subscribe_to_the_group_and_send_the_link(client, groups, phone, db_handler)
            group_parsing(client, groups_wr, phone, db_handler)  # Parsing групп
            # Удаляем отработанную группу или канал
            db_handler.delete_row_db(table="writing_group_links", column="writing_group_links", value=groups_wr)
        db_handler.cleaning_list_of_participants_who_do_not_have_username()  # Чистка списка parsing списка, если нет username
        db_handler.delete_duplicates(table_name="members",
                                     column_name="id")  # Чистка дублирующих username по столбцу id
        client.disconnect()  # Разрываем соединение telegram
    app_notifications(notification_text="Список успешно сформирован!")  # Выводим уведомление


def group_parsing(client, groups_wr, phone, db_handler) -> None:
    """
    Эта функция выполняет парсинг групп, на которые пользователь подписался. Аргумент phone используется декоратором
    @handle_exceptions для отлавливания ошибок и записи их в базу данных user_settings/software_database.db.
    """
    with console.status("[magenta]Работа над задачами...", spinner_style="time") as _:
        all_participants: list = parsing_of_users_from_the_selected_group(client, groups_wr)
        # Записываем parsing данные в файл user_settings/software_database.db
        entities = all_participants_user(all_participants)
        db_handler.write_parsed_chat_participants_to_db(entities)


def choosing_a_group_from_the_subscribed_ones_for_parsing(db_handler) -> None:
    """Выбираем группу из подписанных для parsing"""
    records: list = db_handler.open_the_db_and_read_the_data_lim(name_database_table="config", number_of_accounts=1)
    for row in records:
        # Подключение к Telegram и вывод имя аккаунта в консоль / терминал
        client, phone = telegram_connect_and_output_name(row, db_handler)
        tg_tar = output_a_list_of_groups_new(client)
        all_participants_list = parsing_of_users_from_the_selected_group(client, tg_tar)
        # Записываем parsing данные в файл user_settings/software_database.db
        entities = all_participants_user(all_participants_list)
        db_handler.write_parsed_chat_participants_to_db(entities)
        db_handler.cleaning_list_of_participants_who_do_not_have_username()  # Чистка списка parsing списка, если нет username
        db_handler.delete_duplicates(table_name="members",
                                     column_name="id")  # Чистка дублирующих username по столбцу id
        client.disconnect()  # Разрываем соединение telegram


def parsing_of_users_from_the_selected_group(client, target_group) -> list:
    """Собираем данные user и записываем в файл members.db (создание нового файла members.db)"""
    print("[magenta][+] Ищем участников... Сохраняем в файл software_database.db...")
    all_participants: list = []
    while_condition = True
    my_filter = ChannelParticipantsSearch("")
    offset = 0
    while while_condition:
        try:
            participants = client(
                GetParticipantsRequest(channel=target_group, offset=offset, filter=my_filter, limit=200, hash=0))
            all_participants.extend(participants.users)
            offset += len(participants.users)
            if len(participants.users) < 1:
                while_condition = False
        except TypeError:
            logger.info(
                f'Ошибка parsing: не верное имя или cсылка {target_group} не является группой / каналом: {target_group}')
            time.sleep(2)
            break
    return all_participants


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
        print(f"[magenta][{str(i)}] - {g.title}")
        i += 1
    print("")
    g_index = console.input("[medium_purple3][+] Введите номер : ")
    target_group = groups[int(g_index)]
    return target_group


"""Parsing активных участников группы"""


def we_get_the_data_of_the_group_members_who_wrote_messages(client, chat, limit_active_user, db_handler) -> None:
    """
    Получаем данные участников группы которые писали сообщения

    Параметры:
    client: клиент
    chat: ссылка на чат
    limit_active_user: лимит активных участников
    """
    for message in client.iter_messages(chat, limit=int(limit_active_user)):
        from_user = client.get_entity(message.from_id.user_id)  # Получаем отправителя по ИД
        display_progress_bar(time_activity_user_1, time_activity_user_2, "Выполнение задачи...")
        entities = getting_active_user_data(from_user)
        logger.info(entities)
        db_handler.write_parsed_chat_participants_to_db_active(entities)


def parsing_of_active_participants(chat_input, limit_active_user, db_handler) -> None:
    """
    Parsing участников, которые пишут в чат (активных участников)

    Параметры:
    chat_input: ссылка на чат
    limit_active_user: лимит активных участников
    """
    # Открываем базу с аккаунтами и с выставленными лимитами
    records: list = db_handler.open_the_db_and_read_the_data_lim(name_database_table="config", number_of_accounts=1)
    for row in records:
        # Подключение к Telegram и вывод имя аккаунта в консоль / терминал
        client, phone = telegram_connect_and_output_name(row, db_handler)
        # Подписываемся на чат, с которого будем parsing активных участников
        subscribe_to_group_or_channel(client, chat_input, phone, db_handler)
        time.sleep(time_activity_user_2)
        we_get_the_data_of_the_group_members_who_wrote_messages(client, chat_input, limit_active_user, db_handler)
        client.disconnect()  # Разрываем соединение telegram
    db_handler.cleaning_list_of_participants_who_do_not_have_username()  # Чистка списка parsing списка, если нет username
    db_handler.delete_duplicates(table_name="members", column_name="id")  # Чистка дублирующих username по столбцу id


"""Работа с номерами телефонов"""


def we_record_phone_numbers_in_the_db(db_handler) -> None:
    """Записываем номера телефонов в базу данных"""
    print("[magenta]Контакты которые были добавлены в телефонную книгу, будем записывать с файл "
          "software_database.db, в папке user_settings")
    # Вводим имя файла с которым будем работать
    file_name_input = console.input(
        "[magenta][+] Введите имя файла с контактами, в папке contacts, имя вводим без txt: ")
    # Открываем файл с которым будем работать
    with open(f"user_settings/{file_name_input}.txt", "r") as file_contact:
        for line in file_contact.readlines():
            print(line.strip())
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
    print(result)  # Печатаем результат
    all_participants.extend(result.users)
    return all_participants


def we_show_and_delete_the_contact_of_the_phone_book(client, user) -> None:
    """Показываем и удаляем контакт телефонной книги"""
    client(functions.contacts.DeleteContactsRequest(id=[user.id]))
    print("[magenta] Подождите 2 - 4 секунды")
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
    print(f"[medium_purple3]Всего accounts: {len(records)}")
    for row in records:
        # Подключение к Telegram и вывод имя аккаунта в консоль / терминал
        client, phone = telegram_connect_and_output_name(row, db_handler)
        adding_a_contact_to_the_phone_book(client, db_handler)


def adding_a_contact_to_the_phone_book(client, db_handler) -> None:
    """Добавляем контакт в телефонную книгу"""

    records: list = db_handler.open_and_read_data("contact")
    print(f"[medium_purple3]Всего номеров: {len(records)}")
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
            print(f"[magenta][+] Контакт с добавлен в телефонную книгу!")
            time.sleep(4)
            # Запись результатов parsing в файл members_contacts.db, для дальнейшего inviting
            # После работы с номером телефона, программа удаляет номер со списка
            db_handler.delete_row_db(table="contact", column="phone", value=user["phone"])
        except ValueError:
            print(f"[magenta][+] Контакт с номером {phone} не зарегистрирован или отсутствует "
                  f"возможность добавить в телефонную книгу!")
            # После работы с номером телефона, программа удаляет номер со списка
            db_handler.delete_row_db(table="contact", column="phone", value=user["phone"])
    client.disconnect()  # Разрываем соединение telegram
    db_handler.write_parsed_chat_participants_to_db(entities)
    db_handler.cleaning_list_of_participants_who_do_not_have_username()  # Чистка списка parsing списка, если нет username
