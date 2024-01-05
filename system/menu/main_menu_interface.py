from rich import box
from rich.table import Table

from system.actions.actions_with_account.account_verification import *
from system.actions.creating.creating import creating_groups_and_chats
from system.actions.invite.inviting_participants_telegram import *
from system.actions.invite.telegram_invite_scheduler import *
from system.actions.pars.parsing_account_groups_and_channels import *
from system.actions.pars.parsing_group_members import *
from system.actions.reactions.reactions import *
from system.actions.send_mess_chat.chat_dialog_mes import *
from system.actions.send_mess_chat.telegram_chat_dialog import *
from system.actions.sending_messages_telegram.sending_messages_telegram import *
from system.actions.subscription.subscription import *
from system.actions.subscription.unsubscribe import *
from system.auxiliary_functions.auxiliary_functions import *
from system.auxiliary_functions.global_variables import *
from system.setting.setting import *
from system.sqlite_working_tools.sqlite_working_tools import *

logger.add("user_settings/log/log.log", rotation="1 MB", compression="zip")


def main_menu() -> None:  # 1 - Основное меню программы
    """Основное меню программы"""
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
    console.print(table, justify="center")  # Отображаем таблицу
    user_input = console.input("[medium_purple3][+] Введите номер: ")
    if user_input == "1":  # Inviting в группы
        inviting_groups()
    elif user_input == "2":  # Parsing, в новый файл members.db и до записи в файл
        telegram_parsing_menu()
    elif user_input == "3":  # Работаем с контактами телефонной книги
        working_tools_contacts()
    elif user_input == "4":  # Работаем с подпиской, подписка, отписка, запись ссылок в файл
        subscribe_unsubscribe_write_to_file()
    elif user_input == "5":  # Подключение новых аккаунтов, методом ввода нового номера телефона
        clearing_console_showing_banner()  # Чистим консоль, выводим банер
        connecting_new_account()
        main_menu()
    elif user_input == "6":  # Рассылка сообщений по списку members.db
        sending_messages_to_a_personal_account_chat()
    elif user_input == "7":  # Работа с реакциями
        working_with_the_reaction()
    elif user_input == "8":  # Настройки для программы (прописываем ссылку для inviting, api_id, api_hash)
        program_settings()
    elif user_input == "9":  # Проверка аккаунта через спам бот
        clearing_console_showing_banner()  # Чистим консоль, выводим банер
        check_account_for_spam()
    elif user_input == "10":  # Создание групп (чатов)
        clearing_console_showing_banner()  # Чистим консоль, выводим банер
        creating_groups_and_chats()
    else:
        main_menu()  # После отработки функции переходим в начальное меню


def inviting_groups() -> None:  # 1 - Inviting в группы
    """"Inviting в группы"""
    clearing_console_showing_banner()  # Чистим консоль, выводим банер
    table = Table(title=f"[medium_purple3]Inviting {link_group}!", box=box.HORIZONTALS)  # Выводим таблицу
    column_names(table)  # Формируем колонки таблицы
    # Выводим текст в таблице
    table.add_row("1", f"Inviting {link_group}", "Inviting по списку members")
    table.add_row("2", f"Inviting {link_group}, с лимитами", "Inviting по списку members, с лимитами на аккаунт")
    table.add_row("3", f"Inviting {link_group} 1 раз в час", "Inviting по списку members с запуском 1 рав в час")
    table.add_row("4", f"Inviting time {link_group}", "Inviting по списку members (запуск по времени)")
    table.add_row("5", f"Inviting time avery day{link_group}", "Inviting по списку members (запуск по времени каждый день)")
    table.add_row("0", "Вернуться назад", "Возвращаемся в начальное меню")
    console.print(table, justify="center")  # Отображаем таблицу
    user_input = console.input("[medium_purple3][+] Введите номер: ")
    if user_input == "1":  # Inviting по списку software_database.db
        invitation_from_all_accounts_program_body(name_database_table="members")
    elif user_input == "2":  # Inviting по списку software_database.db, с лимитами
        invite_from_multiple_accounts_with_limits(name_database_table="members")
    elif user_input == "3":  # Inviting по времени 1 раз в час
        clearing_console_showing_banner()  # Чистим консоль, выводим банер
        launching_an_invite_once_an_hour()
    elif user_input == "4":  # Inviting по времени
        clearing_console_showing_banner()  # Чистим консоль, выводим банер
        schedule_invite()
    elif user_input == "5":  # Inviting по времени каждый день
        clearing_console_showing_banner()  # Чистим консоль, выводим банер
        launching_an_invite_every_day_at_a_certain_time()
    elif user_input == "0":  # Вернуться назад
        main_menu()  # После отработки функции переходим в начальное меню
    else:
        inviting_groups()  # Если пользователь ввел не правильный номер, то возвращаемся в начало выбора
    main_menu()  # После отработки функции переходим в начальное меню


