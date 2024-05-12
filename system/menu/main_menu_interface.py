from rich import box
from rich.table import Table

from system.account_actions.checking_spam.account_verification import *
from system.account_actions.creating.account_registration import *
from system.account_actions.creating.creating import *
from system.account_actions.invitation.inviting_participants_telegram import *
from system.account_actions.invitation.telegram_invite_scheduler import *
from system.account_actions.parsing.parsing_account_groups_and_channels import *
from system.account_actions.parsing.parsing_group_members import *
from system.account_actions.reactions.reactions import *
from system.account_actions.sending_messages.chat_dialog_mes import *
from system.account_actions.sending_messages.sending_messages_telegram import *
from system.account_actions.sending_messages.telegram_chat_dialog import *
from system.account_actions.subscription.subscription import *
from system.account_actions.unsubscribe.unsubscribe import *
from system.auxiliary_functions.auxiliary_functions import *
from system.auxiliary_functions.global_variables import *
from system.menu.app_gui import *
from system.setting.setting import *
from system.sqlite_working_tools.sqlite_working_tools import *


def main_menu() -> None:  # 1 - Основное меню программы
    """Основное меню программы"""
    db_handler = DatabaseHandler()  # Создаем объект для работы с БД
    clear_console_and_display_banner()  # Чистим консоль, выводим банер
    table = Table(title="[medium_purple3]Основные функции программы!", box=box.HORIZONTALS)  # Выводим таблицу
    column_names(table)  # Формируем колонки таблицы
    # Выводим текст в таблице
    table.add_row("1", f"Инвайтинг {link_group}")
    table.add_row("2", "Парсинг")
    table.add_row("3", "Работа с контактами")
    table.add_row("4", "Подписка, отписка")
    table.add_row("5", "Подключение аккаунтов")
    table.add_row("6", "Рассылка сообщений")
    table.add_row("7", "Работа с реакциями")
    table.add_row("8", "Настройки")
    table.add_row("9", "Проверка аккаунтов")
    table.add_row("10", "Создание групп (чатов)")
    table.add_row("11", "Редактирование BIO")
    console.print(table, justify="center")  # Отображаем таблицу
    user_input = console.input("[medium_purple3][+] Введите номер: ")
    clear_console_and_display_banner()  # Чистим консоль, выводим банер
    if user_input == "1":  # Инвайтинг
        inviting_groups(db_handler)
    elif user_input == "2":  # Парсинг
        telegram_parsing_menu(db_handler)
    elif user_input == "3":  # Работаем с контактами телефонной книги
        working_tools_contacts(db_handler)
    elif user_input == "4":  # Работаем с подпиской, подписка, отписка, запись ссылок в файл
        subscribe_unsubscribe_write_to_file(db_handler)
    elif user_input == "5":  # Подключение новых аккаунтов, методом ввода нового номера телефона
        connecting_new_account(db_handler)
        main_menu()
    elif user_input == "6":  # Рассылка сообщений по списку members.db
        personal_account_chat_messages_distribution(db_handler)
    elif user_input == "7":  # Работа с реакциями
        working_with_the_reaction(db_handler)
    elif user_input == "8":  # Настройки для программы (прописываем ссылку для inviting, api_id, api_hash)
        program_settings(db_handler)
    elif user_input == "9":  # Проверка аккаунта через спам бот
        check_account_for_spam(db_handler)
    elif user_input == "10":  # Создание групп (чатов)
        creating_groups_and_chats(db_handler)
    elif user_input == '11':
        working_with_bio()
    else:
        main_menu()  # После отработки функции переходим в начальное меню


