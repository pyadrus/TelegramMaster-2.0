# -*- coding: utf-8 -*-
from loguru import logger
from rich import box
from rich.table import Table

from system.actions.actions_with_account.account_verification import *
from system.actions.invite.inviting_participants_by_time_telegram import *
from system.actions.invite.inviting_participants_telegram import *
from system.actions.pars.parsing_account_groups_and_channels import *
from system.actions.pars.parsing_active_participants import *
from system.actions.pars.parsing_group_members import *
from system.actions.pars.parsing_phone_numbers import *
from system.actions.reactions.reactions import *
from system.actions.send_mess_chat.chat_dialog import *
from system.actions.send_mess_chat.chat_dialog_mes import *
from system.actions.sending_messages_telegram.sending_messages_telegram import *
from system.actions.subscription.subscription import *
from system.actions.subscription.unsubscribe import *
from system.auxiliary_functions.auxiliary_functions import *
from system.auxiliary_functions.global_variables import *
from system.setting.setting import *
from system.sqlite_working_tools.sqlite_working_tools import *

logger.add("setting_user/log/log.log", rotation="1 MB", compression="zip")


def main_menu() -> None:
    """Основное меню программы"""
    try:
        clearing_console_showing_banner()  # Чистим консоль, выводим банер
        # Выводим таблицу
        table = Table(title="[bold red]Основные функции программы!", box=box.HORIZONTALS)
        column_names(table)  # Формируем колонки таблицы
        # Выводим текст в таблице, нумерация функций начинается с 1
        table.add_row("1", f"Inviting {target_group_entity}",
                      "Inviting по времени, по номерам, по parsing списку")
        table.add_row("2", "Parsing",
                      "Parsing с обновлением списка members файла members_group, или до запись в существующий")
        table.add_row("3", "Работа с контактами",
                      "Добавляем контакт в телефонную книгу, и создаем список для inviting")
        table.add_row("4", "Подписываемся / отписываемся",
                      "Подписка, отписка  групп / каналов, формирование списка, для подписки")
        table.add_row("5", "Подключение аккаунтов",
                      "Подключение новых аккаунтов")
        table.add_row("6", "Рассылка сообщений",
                      "Рассылка сообщений в личку по списку members. Рассылка сообщений по чатам, потребуется "
                      "сформировать список чатов")
        table.add_row("7", "Работа с реакциями",
                      "Ставим реакции на посты в группе или канале, потребуется ссылка на пост и канал")
        table.add_row("8", "Настройки",
                      "Запись ссылки для Inviting, api_id, api_hash, установка времени")
        table.add_row("9", "Проверка аккаунтов",
                      "Проверка аккаунтов через спам бот")
        console.print(table, justify="center")  # Отображаем таблицу
        user_input = console.input("[bold red][+] Введите номер: ")
        if user_input == "1":
            """Inviting в группы"""
            inviting_groups()
        elif user_input == "2":
            """Parsing, в новый файл members.db и до запись в файл"""
            telegram_parsing_menu()
        elif user_input == "3":
            """Работаем с контактами телефонной книги"""
            working_tools_contacts()
        elif user_input == "4":
            """Работаем с подпиской, подписка, отписка, запись ссылок в файл"""
            subscribe_unsubscribe_write_to_file()
        elif user_input == "5":
            """
            Подключение новых аккаунтов, методом ввода нового номера телефона или сканирование сессий и запись в базу 
            данных
            """
            clearing_console_showing_banner()  # Чистим консоль, выводим банер
            connecting_new_account()
            main_menu()
        elif user_input == "6":
            """Рассылка сообщений по списку members.db"""
            sending_messages_to_a_personal_account_chat()
        elif user_input == "7":
            """Работа с реакциями"""
            working_with_the_reaction()
        elif user_input == "8":
            """Настройки для программы (прописываем ссылку для inviting, api_id, api_hash)"""
            program_settings()
        elif user_input == "9":
            """Проверка аккаунта через спам бот"""
            clearing_console_showing_banner()  # Чистим консоль, выводим банер
            check_account_for_spam()
        else:
            main_menu()  # После отработки функции переходим в начальное меню
    except KeyboardInterrupt:
        """Закрытие окна программы"""
        print("[!] Скрипт остановлен!")


"""1 Inviting"""


