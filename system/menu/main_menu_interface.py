from loguru import logger
from rich import box
from rich.table import Table

from system.account_actions.answering_machine.answering_machine import launching_an_answering_machine
from system.account_actions.checking_spam.account_verification import check_account_for_spam
from system.account_actions.creating.account_registration import change_bio_profile
from system.account_actions.creating.creating import creating_groups_and_chats
from system.account_actions.invitation.inviting_participants_telegram import invitation_from_all_accounts_program_body
from system.account_actions.invitation.inviting_participants_telegram import invite_from_multiple_accounts_with_limits
from system.account_actions.invitation.telegram_invite_scheduler import launching_an_invite_once_an_hour
from system.account_actions.invitation.telegram_invite_scheduler import launching_invite_every_day_certain_time
from system.account_actions.invitation.telegram_invite_scheduler import schedule_invite
from system.account_actions.parsing.parsing_account_groups_and_channels import parsing_groups_which_account_subscribed
from system.account_actions.parsing.parsing_group_members import choosing_a_group_from_the_subscribed_ones_for_parsing
from system.account_actions.parsing.parsing_group_members import delete_contact
from system.account_actions.parsing.parsing_group_members import inviting_contact
from system.account_actions.parsing.parsing_group_members import parsing_mass_parsing_of_groups
from system.account_actions.parsing.parsing_group_members import parsing_of_active_participants
from system.account_actions.parsing.parsing_group_members import show_account_contact_list
from system.account_actions.parsing.parsing_group_members import we_record_phone_numbers_in_the_db
from system.account_actions.reactions.reactions import reaction_gui
from system.account_actions.reactions.reactions import record_the_number_of_accounts
from system.account_actions.reactions.reactions import recording_link_channel
from system.account_actions.reactions.reactions import setting_reactions
from system.account_actions.reactions.reactions import users_choice_of_reaction
from system.account_actions.reactions.reactions import viewing_posts
from system.account_actions.sending_messages.chat_dialog_mes import message_entry_window_time, message_time
from system.account_actions.sending_messages.sending_messages_telegram import send_files_to_personal_account
from system.account_actions.sending_messages.sending_messages_telegram import we_send_a_message_by_members
from system.account_actions.sending_messages.telegram_chat_dialog import sending_messages_chats, sending_files_via_chats
from system.account_actions.sending_messages.telegram_chat_dialog import sending_messages_files_via_chats
from system.account_actions.subscription.subscription import subscription_all
from system.account_actions.unsubscribe.unsubscribe import unsubscribe_all
from system.auxiliary_functions.auxiliary_functions import *
from system.auxiliary_functions.global_variables import *
from system.menu.app_gui import output_the_input_field, writing_members
from system.setting.setting import *
from system.sqlite_working_tools.sqlite_working_tools import *

logger.add("user_settings/log/log.log", rotation="1 MB", compression="zip")