def inviting_groups(db_handler) -> None:  # 1 - Инвайтинг в группы
    """"Inviting в группы"""
    clear_console_and_display_banner()  # Чистим консоль, выводим банер
    table = Table(title=f"[medium_purple3]Инвайтинг {link_group}!", box=box.HORIZONTALS)  # Выводим таблицу
    column_names_2(table)  # Формируем колонки таблицы
    # Выводим текст в таблице
    table.add_row("1", "Инвайтинг без лимитов")
    table.add_row("2", "Инвайтинг с лимитами")
    table.add_row("3", "Инвайтинг 1 раз в час")
    table.add_row("4", "Инвайтинг в определенное время")
    table.add_row("5", "Инвайтинг каждый день")
    table.add_row("0", "В начальное меню")
    console.print(table, justify="left")  # Отображаем таблицу
    user_input = console.input("[medium_purple3][+] Введите номер функции: ")
    clear_console_and_display_banner()  # Чистим консоль, выводим банер
    if user_input == "1":  # Инвайтинг без лимитов
        invitation_from_all_accounts_program_body(name_database_table="members", db_handler=db_handler)
    elif user_input == "2":  # Инвайтинг с лимитами
        invite_from_multiple_accounts_with_limits(name_database_table="members", db_handler=db_handler)
    elif user_input == "3":  # Инвайтинг 1 раз в час
        launching_an_invite_once_an_hour()
    elif user_input == "4":  # Инвайтинг в определенное время
        schedule_invite()
    elif user_input == "5":  # Инвайтинг каждый день
        launching_invite_every_day_certain_time()
    elif user_input == "0":  # Вернуться назад
        main_menu()  # После отработки функции переходим в начальное меню
    else:
        inviting_groups(db_handler)  # Если пользователь ввел не правильный номер, то возвращаемся в начало выбора
    main_menu()  # После отработки функции переходим в начальное меню


def telegram_parsing_menu(db_handler) -> None:  # 2 - Parsing групп и активных участников группы
    """Parsing групп и активных участников группы"""
    clear_console_and_display_banner()  # Чистим консоль, выводим банер
    table = Table(title="[medium_purple3]Parsing участников групп!", box=box.HORIZONTALS)  # Выводим таблицу
    column_names_3(table)  # Формируем колонки таблицы
    # Выводим текст в таблице
    table.add_row("1", "Парсинг одной группы / групп")
    table.add_row("2", "Парсинг выбранной группы из подписанных пользователем")
    table.add_row("3", "Парсинг активных участников группы")
    table.add_row("4", "Парсинг групп / каналов на которые подписан аккаунт")
    table.add_row("5", "Очистка списка от ранее спарсенных данных")
    table.add_row("6", "Формирование списка username")
    table.add_row("0", "В начальное меню")
    console.print(table, justify="left")  # Отображаем таблицу
    user_input = console.input("[medium_purple3][+] Введите номер функции: ")
    clear_console_and_display_banner()  # Чистим консоль, выводим банер
    if user_input == "1":  # Парсинг одной группы / групп
        parsing_mass_parsing_of_groups(db_handler)  # Парсинг участников чата
    elif user_input == "2":  # Парсинг выбранной группы из подписанных пользователем
        choosing_a_group_from_the_subscribed_ones_for_parsing(db_handler)
    elif user_input == "3":  # Парсинг активных участников группы
        chat_input: str = console.input(
            "[medium_purple3][+] Введите ссылку на чат с которого будем собирать активных: ")
        limit_active_user: int = console.input(
            "[medium_purple3][+] Введите количество сообщений которые будем parsing: ")
        parsing_of_active_participants(chat_input, limit_active_user, db_handler)
    elif user_input == "4":  # Парсинг групп / каналов на которые подписан аккаунт
        parsing_groups_which_account_subscribed(db_handler)
    elif user_input == "5":  # Очистка списка от ранее спарсенных данных
        db_handler.cleaning_db(name_database_table="members")
    elif user_input == "6":  # Формирование списка username
        writing_members(db_handler)
    elif user_input == "0":  # Вернуться назад
        main_menu()  # После отработки функции переходим в начальное меню
    else:
        telegram_parsing_menu(db_handler)


def working_tools_contacts(db_handler) -> None:  # 3 - Работаем с контактами телефонной книги
    """Работаем с контактами телефонной книги"""
    clear_console_and_display_banner()  # Чистим консоль, выводим банер
    table = Table(title="[medium_purple3]Работа с контактами!", box=box.HORIZONTALS)  # Выводим таблицу
    column_names(table)  # Формируем колонки таблицы
    # Выводим текст в таблице
    table.add_row("1", "Формирование списка контактов")
    table.add_row("2", "Показать список контактов")
    table.add_row("3", "Удаление контактов")
    table.add_row("4", "Добавление контактов")
    table.add_row("0", "Вернуться назад")
    console.print(table, justify="center")  # Отображаем таблицу
    user_input = console.input("[medium_purple3][+] Введите номер: ")
    clear_console_and_display_banner()  # Чистим консоль, выводим банер
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
    clear_console_and_display_banner()  # Чистим консоль, выводим банер
    table = Table(title="[medium_purple3]Подписываемся / отписываемся!", box=box.HORIZONTALS)  # Выводим таблицу
    column_names(table)  # Формируем колонки таблицы
    # Выводим текст в таблице
    table.add_row("1", "Подписка")
    table.add_row("2", "Отписываемся")
    table.add_row("0", "Вернуться назад")
    console.print(table, justify="center")  # Отображаем таблицу
    user_input = console.input("[medium_purple3][+] Введите номер: ")
    clear_console_and_display_banner()  # Чистим консоль, выводим банер
    if user_input == "1":  # Запись: групп, каналов в файл, в файл user_settings/software_database.db
        subscription_all(db_handler)
    elif user_input == "2":  # Отписываемся от групп / каналов (работа с несколькими аккаунтами)
        unsubscribe_all(db_handler)
    elif user_input == "0":  # Вернуться назад
        main_menu()  # После отработки функции переходим в начальное меню
    else:
        subscribe_unsubscribe_write_to_file(db_handler)
    main_menu()  # После отработки функции переходим в начальное меню