def inviting_groups() -> None:
    """"Inviting в группы"""
    clearing_console_showing_banner()  # Чистим консоль, выводим банер
    # Выводим таблицу
    table = Table(title=f"[bold red]Inviting {target_group_entity}!", box=box.HORIZONTALS)
    column_names(table)  # Формируем колонки таблицы
    # Выводим текст в таблице
    table.add_row("1", f"Inviting {target_group_entity}",
                  "Inviting по списку members")
    table.add_row("2", f"Inviting {target_group_entity}, с лимитами",
                  "Inviting по списку members, с лимитами на аккаунт")
    table.add_row("3", f"Inviting time {target_group_entity}",
                  "Inviting по списку members (запуск по времени)")
    table.add_row("4", f"Inviting активных участников в чат {target_group_entity}",
                  "Inviting активных участников чата оп ранее parsing списку")
    table.add_row("5", f"Inviting contact {target_group_entity}",
                  "Inviting по списку контактов members")
    table.add_row("0", "Вернуться назад",
                  "Возвращаемся в начальное меню")
    console.print(table, justify="center")  # Отображаем таблицу
    user_input = console.input("[bold red][+] Введите номер: ")
    if user_input == "1":
        """Inviting по списку software_database.db"""
        clearing_console_showing_banner()  # Чистим консоль, выводим банер
        invitation_from_all_accounts_program_body(name_database_table="members")
    elif user_input == "2":
        """Inviting по списку software_database.db, с лимитами"""
        clearing_console_showing_banner()  # Чистим консоль, выводим банер
        invite_from_multiple_accounts_with_limits(name_database_table="members")
    elif user_input == "3":
        """Inviting по времени"""
        clearing_console_showing_banner()  # Чистим консоль, выводим банер
        launching_an_invite_by_time()
    elif user_input == "4":
        """Inviting активных участников чата оп ранее parsing списку"""
        clearing_console_showing_banner()  # Чистим консоль, выводим банер
        invitation_from_all_accounts_program_body(name_database_table="members_active")
    elif user_input == "5":
        """Inviting по сформированному списку контактов"""
        clearing_console_showing_banner()  # Чистим консоль, выводим банер
        invitation_from_all_accounts_program_body(name_database_table="members_contacts")
    elif user_input == "0":
        """Вернуться назад"""
        main_menu()  # После отработки функции переходим в начальное меню
    else:
        inviting_groups()
    main_menu()  # После отработки функции переходим в начальное меню


""" 2 Parsing"""


def telegram_parsing_menu() -> None:
    """Parsing групп и активных участников группы"""
    clearing_console_showing_banner()  # Чистим консоль, выводим банер
    # Выводим таблицу
    table = Table(title="[bold red]Parsing участников групп, и активных участников!", box=box.HORIZONTALS)
    column_names(table)  # Формируем колонки таблицы
    # Выводим текст в таблице, нумерация функций начинается с 0
    table.add_row("1", "Parsing одной группы / групп",
                  "Parsing одной группы / групп в список software_database.db (группы вводятся в графическое окно)")
    table.add_row("2", "Выбираем группу из подписанных для parsing",
                  "Parsing группы из подписанных (использовать если вас ранее пригласили в закрытую группу,"
                  " и вставка ссылки на помогает, или она отсутствует)")
    table.add_row("3", "Parsing участников группы которые которые оставляли сообщения",
                  "Parsing участников группы которые которые оставляли сообщения, от вас потребуется ссылка на "
                  "группу и ввести количество просматриваемых сообщений группы")
    table.add_row("4", "Parsing подписанных групп / каналов аккаунтов",
                  "Parsing групп / каналов на которые подписан аккаунт. Программа соберет все группы / каналы и "
                  "запишет в файл")
    table.add_row("5", "Очистка списка software_database.db",
                  "Очистка списка software_database.db (может понадобится при формировании нового списка для "
                  "Inviting)")
    table.add_row("0", "Вернуться назад",
                  "Возвращаемся в начальное меню")
    console.print(table, justify="center")  # Отображаем таблицу
    user_input = console.input("[bold red][+] Введите номер: ")
    if user_input == "1":
        """Parsing одной группы / групп в список software_database.db (группы вводятся в графическое окно)"""
        clearing_console_showing_banner()  # Чистим консоль, выводим банер
        mass_parsing_of_group()
    elif user_input == "2":
        """Parsing группы из подписанных (использовать если вас ранее пригласили в закрытую
           группу, и вставка ссылки на помогает, или она отсутствует)"""
        clearing_console_showing_banner()  # Чистим консоль, выводим банер
        choosing_a_group_from_the_subscribed_ones_for_parsing()
    elif user_input == "3":
        """Parsing активных участников группы"""
        clearing_console_showing_banner()  # Чистим консоль, выводим банер
        chat_input: str = console.input("[bold red][+] Введите ссылку на чат с которого будем собирать активных: ")
        limit_active_user: int = console.input("[bold red][+] Введите количество сообщений которые будем parsing: ")
        parsing_of_active_participants(chat_input, limit_active_user)
    elif user_input == "4":
        """Parsing групп / каналов на которые подписан аккаунт"""
        clearing_console_showing_banner()  # Чистим консоль, выводим банер
        parsing_of_groups_to_which_the_account_is_subscribed()
    elif user_input == "5":
        """Очистка списка software_database.db (может понадобится при формировании нового списка для Inviting)"""
        clearing_console_showing_banner()  # Чистим консоль, выводим банер
        cleaning_db(name_database_table="members")
    elif user_input == "0":
        """Вернуться назад"""
        main_menu()  # После отработки функции переходим в начальное меню
    else:
        telegram_parsing_menu()
    main_menu()  # После отработки функции переходим в начальное меню