def main_menu() -> None:  # 1 - Основное меню программы
    """Основное меню программы"""
    db_handler = DatabaseHandler()  # Создаем объект для работы с БД
    clearing_console_showing_banner()  # Чистим консоль, выводим банер
    table = Table(title="[medium_purple3]Основные функции программы!", box=box.HORIZONTALS)  # Выводим таблицу
    column_names(table)  # Формируем колонки таблицы
    # Выводим текст в таблице
    table.add_row("1", f"Inviting {link_group}", "Inviting по времени, по номерам, по parsing списку")
    table.add_row("2", "Parsing", "Parsing списка или до запись в существующий")
    table.add_row("3", "Работа с контактами", "Добавляем контакт в телефонную книгу, и создаем список для inviting")
    table.add_row("4", "Подписка, отписка", "Подписка, отписка  групп / каналов, формирование списка для подписки")
    table.add_row("5", "Подключение аккаунтов", "Подключение новых аккаунтов")
    table.add_row("6", "Рассылка сообщений", "Рассылка: в личку, по чатам (потребуется сформировать список чатов)")
    table.add_row("7", "Работа с реакциями", "Ставим реакции на посты: группе, канале. Потребуется ссылка на пост")
    table.add_row("8", "Настройки", "Запись ссылки для Inviting, api_id, api_hash, установка времени")
    table.add_row("9", "Проверка аккаунтов", "Проверка аккаунтов через спам бот")
    table.add_row("10", "Создание групп (чатов)", "Автоматическое создание групп и чатов")
    table.add_row("11", "Редактирование BIO", "Редактирование описания профиля")
    table.add_row("12", "Автоответчик", "Проверка автоответчика")
    console.print(table, justify="center")  # Отображаем таблицу
    user_input = console.input("[medium_purple3][+] Введите номер: ")
    clearing_console_showing_banner()  # Чистим консоль, выводим банер
    if user_input == "1":  # Inviting в группы
        inviting_groups(db_handler)
    elif user_input == "2":  # Parsing, в новый файл members.db и до записи в файл
        telegram_parsing_menu(db_handler)
    elif user_input == "3":  # Работаем с контактами телефонной книги
        working_tools_contacts(db_handler)
    elif user_input == "4":  # Работаем с подпиской, подписка, отписка, запись ссылок в файл
        subscribe_unsubscribe_write_to_file(db_handler)
    elif user_input == "5":  # Подключение новых аккаунтов, методом ввода нового номера телефона
        connecting_new_account(db_handler)
        main_menu()
    elif user_input == "6":  # Рассылка сообщений по списку members.db
        sending_messages_to_a_personal_account_chat(db_handler)
    elif user_input == "7":  # Работа с реакциями
        working_with_the_reaction(db_handler)
    elif user_input == "8":  # Настройки для программы (прописываем ссылку для inviting, api_id, api_hash)
        program_settings(db_handler)
    elif user_input == "9":  # Проверка аккаунта через спам бот
        check_account_for_spam(db_handler)
    elif user_input == "10":  # Создание групп (чатов)
        creating_groups_and_chats(db_handler)
    elif user_input == '11':
        change_bio_profile(db_handler)  # Редактирование описания профиля
    elif user_input == '12':
        launching_an_answering_machine(db_handler)  # Проверка автоответчика
    else:
        main_menu()  # После отработки функции переходим в начальное меню


def inviting_groups(db_handler) -> None:  # 1 - Inviting в группы
    """"Inviting в группы"""
    clearing_console_showing_banner()  # Чистим консоль, выводим банер
    table = Table(title=f"[medium_purple3]Inviting {link_group}!", box=box.HORIZONTALS)  # Выводим таблицу
    column_names(table)  # Формируем колонки таблицы
    # Выводим текст в таблице
    table.add_row("1", f"Inviting {link_group}", "Inviting по списку members")
    table.add_row("2", f"Inviting {link_group}, с лимитами", "Inviting по списку members, с лимитами на аккаунт")
    table.add_row("3", f"Inviting {link_group} 1 раз в час", "Inviting по списку members с запуском 1 рав в час")
    table.add_row("4", f"Inviting time {link_group}", "Inviting по списку members (запуск по времени)")
    table.add_row("5", f"Inviting time avery day{link_group}",
                  "Inviting по списку members (запуск по времени каждый день)")
    table.add_row("0", "Вернуться назад", "Возвращаемся в начальное меню")
    console.print(table, justify="center")  # Отображаем таблицу
    user_input = console.input("[medium_purple3][+] Введите номер: ")
    clearing_console_showing_banner()  # Чистим консоль, выводим банер
    if user_input == "1":  # Inviting по списку software_database.db
        invitation_from_all_accounts_program_body(name_database_table="members", db_handler=db_handler)
    elif user_input == "2":  # Inviting по списку software_database.db, с лимитами
        invite_from_multiple_accounts_with_limits(name_database_table="members", db_handler=db_handler)
    elif user_input == "3":  # Inviting по времени 1 раз в час
        launching_an_invite_once_an_hour()
    elif user_input == "4":  # Inviting по времени
        schedule_invite()
    elif user_input == "5":  # Inviting по времени каждый день
        launching_invite_every_day_certain_time()
    elif user_input == "0":  # Вернуться назад
        main_menu()  # После отработки функции переходим в начальное меню
    else:
        inviting_groups(db_handler)  # Если пользователь ввел не правильный номер, то возвращаемся в начало выбора
    main_menu()  # После отработки функции переходим в начальное меню