def telegram_parsing_menu() -> None:  # 2 - Parsing групп и активных участников группы
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
    if user_input == "1":  # Parsing: группы, групп в список software_database.db (группы вводятся в графическое окно)
        clearing_console_showing_banner()  # Чистим консоль, выводим банер
        print("[medium_purple3][+] Введите ссылки чатов которые будем parsing, для вставки в графическое окно "
              "используйте комбинацию клавиш Ctrl + V, обратите внимание что при использование комбинации язык должен "
              "быть переключен на английский")

        db_handler = DatabaseHandler()
        db_handler.cleaning_db(name_database_table="writing_group_links")  # Перед началом parsing очистка таблицы writing_group_links

        writing_group_links_to_file(name_database="writing_group_links")
        parsing_mass_parsing_of_groups()  # Парсинг участников чата

    elif user_input == "2":  # Parsing группы из подписанных
        clearing_console_showing_banner()  # Чистим консоль, выводим банер
        choosing_a_group_from_the_subscribed_ones_for_parsing()
    elif user_input == "3":  # Parsing активных участников группы
        clearing_console_showing_banner()  # Чистим консоль, выводим банер
        chat_input: str = console.input("[medium_purple3][+] Введите ссылку на чат с которого будем собирать активных: ")
        limit_active_user: int = console.input("[medium_purple3][+] Введите количество сообщений которые будем parsing: ")
        parsing_of_active_participants(chat_input, limit_active_user)
    elif user_input == "4":  # Parsing групп / каналов на которые подписан аккаунт
        clearing_console_showing_banner()  # Чистим консоль, выводим банер
        parsing_of_groups_to_which_the_account_is_subscribed()
    elif user_input == "5":  # Очистка списка software_database.db
        clearing_console_showing_banner()  # Чистим консоль, выводим банер
        db_handler = DatabaseHandler()
        db_handler.cleaning_db(name_database_table="members")
    elif user_input == "6":  # Формирование списка
        print("[medium_purple3][+] Введите username, для вставки в графическое окно "
              "используйте комбинацию клавиш Ctrl + V, обратите внимание что при использование комбинации язык должен "
              "быть переключен на английский")
        clearing_console_showing_banner()  # Чистим консоль, выводим банер
        writing_members()
    elif user_input == "0":  # Вернуться назад
        main_menu()  # После отработки функции переходим в начальное меню
    else:
        telegram_parsing_menu()
    main_menu()  # После отработки функции переходим в начальное меню


def working_tools_contacts() -> None:  # 3 - Работаем с контактами телефонной книги
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
    if user_input == "1":  # Формирование списка контактов
        clearing_console_showing_banner()  # Чистим консоль, выводим банер
        we_record_phone_numbers_in_the_db()
    elif user_input == "2":  # Отображение списка контактов
        clearing_console_showing_banner()  # Чистим консоль, выводим банер
        show_account_contact_list()
    elif user_input == "3":  # Удаляем все контакты с аккаунтов
        clearing_console_showing_banner()  # Чистим консоль, выводим банер
        delete_contact()
    elif user_input == "4":  # Вносим контакты в телефонную книгу
        clearing_console_showing_banner()  # Чистим консоль, выводим банер
        inviting_contact()
    elif user_input == "0":  # Вернуться назад
        main_menu()  # После отработки функции переходим в начальное меню
    else:
        working_tools_contacts()
    main_menu()  # После отработки функции переходим в начальное меню