"""3 работа с контактами"""


def working_tools_contacts() -> None:
    """Работаем с контактами телефонной книги"""
    clearing_console_showing_banner()  # Чистим консоль, выводим банер
    # Выводим таблицу
    table = Table(title="[bold red]Работа с контактами!", box=box.HORIZONTALS)
    column_names(table)  # Формируем колонки таблицы
    # Выводим текст в таблице, нумерация функций начинается с 0
    table.add_row("1", "Формирование списка контактов",
                  "Подготовление списка контактов для работы с ним")
    table.add_row("2", "Показать список контактов",
                  "Отображение списка контактов аккаунта")
    table.add_row("3", "Удаление контактов",
                  "Удаление контактов во всех аккаунтах")
    table.add_row("4", "Добавление контактов",
                  "Добавляем контакты в телефонную книгу")
    table.add_row("0", "Вернуться назад",
                  "Возвращаемся в начальное меню")
    console.print(table, justify="center")  # Отображаем таблицу
    user_input = console.input("[bold red][+] Введите номер: ")
    if user_input == "1":
        """Формирование списка контактов"""
        clearing_console_showing_banner()  # Чистим консоль, выводим банер
        we_record_phone_numbers_in_the_db()
    elif user_input == "2":
        """Отображение списка контактов"""
        clearing_console_showing_banner()  # Чистим консоль, выводим банер
        show_account_contact_list()
    elif user_input == "3":
        """Удаляем все контакты с аккаунтов"""
        clearing_console_showing_banner()  # Чистим консоль, выводим банер
        delete_contact()
    elif user_input == "4":
        """Вносим контакты в телефонную книгу"""
        clearing_console_showing_banner()  # Чистим консоль, выводим банер
        inviting_contact()
    elif user_input == "0":
        """Вернуться назад"""
        main_menu()  # После отработки функции переходим в начальное меню
    else:
        working_tools_contacts()
    main_menu()  # После отработки функции переходим в начальное меню


"""4 подписка и отписка"""


def subscribe_unsubscribe_write_to_file() -> None:
    """Подписка, отписка, запись в файл групп"""
    clearing_console_showing_banner()  # Чистим консоль, выводим банер
    # Выводим таблицу
    table = Table(title="[bold red]Подписываемся / отписываемся!", box=box.HORIZONTALS)
    column_names(table)  # Формируем колонки таблицы
    # Выводим текст в таблице, нумерация функций начинается с 0
    table.add_row("1", "Формирование списка и подписка",
                  "Запись ссылок в поле ввода и запуск подписки")
    table.add_row("2", "Отписываемся",
                  "Отписываемся от групп / каналов чистим аккаунты")
    table.add_row("0", "Вернуться назад",
                  "Возвращаемся в начальное меню")
    console.print(table, justify="center")  # Отображаем таблицу
    user_input = console.input("[bold red][+] Введите номер: ")
    if user_input == "1":
        """Запись групп / каналов в файл, программа записывает данные в существующий файл 
        setting_user/software_database.db """
        clearing_console_showing_banner()  # Чистим консоль, выводим банер
        writing_group_links_to_file()
        subscription_all()
    elif user_input == "2":
        """Отписываемся от групп / каналов (работа с несколькими аккаунтами)"""
        clearing_console_showing_banner()  # Чистим консоль, выводим банер
        unsubscribe_all()
    elif user_input == "0":
        """Вернуться назад"""
        main_menu()  # После отработки функции переходим в начальное меню
    else:
        subscribe_unsubscribe_write_to_file()
    main_menu()  # После отработки функции переходим в начальное меню