def telegram_parsing_menu(db_handler) -> None:  # 2 - Parsing групп и активных участников группы
    """Parsing групп и активных участников группы"""
    clearing_console_showing_banner()  # Чистим консоль, выводим банер
    table = Table(title="[medium_purple3]Parsing участников групп!", box=box.HORIZONTALS)  # Выводим таблицу
    column_names(table)  # Формируем колонки таблицы
    # Выводим текст в таблице
    table.add_row("1", "Parsing одной групп", "Parsing в список software_database.db")
    table.add_row("2", "Выбор группы из подписанных", "Parsing группы из подписанных групп аккаунтом")
    table.add_row("3", "Parsing активных участников", "Parsing участников которые которые писали сообщения в группе")
    table.add_row("4", "Parsing списка: групп, каналов аккаунтов", "Программа соберет: группы / каналы аккаунтов")
    table.add_row("5", "Очистка parsing списка", "Очистка списка software_database.db")
    table.add_row("6", "Формирование списка", "Формирование собственного списка username")
    table.add_row("0", "Вернуться назад", "Возвращаемся в начальное меню")
    console.print(table, justify="center")  # Отображаем таблицу
    user_input = console.input("[medium_purple3][+] Введите номер: ")
    clearing_console_showing_banner()  # Чистим консоль, выводим банер
    if user_input == "1":  # Parsing: группы, групп в список software_database.db (группы вводятся в графическое окно)

        print("[medium_purple3][+] Введите ссылки чатов которые будем parsing, для вставки в графическое окно "
              "используйте комбинацию клавиш Ctrl + V, обратите внимание что при использование комбинации язык должен "
              "быть переключен на английский")
        # Перед началом parsing очистка таблицы writing_group_links
        db_handler.cleaning_db(name_database_table="writing_group_links")
        output_the_input_field(db_handler)
        parsing_mass_parsing_of_groups(db_handler)  # Парсинг участников чата

    elif user_input == "2":  # Parsing группы из подписанных
        choosing_a_group_from_the_subscribed_ones_for_parsing(db_handler)
    elif user_input == "3":  # Parsing активных участников группы
        chat_input: str = console.input(
            "[medium_purple3][+] Введите ссылку на чат с которого будем собирать активных: ")
        limit_active_user: int = console.input(
            "[medium_purple3][+] Введите количество сообщений которые будем parsing: ")
        parsing_of_active_participants(chat_input, limit_active_user, db_handler)
    elif user_input == "4":  # Parsing групп / каналов на которые подписан аккаунт
        parsing_groups_which_account_subscribed(db_handler)
    elif user_input == "5":  # Очистка списка software_database.db
        db_handler.cleaning_db(name_database_table="members")
    elif user_input == "6":  # Формирование списка
        writing_members(db_handler)
    elif user_input == "0":  # Вернуться назад
        main_menu()  # После отработки функции переходим в начальное меню
    else:
        telegram_parsing_menu(db_handler)
    # main_menu()  # После отработки функции переходим в начальное меню


def working_tools_contacts(db_handler) -> None:  # 3 - Работаем с контактами телефонной книги
    """Работаем с контактами телефонной книги"""
    clearing_console_showing_banner()  # Чистим консоль, выводим банер
    table = Table(title="[medium_purple3]Работа с контактами!", box=box.HORIZONTALS)  # Выводим таблицу
    column_names(table)  # Формируем колонки таблицы
    # Выводим текст в таблице
    table.add_row("1", "Формирование списка контактов", "Подготовление списка контактов для работы с ним")
    table.add_row("2", "Показать список контактов", "Отображение списка контактов аккаунта")
    table.add_row("3", "Удаление контактов", "Удаление контактов во всех аккаунтах")
    table.add_row("4", "Добавление контактов", "Добавляем контакты в телефонную книгу")
    table.add_row("0", "Вернуться назад", "Возвращаемся в начальное меню")
    console.print(table, justify="center")  # Отображаем таблицу
    user_input = console.input("[medium_purple3][+] Введите номер: ")
    clearing_console_showing_banner()  # Чистим консоль, выводим банер
    if user_input == "1":  # Формирование списка контактов
        we_record_phone_numbers_in_the_db(db_handler)
    elif user_input == "2":  # Отображение списка контактов
        show_account_contact_list(db_handler)
    elif user_input == "3":  # Удаляем все контакты с аккаунтов
        delete_contact(db_handler)
    elif user_input == "4":  # Вносим контакты в телефонную книгу
        inviting_contact(db_handler)
    elif user_input == "0":  # Вернуться назад
        main_menu()  # После отработки функции переходим в начальное меню
    else:
        working_tools_contacts(db_handler)
    main_menu()  # После отработки функции переходим в начальное меню