def personal_account_chat_messages_distribution(db_handler) -> None:  # 6 - Рассылка сообщений в личку
    """Рассылка сообщений в личку"""
    clear_console_and_display_banner()  # Чистим консоль, выводим банер
    table = Table(title="[medium_purple3]Рассылка сообщений в личку!", box=box.HORIZONTALS)  # Выводим таблицу
    column_names(table)  # Формируем колонки таблицы
    # Выводим текст в таблице
    table.add_row("1", "Отправка сообщений в личку")
    table.add_row("2", "Отправка файлов в личку")
    table.add_row("3", "Рассылка сообщений по чатам")
    table.add_row("4", "Рассылка сообщений по чатам с автоответчиком")
    table.add_row("5", "Рассылка файлов по чатам")
    table.add_row("6", "Рассылка сообщений + файлов по чатам")
    table.add_row("7", "Отправка сообщений в личку (с лимитами)")
    table.add_row("8", "Отправка файлов в личку (с лимитами)")
    table.add_row("0", "В начальное меню")
    console.print(table, justify="center")  # Отображаем таблицу
    user_input = console.input("[medium_purple3][+] Введите номер: ")
    clear_console_and_display_banner()  # Чистим консоль, выводим банер
    if user_input == "1":  # Отправка сообщений в личку по parsing списку user_settings/software_database.db
        send_message_from_all_accounts(limits=None, db_handler=db_handler)
    elif user_input == "2":  # Отправка файлов в личку по parsing списку user_settings/software_database.db
        send_files_to_personal_chats(limits=None, db_handler=db_handler)
    elif user_input == "3":  # Рассылка сообщений по чатам
        entities = find_files(directory_path="user_settings/message", extension="json")
        logger.info(entities)
        sending_messages_via_chats_times(entities, db_handler)
    elif user_input == "4":  # ✅ Рассылка сообщений по чатам по времени
        mains(DatabaseHandler())
    elif user_input == "5":  # Рассылка файлов по чатам
        sending_files_via_chats(db_handler)
    elif user_input == "6":  # Рассылка сообщений + файлов по чатам
        sending_messages_files_via_chats()
    elif user_input == "7":  # Отправка сообщений в личку (с лимитами)
        send_message_from_all_accounts(limits=limits_message, db_handler=db_handler)
    elif user_input == "8":  # Отправка файлов в личку (с лимитами)
        send_files_to_personal_chats(limits=limits_message, db_handler=db_handler)
    elif user_input == "0":  # Вернуться назад
        main_menu()  # После отработки функции переходим в начальное меню
    else:
        personal_account_chat_messages_distribution(db_handler)


def working_with_the_reaction(db_handler) -> None:  # 7 - Работа с реакциями на посты группы или канала
    """Работа с реакциями на посты группы или канала"""
    clear_console_and_display_banner()  # Чистим консоль, выводим банер
    table = Table(title="[medium_purple3]Работа с реакциями / постами!", box=box.HORIZONTALS)  # Выводим таблицу
    column_names(table)  # Формируем колонки таблицы
    # Выводим текст в таблице
    table.add_row("1", "Ставим реакцию на 1 пост")
    table.add_row("2", "Накручиваем просмотры постов")
    table.add_row("3", "Автоматическое выставление реакций")
    table.add_row("0", "Вернуться назад")
    console.print(table, justify="center")  # Отображаем таблицу
    user_input = console.input("[medium_purple3][+] Введите номер: ")
    clear_console_and_display_banner()  # Чистим консоль, выводим банер
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