"""6 отправка сообщений"""


def sending_messages_to_a_personal_account_chat() -> None:
    """Рассылка сообщений в личку"""
    clearing_console_showing_banner()  # Чистим консоль, выводим банер
    # Выводим таблицу
    table = Table(title="[bold red]Рассылка сообщений в личку!", box=box.HORIZONTALS)
    column_names(table)  # Формируем колонки таблицы
    # Выводим текст в таблице, нумерация функций начинается с 0
    table.add_row("1", "Отправка сообщений в личку parsing список",
                  "Отправка сообщений в личку по parsing списку setting_user/software_database.db")
    table.add_row("2", "Отправка файлов в личку",
                  "Отправка файлов в личку по parsing списку setting_user/software_database.db")
    table.add_row("3", "Рассылка сообщений по чатам",
                  "Рассылка сообщений по чатам, потребуется заранее записать чаты в файл")
    table.add_row("4", "Рассылка сообщений по чатам, по времени",
                  "Рассылка сообщений по чатам по времени, потребуется заранее записать чаты в файл")
    table.add_row("5", "Рассылка файлов по чатам",
                  "Рассылка файлов по чатам, потребуется заранее записать чаты в файл")
    table.add_row("6", "Рассылка сообщений + файлов по чатам",
                  "Рассылка сообщений + файлов по чатам, потребуется заранее записать чаты в файл")
    table.add_row("7", "Формирование списка чатов",
                  "Формирование списка чатов для рассылки сообщений. Откроется txt файл для записи списка "
                  "чатов")
    table.add_row("0", "Вернуться назад",
                  "Возвращаемся в начальное меню")
    console.print(table, justify="center")  # Отображаем таблицу
    user_input = console.input("[bold red][+] Введите номер: ")
    if user_input == "1":
        """Отправка сообщений в личку по parsing списку setting_user/software_database.db"""
        clearing_console_showing_banner()  # Чистим консоль, выводим банер
        we_send_a_message_by_members()
    elif user_input == "2":
        """Отправка файлов в личку по parsing списку setting_user/software_database.db"""
        clearing_console_showing_banner()  # Чистим консоль, выводим банер
        sending_files_to_a_personal_account()
    elif user_input == "3":
        """Рассылка сообщений по чатам"""
        clearing_console_showing_banner()  # Чистим консоль, выводим банер
        message_entry_window()
    elif user_input == "4":
        """Рассылка сообщений по чатам по времени"""
        clearing_console_showing_banner()  # Чистим консоль, выводим банер
        message_entry_window_time()
        mesage_time()
    elif user_input == "5":
        """Рассылка файлов по чатам"""
        clearing_console_showing_banner()  # Чистим консоль, выводим банер
        sending_files_via_chats()
    elif user_input == "6":
        """Рассылка сообщений + файлов по чатам"""
        clearing_console_showing_banner()  # Чистим консоль, выводим банер
        sending_messages_files_via_chats()
    elif user_input == "7":
        """Запись чатов в файл для рассылки сообщений"""
        clearing_console_showing_banner()  # Чистим консоль, выводим банер
        output_the_input_field()
    elif user_input == "0":
        """Вернуться назад"""
        main_menu()  # После отработки функции переходим в начальное меню
    else:
        sending_messages_to_a_personal_account_chat()
    main_menu()  # После отработки функции переходим в начальное меню


"""7 работа с реакциями"""


def working_with_the_reaction() -> None:
    """Работа с реакциями на посты группы или канала"""
    clearing_console_showing_banner()  # Чистим консоль, выводим банер
    # Выводим таблицу
    table = Table(title="[bold red]Работа с реакциями!", box=box.HORIZONTALS)
    column_names(table)  # Формируем колонки таблицы
    # Выводим текст в таблице, нумерация функций начинается с 0
    table.add_row("1", "Ставим реакцию на 1 пост",
                  "Ставим реакции на один пост с группе / канале")
    table.add_row("0", "Вернуться назад",
                  "Возвращаемся в начальное меню")
    console.print(table, justify="center")  # Отображаем таблицу
    user_input = console.input("[bold red][+] Введите номер: ")
    if user_input == "1":
        """Ставим реакции на один пост с группе / канале"""
        clearing_console_showing_banner()  # Чистим консоль, выводим банер
        users_choice_of_reaction()
    elif user_input == "0":
        """Вернуться назад"""
        main_menu()  # После отработки функции переходим в начальное меню
    else:
        working_with_the_reaction()
    main_menu()  # После отработки функции переходим в начальное меню