def subscribe_unsubscribe_write_to_file(db_handler) -> None:  # 4 - Подписка, отписка, запись в файл групп
    """Подписка, отписка, запись в файл групп"""
    clearing_console_showing_banner()  # Чистим консоль, выводим банер
    table = Table(title="[medium_purple3]Подписываемся / отписываемся!", box=box.HORIZONTALS)  # Выводим таблицу
    column_names(table)  # Формируем колонки таблицы
    # Выводим текст в таблице
    table.add_row("1", "Подписка", "Подписка на группы / каналы")
    table.add_row("2", "Отписываемся", "Отписываемся от групп / каналов чистим аккаунты")
    table.add_row("0", "Вернуться назад", "Возвращаемся в начальное меню")
    console.print(table, justify="center")  # Отображаем таблицу
    user_input = console.input("[medium_purple3][+] Введите номер: ")
    clearing_console_showing_banner()  # Чистим консоль, выводим банер
    if user_input == "1":  # Запись: групп, каналов в файл, в файл user_settings/software_database.db
        subscription_all(db_handler)
    elif user_input == "2":  # Отписываемся от групп / каналов (работа с несколькими аккаунтами)
        unsubscribe_all(db_handler)
    elif user_input == "0":  # Вернуться назад
        main_menu()  # После отработки функции переходим в начальное меню
    else:
        subscribe_unsubscribe_write_to_file(db_handler)
    main_menu()  # После отработки функции переходим в начальное меню


def sending_messages_to_a_personal_account_chat(db_handler) -> None:  # 6 - Рассылка сообщений в личку
    """Рассылка сообщений в личку"""
    clearing_console_showing_banner()  # Чистим консоль, выводим банер
    table = Table(title="[medium_purple3]Рассылка сообщений в личку!", box=box.HORIZONTALS)  # Выводим таблицу
    column_names(table)  # Формируем колонки таблицы
    # Выводим текст в таблице
    table.add_row("1", "Отправка сообщений в личку", "Отправка сообщений в личку по parsing списку")
    table.add_row("2", "Отправка файлов в личку", "Отправка файлов в личку по parsing списку")
    table.add_row("3", "Рассылка сообщений по чатам", "Рассылка сообщений по чатам, потребуется сформировать список")
    table.add_row("4", "Рассылка сообщений по чатам, по времени", "Потребуется заранее сформировать список чатов")
    table.add_row("5", "Рассылка файлов по чатам", "Рассылка файлов по чатам, потребуется заранее записать чаты в файл")
    table.add_row("6", "Рассылка сообщений + файлов по чатам", "Потребуется заранее сформировать список чатов")
    table.add_row("7", "Отправка сообщений в личку (с лимитами)",
                  "Отправка сообщений в личку по parsing списку (с лимитами)")
    table.add_row("8", "Отправка файлов в личку (с лимитами)", "Отправка файлов в личку по parsing списку (с лимитами)")
    table.add_row("0", "Вернуться назад", "Возвращаемся в начальное меню")
    console.print(table, justify="center")  # Отображаем таблицу
    user_input = console.input("[medium_purple3][+] Введите номер: ")
    clearing_console_showing_banner()  # Чистим консоль, выводим банер
    if user_input == "1":  # Отправка сообщений в личку по parsing списку user_settings/software_database.db
        we_send_a_message_by_members(limits=None, db_handler=db_handler)
    elif user_input == "2":  # Отправка файлов в личку по parsing списку user_settings/software_database.db
        send_files_to_personal_account(limits=None, db_handler=db_handler)
    elif user_input == "3":  # Рассылка сообщений по чатам
        sending_messages_chats(db_handler)
    elif user_input == "4":  # Рассылка сообщений по чатам по времени
        message_entry_window_time()
        message_time()
    elif user_input == "5":  # Рассылка файлов по чатам
        sending_files_via_chats(db_handler)
    elif user_input == "6":  # Рассылка сообщений + файлов по чатам
        sending_messages_files_via_chats()
    elif user_input == "7":  # Отправка сообщений в личку (с лимитами)
        we_send_a_message_by_members(limits=limits_message, db_handler=db_handler)
    elif user_input == "8":  # Отправка файлов в личку (с лимитами)
        send_files_to_personal_account(limits=limits_message, db_handler=db_handler)
    elif user_input == "0":  # Вернуться назад
        main_menu()  # После отработки функции переходим в начальное меню
    else:
        sending_messages_to_a_personal_account_chat(db_handler)
    main_menu()  # После отработки функции переходим в начальное меню


