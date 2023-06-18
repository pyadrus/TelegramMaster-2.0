# coding: utf-8
from tkinter import *

from rich import print
from telethon import types
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import ChannelParticipantsSearch
from telethon.tl.types import InputPeerEmpty
from telethon.tl.types import UserStatusLastMonth
from telethon.tl.types import UserStatusLastWeek
from telethon.tl.types import UserStatusOffline
from telethon.tl.types import UserStatusRecently

from system.actions.subscription.subscription import subscribe_to_the_group_and_send_the_link
from system.auxiliary_functions.global_variables import console
from system.error.telegram_errors import handle_exceptions_pars
from system.menu.gui_program import program_window
from system.notification.notification import app_notifications
from system.sqlite_working_tools.sqlite_working_tools import cleaning_list_of_participants_who_do_not_have_username, \
    write_members_column_table
from system.sqlite_working_tools.sqlite_working_tools import delete_duplicates
from system.sqlite_working_tools.sqlite_working_tools import delete_row_db
from system.sqlite_working_tools.sqlite_working_tools import open_the_db_and_read_the_data
from system.sqlite_working_tools.sqlite_working_tools import open_the_db_and_read_the_data_lim
from system.sqlite_working_tools.sqlite_working_tools import write_parsed_chat_participants_to_db
from system.telegram_actions.telegram_actions import connect_to_telegram_account_and_output_name


def all_participants_user(all_participants):
    """Формируем список setting_user/software_database.db"""
    entities = []  # Создаем словарь
    for user in all_participants:
        # Если нет имени, то записываем "NONE", для дальнейшего поиска слова "NONE" и удаления с базы данных
        username = user.username if user.username else "NONE"
        user_phone = user.phone if user.phone else "Номер телефона скрыт"
        first_name = user.first_name if user.first_name else ""
        last_name = user.last_name if user.last_name else ""
        photos_id = "Пользователь с фото" if isinstance(user.photo, types.UserProfilePhoto) else "Пользователь без фото"
        online_at = ""
        # Статусы пользователя https://core.telegram.org/type/UserStatus
        if isinstance(user.status, (UserStatusRecently, UserStatusOffline, UserStatusLastWeek, UserStatusLastMonth)):
            if isinstance(user.status, UserStatusOffline):
                online_at = user.status.was_online
            if isinstance(user.status, UserStatusRecently):
                online_at = "Был(а) недавно"
            if isinstance(user.status, UserStatusLastWeek):
                online_at = "Был(а) на этой неделе"
            if isinstance(user.status, UserStatusLastMonth):
                online_at = "Был(а) в этом месяце"
        user_premium = "Пользователь с premium" if user.premium else ""
        # Заполняем словарь
        entities.append([username, user.id, user.access_hash, first_name, last_name, user_phone, online_at, photos_id,
                         user_premium])
    return entities  # Возвращаем словарь пользователей


def parsing_mass_parsing_of_groups() -> None:
    """Parsing групп, ввод в графическое окно списка групп"""
    # Открываем базу с аккаунтами и с выставленными лимитами
    records: list = open_the_db_and_read_the_data_lim(name_database_table="config", number_of_accounts=1)
    for row in records:
        # Подключение к Telegram и вывод имя аккаунта в консоль / терминал
        client, phone = connect_to_telegram_account_and_output_name(row)
        # Открываем базу с группами для дальнейшего parsing
        records: list = open_the_db_and_read_the_data(name_database_table="writing_group_links")
        for groups in records:  # Поочередно выводим записанные группы
            groups_wr = subscribe_to_the_group_and_send_the_link(client, groups, phone)
            group_parsing(client, groups_wr, phone)  # Parsing групп
            # Удаляем отработанную группу или канал
            delete_row_db(table="writing_group_links", column="writing_group_links", value=groups_wr)
        # Чистка списка parsing списка, если нет username
        cleaning_list_of_participants_who_do_not_have_username()
        delete_duplicates(table_name="members", column_name="id")  # Чистка дублирующих username по столбцу id
        client.disconnect()  # Разрываем соединение telegram
    # Выводим уведомление, если операционная система windows 7, то выводим уведомление в консоль
    app_notifications(notification_text="Список успешно сформирован!")


@handle_exceptions_pars
def group_parsing(client, groups_wr, phone) -> None:
    """
    Эта функция выполняет парсинг групп, на которые пользователь подписался. Аргумент phone используется декоратором
    @handle_exceptions для отлавливания ошибок и записи их в базу данных setting_user/software_database.db.
    """
    with console.status("[bold green]Работа над задачами...", spinner_style="time") as _:
        all_participants: list = parsing_of_users_from_the_selected_group(client, groups_wr)
        # Записываем parsing данные в файл setting_user/software_database.db
        entities = all_participants_user(all_participants)
        write_parsed_chat_participants_to_db(entities)


@handle_exceptions_pars
def choosing_a_group_from_the_subscribed_ones_for_parsing() -> None:
    """Выбираем группу из подписанных для parsing"""
    records: list = open_the_db_and_read_the_data_lim(name_database_table="config", number_of_accounts=1)
    for row in records:
        # Подключение к Telegram и вывод имя аккаунта в консоль / терминал
        client, phone = connect_to_telegram_account_and_output_name(row)
        tg_tar = output_a_list_of_groups_new(client)
        all_participants_list = parsing_of_users_from_the_selected_group(client, tg_tar)
        # Записываем parsing данные в файл setting_user/software_database.db
        entities = all_participants_user(all_participants_list)
        write_parsed_chat_participants_to_db(entities)
        cleaning_list_of_participants_who_do_not_have_username()  # Чистка списка parsing списка, если нет username
        delete_duplicates(table_name="members", column_name="id")  # Чистка дублирующих username по столбцу id
        client.disconnect()  # Разрываем соединение telegram


def parsing_of_users_from_the_selected_group(client, target_group) -> list:
    """Собираем данные user и записываем в файл members.db (создание нового файла members.db)"""
    print('[green][+] Ищем участников... Сохраняем в файл software_database.db...')
    all_participants: list = []
    while_condition = True
    my_filter = ChannelParticipantsSearch('')
    offset = 0
    while while_condition:
        participants = client(
            GetParticipantsRequest(channel=target_group, offset=offset, filter=my_filter, limit=200, hash=0))
        all_participants.extend(participants.users)
        offset += len(participants.users)
        if len(participants.users) < 1:
            while_condition = False
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
        except:
            continue  # Записываем ошибку в software_database.db и продолжаем работу
    i = 0
    for g in groups:
        print(f'[bold green][{str(i)}] - {g.title}')
        i += 1
    print('')
    g_index = console.input("[bold red][+] Введите номер : ")
    target_group = groups[int(g_index)]
    return target_group


def writing_members() -> None:
    """Запускаем окно программы (большого поля ввода)"""
    root, text = program_window()

    def output_values_from_the_input_field() -> None:
        """Выводим значения с поля ввода (то что ввел пользователь)"""
        message_text = text.get("1.0", 'end-1c')
        closing_the_input_field()
        lines = message_text.split('\n')
        write_members_column_table(lines)

    def closing_the_input_field() -> None:
        """Закрываем программу"""
        root.destroy()

    # Создаем кнопку по нажатии которой выведется поле ввода. После ввода чатов данные запишутся во временный файл
    but = Button(root, text="Готово", command=output_values_from_the_input_field)
    but.pack()
    root.mainloop()  # Запускаем программу


if __name__ == "__main__":
    choosing_a_group_from_the_subscribed_ones_for_parsing()
    parsing_mass_parsing_of_groups()