"""8 Настройки"""


def program_settings() -> None:
    """Настройки программы, запись времени задержки, api_id, api_hash, запись ссылки для inviting"""
    clearing_console_showing_banner()  # Чистим консоль, выводим банер
    table = Table(title="[bold red]Настройки программы!", box=box.HORIZONTALS)  # Выводим таблицу
    column_names(table)  # Формируем колонки таблицы
    # Выводим текст в таблице
    table.add_row("1", "Запись ссылки",
                  "Запись ссылки, для Inviting")
    table.add_row("2", "Запись api_id, api_hash",
                  "Запись api_id, api_hash")
    table.add_row("3", "Время между Inviting / Рассылка сообщений",
                  "Запись времени между приглашениями, (Inviting) / Рассылкой сообщений")
    table.add_row("4", "Смена аккаунтов",
                  "Запись времени между сменой аккаунтов")
    table.add_row("5", "Время между подпиской",
                  "Запись времени между сменой групп при подписке.")
    table.add_row("6", "Запись proxy",
                  "Запись данных для proxy")
    table.add_row("7", "Лимиты на аккаунт",
                  "Установление лимитов на аккаунт")
    table.add_row("0", "Вернуться назад",
                  "Возвращаемся в начальное меню")
    console.print(table, justify="center")  # Отображаем таблицу
    user_input = console.input("[bold red][+] Введите номер: ")
    if user_input == "1":
        """Запись ссылки для inviting (Записываем ссылку на группу, которую будем inviting)"""
        clearing_console_showing_banner()  # Чистим консоль, выводим банер
        print(f"[bold green][!] Давайте запишем ссылку для inviting, ссылка должна быть [bold red]одна! Обратите "
              f"внимание, что программа будет перезапущенна")
        writing_settings_to_a_file(config=writing_link_to_the_group())
        os.system("python main.py")  # После отработки функции возвращаемся в начальное меню
    elif user_input == "2":
        """Запись id, hash в файл"""
        clearing_console_showing_banner()  # Чистим консоль, выводим банер
        print("[bold red][!] Получить api_id, api_hash можно на сайте https://my.telegram.org/auth")
        writing_settings_to_a_file(config=writing_api_id_api_hash())
    if user_input == "3":
        """Время между приглашениями Inviting  / Рассылка сообщений"""
        clearing_console_showing_banner()  # Чистим консоль, выводим банер
        print("[bold red][+] Введите время между Inviting / Рассылка сообщений! C начала меньшее, потом большее. "
              "НАПРИМЕР: 10 20!")
        create_main_window(variable="time_inviting")
    elif user_input == "4":
        """Время между сменой аккаунтов"""
        clearing_console_showing_banner()  # Чистим консоль, выводим банер
        print("[bold red][+] Введите время между сменой аккаунтов в секундах. C начала меньшее, потом большее. "
              "НАПРИМЕР: 10 20!")
        create_main_window(variable="time_changing_accounts")
    elif user_input == "5":
        """Время между подпиской групп"""
        clearing_console_showing_banner()  # Чистим консоль, выводим банер
        print("[bold red][+] Введите время между подпиской на группы / каналы в секундах (между приглашениями) C "
              "начала меньшее, потом большее. НАПРИМЕР: 10 20!")
        create_main_window(variable="time_subscription")
    elif user_input == "6":
        """Запись данных для proxy"""
        creating_the_main_window_for_proxy_data_entry()
        program_settings()
    elif user_input == "7":
        """Запись лимитов на аккаунт"""
        clearing_console_showing_banner()  # Чистим консоль, выводим банер
        writing_settings_to_a_file(config=record_account_limits())
    elif user_input == "0":
        """Вернуться назад"""
        main_menu()  # После отработки функции переходим в начальное меню
    else:
        program_settings()
    main_menu()  # После отработки функции переходим в начальное меню


if __name__ == "__main__":
    try:
        main_menu()
    except Exception as e:
        logger.exception(e)
        print("[bold red][!] Произошла ошибка, для подробного изучения проблемы просмотрите файл log.log")