def working_with_the_reaction(db_handler) -> None:  # 7 - Работа с реакциями на посты группы или канала
    """Работа с реакциями на посты группы или канала"""
    clearing_console_showing_banner()  # Чистим консоль, выводим банер
    table = Table(title="[medium_purple3]Работа с реакциями / постами!", box=box.HORIZONTALS)  # Выводим таблицу
    column_names(table)  # Формируем колонки таблицы
    # Выводим текст в таблице
    table.add_row("1", "Ставим реакцию на 1 пост", "Ставим реакции на один пост с группе / канале")
    table.add_row("2", "Накручиваем просмотры постов", "Накручиваем просмотры постов канале")
    table.add_row("3", "Автоматическое выставление реакций",
                  "Автоматическое проставление реакций на посты, требуются настройки программы")
    table.add_row("0", "Вернуться назад", "Возвращаемся в начальное меню")
    console.print(table, justify="center")  # Отображаем таблицу
    user_input = console.input("[medium_purple3][+] Введите номер: ")
    clearing_console_showing_banner()  # Чистим консоль, выводим банер
    if user_input == "1":  # Ставим реакции на один пост в группе / канале
        users_choice_of_reaction(db_handler)
    elif user_input == "2":  # Накручиваем просмотры постов
        viewing_posts(db_handler)
    elif user_input == "3":
        setting_reactions(db_handler)  # Автоматическое выставление реакций
    elif user_input == "0":  # Вернуться назад
        main_menu()  # После отработки функции переходим в начальное меню
    else:
        working_with_the_reaction(db_handler)
    main_menu()  # После отработки функции переходим в начальное меню