def program_settings(db_handler) -> None:  # 8 - Настройки программы, запись времени, api_id, api_hash, запись ссылки для inviting
    """Настройки программы, запись времени задержки, api_id, api_hash, запись ссылки для inviting"""
    clear_console_and_display_banner()  # Чистим консоль, выводим банер
    table = Table(title="[medium_purple3]Настройки программы!", box=box.HORIZONTALS)  # Выводим таблицу
    column_names(table)  # Формируем колонки таблицы
    # Выводим текст в таблице
    table.add_row("1", "Запись ссылки")
    table.add_row("2", "Запись api_id, api_hash")
    table.add_row("3", "Время между Inviting, рассылка сообщений")
    table.add_row("4", "Смена аккаунтов")
    table.add_row("5", "Время между подпиской")
    table.add_row("6", "Запись proxy")
    table.add_row("7", "Лимиты на аккаунт")
    table.add_row("8", "Смена типа устройства")
    table.add_row("9", "Запись времени")
    table.add_row("10", "Лимиты на сообщения")
    table.add_row("11", "Выбор реакций")
    table.add_row("12", "Запись ссылки для реакций")
    table.add_row("13", "Запись количества аккаунтов для реакций")
    table.add_row("14", "Запись сообщений")
    table.add_row("15", "Запись времени между сообщениями")
    table.add_row("16", "Формирование списка чатов / каналов")
    table.add_row("17", "Запись имени аккаунта")
    table.add_row("0", "В начальное меню")
    console.print(table, justify="center")  # Отображаем таблицу
    user_input = console.input("[medium_purple3][+] Введите номер: ")
    clear_console_and_display_banner()  # Чистим консоль, выводим банер
    if user_input == "1":  # Запись ссылки для inviting (Записываем ссылку на группу, которую будем inviting)
        print("[magenta][!] Давайте запишем ссылку для inviting, ссылка должна быть [medium_purple3]одна! Обратите "
              "внимание, что программа будет заново запущена")
        writing_settings_to_a_file(config=writing_link_to_the_group())
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
    elif user_input == "17":
        record_account_name_newsletter()
    elif user_input == "0":  # Вернуться назад
        main_menu()  # После отработки функции переходим в начальное меню
    else:
        program_settings(db_handler)
    os.system("python main.py")  # После отработки функции возвращаемся в начальное меню


def working_with_bio() -> None:  # 11 - Работа с био аккаунта Telegram
    """Работа с реакциями на посты группы или канала"""
    clear_console_and_display_banner()  # Чистим консоль, выводим банер
    table = Table(title="[medium_purple3]Редактирование BIO!", box=box.HORIZONTALS)  # Выводим таблицу
    column_names(table)  # Формируем колонки таблицы
    # Выводим текст в таблице
    table.add_row("1", "Изменение username")
    table.add_row("2", "Изменение фото")
    table.add_row("3", "Изменение описания")
    table.add_row("4", "Изменение имени")
    table.add_row("5", "Изменение фамилии")
    table.add_row("0", "Вернуться назад")
    console.print(table, justify="center")  # Отображаем таблицу
    user_input = console.input("[medium_purple3][+] Введите номер: ")
    clear_console_and_display_banner()  # Чистим консоль, выводим банер
    if user_input == "1":
        aaa = AccountRIO(DatabaseHandler())  # Передаем db_handler как аргумент
        aaa.change_username_profile(DatabaseHandler())
    elif user_input == "2":
        aaa = AccountRIO(DatabaseHandler())  # Передаем db_handler как аргумент
        aaa.change_photo_profile(DatabaseHandler())
    elif user_input == "3":
        aaa = AccountRIO(DatabaseHandler())  # Передаем db_handler как аргумент
        aaa.change_bio_profile(DatabaseHandler())
    elif user_input == "4":
        aaa = AccountRIO(DatabaseHandler())  # Передаем db_handler как аргумент
        aaa.change_name_profile(DatabaseHandler())
    elif user_input == "5":
        aaa = AccountRIO(DatabaseHandler())  # Передаем db_handler как аргумент
        aaa.change_last_name_profile(DatabaseHandler())
    elif user_input == "0":  # Вернуться назад
        main_menu()  # После отработки функции переходим в начальное меню
    else:
        working_with_bio()
    main_menu()  # После отработки функции переходим в начальное меню


if __name__ == "__main__":
    try:
        main_menu()
    except Exception as e:
        logger.exception(e)
        print("[medium_purple3][!] Произошла ошибка, для подробного изучения проблемы просмотрите файл log.log")