def subscribe_unsubscribe_write_to_file() -> None:  # 4 - Подписка, отписка, запись в файл групп
    """Подписка, отписка, запись в файл групп"""
    clearing_console_showing_banner()  # Чистим консоль, выводим банер
    table = Table(title="[medium_purple3]Подписываемся / отписываемся!", box=box.HORIZONTALS)  # Выводим таблицу
    column_names(table)  # Формируем колонки таблицы
    # Выводим текст в таблице
    table.add_row("1", "Формирование списка и подписка", "Запись ссылок в поле ввода и запуск подписки")
    table.add_row("2", "Отписываемся", "Отписываемся от групп / каналов чистим аккаунты")
    table.add_row("0", "Вернуться назад", "Возвращаемся в начальное меню")
    console.print(table, justify="center")  # Отображаем таблицу
    user_input = console.input("[medium_purple3][+] Введите номер: ")
    if user_input == "1":  # Запись: групп, каналов в файл, данные записываются в файл user_settings/software_database.db
        clearing_console_showing_banner()  # Чистим консоль, выводим банер
        print("[medium_purple3][+] Введите ссылки чатов на которые нужно подписаться, для вставки в графическое окно "
              "используйте комбинацию клавиш Ctrl + V, обратите внимание что при использование комбинации язык должен "
              "быть переключен на английский")
        name_database = "writing_group_links"
        writing_group_links_to_file(name_database)
        subscription_all()
    elif user_input == "2":  # Отписываемся от групп / каналов (работа с несколькими аккаунтами)
        clearing_console_showing_banner()  # Чистим консоль, выводим банер
        unsubscribe_all()
    elif user_input == "0":  # Вернуться назад
        main_menu()  # После отработки функции переходим в начальное меню
    else:
        subscribe_unsubscribe_write_to_file()
    main_menu()  # После отработки функции переходим в начальное меню


def sending_messages_to_a_personal_account_chat() -> None:  # 6 - Рассылка сообщений в личку
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
    table.add_row("7", "Формирование списка чатов", "Формирование списка чатов для рассылки сообщений по чатам")
    table.add_row("8", "Отправка сообщений в личку (с лимитами)", "Отправка сообщений в личку по parsing списку (с лимитами)")
    table.add_row("9", "Отправка файлов в личку (с лимитами)", "Отправка файлов в личку по parsing списку (с лимитами)")
    table.add_row("0", "Вернуться назад", "Возвращаемся в начальное меню")
    console.print(table, justify="center")  # Отображаем таблицу
    user_input = console.input("[medium_purple3][+] Введите номер: ")
    clearing_console_showing_banner()  # Чистим консоль, выводим банер
    if user_input == "1":  # Отправка сообщений в личку по parsing списку user_settings/software_database.db
        we_send_a_message_by_members(limits=None)
    elif user_input == "2":  # Отправка файлов в личку по parsing списку user_settings/software_database.db
        sending_files_to_a_personal_account(limits=None)
    elif user_input == "3":  # Рассылка сообщений по чатам
        message_entry_window()
    elif user_input == "4":  # Рассылка сообщений по чатам по времени
        message_entry_window_time()
        message_time()
    elif user_input == "5":  # Рассылка файлов по чатам
        sending_files_via_chats()
    elif user_input == "6":  # Рассылка сообщений + файлов по чатам
        sending_messages_files_via_chats()
    elif user_input == "7":  # Запись чатов в файл для рассылки сообщений
        output_the_input_field()
    elif user_input == "8":  # Отправка сообщений в личку (с лимитами)
        we_send_a_message_by_members(limits=limits)
    elif user_input == "9":  # Отправка файлов в личку (с лимитами)
        sending_files_to_a_personal_account(limits=limits)
    elif user_input == "0":  # Вернуться назад
        main_menu()  # После отработки функции переходим в начальное меню
    else:
        sending_messages_to_a_personal_account_chat()
    main_menu()  # После отработки функции переходим в начальное меню


def working_with_the_reaction() -> None:  # 7 - Работа с реакциями на посты группы или канала
    """Работа с реакциями на посты группы или канала"""
    clearing_console_showing_banner()  # Чистим консоль, выводим банер
    table = Table(title="[medium_purple3]Работа с реакциями / постами!", box=box.HORIZONTALS)  # Выводим таблицу
    column_names(table)  # Формируем колонки таблицы
    # Выводим текст в таблице
    table.add_row("1", "Ставим реакцию на 1 пост", "Ставим реакции на один пост с группе / канале")
    table.add_row("2", "Накручиваем просмотры постов", "Накручиваем просмотры постов канале")
    table.add_row("0", "Вернуться назад", "Возвращаемся в начальное меню")
    console.print(table, justify="center")  # Отображаем таблицу
    user_input = console.input("[medium_purple3][+] Введите номер: ")
    if user_input == "1":  # Ставим реакции на один пост в группе / канале
        clearing_console_showing_banner()  # Чистим консоль, выводим банер
        users_choice_of_reaction()
    elif user_input == "2":  # Накручиваем просмотры постов
        clearing_console_showing_banner()  # Чистим консоль, выводим банер
        viewing_posts()
    elif user_input == "0":  # Вернуться назад
        main_menu()  # После отработки функции переходим в начальное меню
    else:
        working_with_the_reaction()
    main_menu()  # После отработки функции переходим в начальное меню