def program_settings(
        db_handler) -> None:  # 8 - Настройки программы, запись времени, api_id, api_hash, запись ссылки для inviting
    """Настройки программы, запись времени задержки, api_id, api_hash, запись ссылки для inviting"""
    clearing_console_showing_banner()  # Чистим консоль, выводим банер
    table = Table(title="[medium_purple3]Настройки программы!", box=box.HORIZONTALS)  # Выводим таблицу
    column_names(table)  # Формируем колонки таблицы
    # Выводим текст в таблице
    table.add_row("1", "Запись ссылки",
                  "Запись ссылки, для Inviting")
    table.add_row("2", "Запись api_id, api_hash",
                  "Запись api_id, api_hash")
    table.add_row("3", "Время между Inviting, рассылка сообщений",
                  "Запись времени между: Inviting, рассылка сообщений")
    table.add_row("4", "Смена аккаунтов",
                  "Запись времени между сменой аккаунтов")
    table.add_row("5", "Время между подпиской",
                  "Запись времени между сменой групп при подписке.")
    table.add_row("6", "Запись proxy",
                  "Запись данных для proxy")
    table.add_row("7", "Лимиты на аккаунт",
                  "Установление лимитов на аккаунт")
    table.add_row("8", "Смена типа устройства",
                  "Запись данных для смены типа устройства")
    table.add_row("9", "Запись времени",
                  "Запись времени для Inviting один раз в сутки")
    table.add_row("10", "Лимиты на сообщения",
                  "Установление лимитов на сообщения")
    table.add_row("11", "Выбор реакций",
                  "Выбор нескольких реакций (gui) для выставления на пост")
    table.add_row("12", "Запись ссылки для реакций",
                  "Запись ссылки на канал / группу, для автоматического выставления реакции на новые посты")
    table.add_row("13", "Запись количества аккаунтов для реакций",
                  "Количество аккаунтов, которые будут ставить реакции на посты каналов / групп")
    table.add_row("14", "Запись сообщений",
                  "Запись сообщений для для рассылки сообщений по чатам")
    table.add_row("15", "Запись времени между сообщениями",
                  "Запись времени для рассылки сообщений по чатам между сообщениями")
    table.add_row("16", "Формирование списка чатов / каналов",
                  "Формирование списка чатов для рассылки сообщений по чатам, подписки на группы / каналы")
    table.add_row("0", "Вернуться назад", "Возвращаемся в начальное меню")
    console.print(table, justify="center")  # Отображаем таблицу
    user_input = console.input("[medium_purple3][+] Введите номер: ")
    clearing_console_showing_banner()  # Чистим консоль, выводим банер
    if user_input == "1":  # Запись ссылки для inviting (Записываем ссылку на группу, которую будем inviting)
        print("[magenta][!] Давайте запишем ссылку для inviting, ссылка должна быть [medium_purple3]одна! Обратите "
              "внимание, что программа будет заново запущена")
        writing_settings_to_a_file(config=writing_link_to_the_group())
        os.system("python main.py")  # После отработки функции возвращаемся в начальное меню
    elif user_input == "2":  # Запись id, hash в файл
        print("[medium_purple3][!] Получить api_id, api_hash можно на сайте https://my.telegram.org/auth")
        writing_settings_to_a_file(config=writing_api_id_api_hash())
    if user_input == "3":  # Время между приглашениями Inviting / Рассылка сообщений
        print("[medium_purple3][+] Введите время между Inviting / Рассылка сообщений! C начала меньшее, потом большее. "
              "НАПРИМЕР: 10 20!")
        create_main_window(variable="time_inviting")
    elif user_input == "4":  # Время между сменой аккаунтов
        print("[medium_purple3][+] Введите время между сменой аккаунтов в секундах. C начала меньшее, потом большее. "
              "НАПРИМЕР: 10 20!")
        create_main_window(variable="time_changing_accounts")
    elif user_input == "5":  # Время между подпиской групп
        print("[medium_purple3][+] Введите время между подпиской на группы / каналы в секундах (между приглашениями) C "
              "начала меньшее, потом большее. НАПРИМЕР: 10 20!")
        create_main_window(variable="time_subscription")
    elif user_input == "6":  # Запись данных для proxy
        creating_the_main_window_for_proxy_data_entry(db_handler)
        program_settings(db_handler)
    elif user_input == "7":  # Запись лимитов на аккаунт
        writing_settings_to_a_file(config=record_account_limits())
    elif user_input == "8":  # Запись типа устройства
        writing_settings_to_a_file(config=record_device_type())
    elif user_input == "9":  # Запись времени для запуска inviting в определенное время
        recording_the_time_to_launch_an_invite_every_day()
    elif user_input == "10":  # Запись лимитов на количество сообщений
        writing_settings_to_a_file(config=record_message_limits())
    elif user_input == "11":  # Выбор реакции
        reaction_gui()  # Вызов функции выбора реакции
    elif user_input == "12":  # Запись ссылки для реакций
        recording_link_channel()
    elif user_input == "13":  # Запись ссылки для рассылки
        record_the_number_of_accounts()
    elif user_input == "14":  # Запись текста для рассылки
        recording_text_for_sending_messages()  # Вызов функции записи текста для рассылки
    elif user_input == "15":  # Запись времени между сообщениями
        recording_the_time_between_chat_messages(variable="time_sending_messages")
    elif user_input == "16":  # Формирование списка чатов
        output_the_input_field(db_handler)  # Вызов функции формирования списка чатов
    elif user_input == "0":  # Вернуться назад
        main_menu()  # После отработки функции переходим в начальное меню
    else:
        program_settings(db_handler)
    # main_menu()  # После отработки функции переходим в начальное меню


if __name__ == "__main__":
    try:
        main_menu()
    except Exception as e:
        logger.exception(e)
        print("[medium_purple3][!] Произошла ошибка, для подробного изучения проблемы просмотрите файл log.log")