def program_settings() -> None:  # 8 - Настройки программы, запись времени, api_id, api_hash, запись ссылки для inviting
    """Настройки программы, запись времени задержки, api_id, api_hash, запись ссылки для inviting"""
    clearing_console_showing_banner()  # Чистим консоль, выводим банер
    table = Table(title="[medium_purple3]Настройки программы!", box=box.HORIZONTALS)  # Выводим таблицу
    column_names(table)  # Формируем колонки таблицы
    # Выводим текст в таблице
    table.add_row("1", "Запись ссылки", "Запись ссылки, для Inviting")
    table.add_row("2", "Запись api_id, api_hash", "Запись api_id, api_hash")
    table.add_row("3", "Время между Inviting, рассылка сообщений", "Запись времени между: Inviting, рассылка сообщений")
    table.add_row("4", "Смена аккаунтов", "Запись времени между сменой аккаунтов")
    table.add_row("5", "Время между подпиской", "Запись времени между сменой групп при подписке.")
    table.add_row("6", "Запись proxy", "Запись данных для proxy")
    table.add_row("7", "Лимиты на аккаунт", "Установление лимитов на аккаунт")
    table.add_row("8", "Смена типа устройства", "Запись данных для смены типа устройства")
    table.add_row("9", "Запись времени", "Запись времени для Inviting один раз в сутки")
    table.add_row("0", "Вернуться назад", "Возвращаемся в начальное меню")
    console.print(table, justify="center")  # Отображаем таблицу
    user_input = console.input("[medium_purple3][+] Введите номер: ")
    if user_input == "1":  # Запись ссылки для inviting (Записываем ссылку на группу, которую будем inviting)
        clearing_console_showing_banner()  # Чистим консоль, выводим банер
        print("[magenta][!] Давайте запишем ссылку для inviting, ссылка должна быть [medium_purple3]одна! Обратите "
              "внимание, что программа будет заново запущена")
        writing_settings_to_a_file(config=writing_link_to_the_group())
        os.system("python main.py")  # После отработки функции возвращаемся в начальное меню
    elif user_input == "2":  # Запись id, hash в файл
        clearing_console_showing_banner()  # Чистим консоль, выводим банер
        print("[medium_purple3][!] Получить api_id, api_hash можно на сайте https://my.telegram.org/auth")
        writing_settings_to_a_file(config=writing_api_id_api_hash())
    if user_input == "3":  # Время между приглашениями Inviting / Рассылка сообщений
        clearing_console_showing_banner()  # Чистим консоль, выводим банер
        print("[medium_purple3][+] Введите время между Inviting / Рассылка сообщений! C начала меньшее, потом большее. "
              "НАПРИМЕР: 10 20!")
        create_main_window(variable="time_inviting")
    elif user_input == "4":  # Время между сменой аккаунтов
        clearing_console_showing_banner()  # Чистим консоль, выводим банер
        print("[medium_purple3][+] Введите время между сменой аккаунтов в секундах. C начала меньшее, потом большее. "
              "НАПРИМЕР: 10 20!")
        create_main_window(variable="time_changing_accounts")
    elif user_input == "5":  # Время между подпиской групп
        clearing_console_showing_banner()  # Чистим консоль, выводим банер
        print("[medium_purple3][+] Введите время между подпиской на группы / каналы в секундах (между приглашениями) C "
              "начала меньшее, потом большее. НАПРИМЕР: 10 20!")
        create_main_window(variable="time_subscription")
    elif user_input == "6":  # Запись данных для proxy
        creating_the_main_window_for_proxy_data_entry()
        program_settings()
    elif user_input == "7":  # Запись лимитов на аккаунт
        clearing_console_showing_banner()  # Чистим консоль, выводим банер
        writing_settings_to_a_file(config=record_account_limits())
    elif user_input == "8":  # Запись типа устройства
        clearing_console_showing_banner()  # Чистим консоль, выводим банер
        writing_settings_to_a_file(config=record_device_type())
    elif user_input == "9":  # Запись времени для запуска inviting в определенное время
        try:
            clearing_console_showing_banner()  # Чистим консоль, выводим банер
            recording_the_time_to_launch_an_invite_every_day()
        except Exception as e:
            logger.exception(e)
    elif user_input == "0":  # Вернуться назад
        main_menu()  # После отработки функции переходим в начальное меню
    else:
        program_settings()
    main_menu()  # После отработки функции переходим в начальное меню


if __name__ == "__main__":
    try:
        main_menu()
    except Exception as e:
        logger.exception(e)
        print("[medium_purple3][!] Произошла ошибка, для подробного изучения проблемы просмотрите файл log.log")
