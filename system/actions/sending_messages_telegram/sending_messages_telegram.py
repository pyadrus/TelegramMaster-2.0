import sys
from tkinter import *

from rich import print
from telethon.errors import *

from system.actions.invite.inviting_participants_telegram import record_inviting_results
from system.auxiliary_functions.auxiliary_functions import record_and_interrupt
from system.auxiliary_functions.global_variables import console
from system.menu.gui_program import program_window
from system.notification.notification import app_notifications
from system.sqlite_working_tools.sqlite_working_tools import open_the_db_and_read_the_data
from system.telegram_actions.telegram_actions import connect_to_telegram_account_and_output_name
from system.telegram_actions.telegram_actions import we_get_username_user_id_access_hash


def we_send_a_message_by_members() -> None:
    """Рассылка сообщений по списку software_database.db"""

    # Предупреждаем пользователя о вводе ссылок в графическое окно программы
    print("[bold red][+] Введите текст который будем рассылать в личку, для вставки в графическое окно готового "
          "текста используйте комбинацию клавиш Ctrl + V, обратите внимание что при использование комбинации язык "
          "должен быть переключен на английский")

    root, text = program_window()

    def output_values_from_the_input_field() -> None:
        """Выводим значения с поля ввода (то что ввел пользователь)"""
        message_text = text.get("1.0", 'end-1c')
        closing_the_input_field()
        we_send_a_message_from_all_accounts(message_text)

    def closing_the_input_field() -> None:
        """Закрываем программу"""
        root.destroy()

    # Создаем кнопку по нажатии которой выведется поле ввода. После ввода чатов данные запишутся во временный файл
    but = Button(root, text="Готово", command=output_values_from_the_input_field)
    but.pack()
    root.mainloop()  # Запускаем программу


def sending_files_to_a_personal_account() -> None:
    """Отправка файлов в личку"""
    # Просим пользователя ввести расширение сообщения
    link_to_the_file: str = console.input("[bold red][+] Введите название файла с папки setting_user/files_to_send: ")
    event: str = f"Отправляем сообщение"
    # Выводим уведомление, если операционная система windows 7, то выводим уведомление в консоль
    app_notifications(notification_text=event)
    # Открываем базу данных для работы с аккаунтами setting_user/software_database.db
    records: list = open_the_db_and_read_the_data(name_database_table="config")
    for row in records:
        # Подключение к Telegram и вывод имя аккаунта в консоль / терминал
        client, phone = connect_to_telegram_account_and_output_name(row)
        try:
            # Открываем parsing список setting_user/software_database.db для inviting в группу
            records: list = open_the_db_and_read_the_data(name_database_table="members")
            # Количество аккаунтов на данный момент в работе
            print(f"[bold red]Всего username: {len(records)}")
            for rows in records:
                username, user = we_get_username_user_id_access_hash(rows)
                print(f"[bold green][!] Отправляем сообщение: {username}")
                try:
                    user_to_add = client.get_input_entity(username)
                    client.send_file(user_to_add, f"setting_user/files_to_send/{link_to_the_file}")
                    # Записываем данные в базу данных, чистим список кого добавляли или писали сообщение
                    actions = "Сообщение отправлено"
                    record_inviting_results(user, phone, f"username : {username}", event, actions)
                except FloodWaitError as e:
                    actions = f'Flood! wait for {e.seconds} seconds'
                    record_and_interrupt(actions, phone, f"username : {username}", event)
                    break  # Прерываем работу и меняем аккаунт
                except PeerFloodError:
                    actions = "Предупреждение о Flood от telegram."
                    record_and_interrupt(actions, phone, f"username : {username}", event)
                    break  # Прерываем работу и меняем аккаунт
                except UserNotMutualContactError:
                    actions = "User не является взаимным контактом."
                    record_inviting_results(username, phone, f"username : {username}", event, actions)
                except (UserIdInvalidError, UsernameNotOccupiedError, ValueError, UsernameInvalidError):
                    actions = "Не корректное имя user"
                    record_inviting_results(username, phone, f"username : {username}", event, actions)
                except ChatWriteForbiddenError:
                    actions = "Вам запрещено писать в супергруппу / канал."
                    record_and_interrupt(actions, phone, f"username : {username}", event)
                    break  # Прерываем работу и меняем аккаунт
                except (TypeError, UnboundLocalError):
                    continue  # Записываем ошибку в software_database.db и продолжаем работу
        except KeyError:
            sys.exit(1)
    # Выводим уведомление, если операционная система windows 7, то выводим уведомление в консоль
    app_notifications(notification_text="Работа окончена!")


def we_send_a_message_from_all_accounts(message_text) -> None:
    """Отправка сообщений в личку"""
    event: str = f"Отправляем сообщение в личку пользователям Telegram"
    # Выводим уведомление, если операционная система windows 7, то выводим уведомление в консоль
    app_notifications(notification_text=event)
    # Открываем базу данных для работы с аккаунтами setting_user/software_database.db
    records: list = open_the_db_and_read_the_data(name_database_table="config")
    for row in records:
        # Подключение к Telegram и вывод имя аккаунта в консоль / терминал
        client, phone = connect_to_telegram_account_and_output_name(row)
        try:
            # Открываем parsing список setting_user/software_database.db для inviting в группу
            records: list = open_the_db_and_read_the_data(name_database_table="members")
            # Количество аккаунтов на данный момент в работе
            print(f"[bold red]Всего username: {len(records)}")
            for rows in records:
                username, user = we_get_username_user_id_access_hash(rows)
                print(f"[bold green][!] Отправляем сообщение: {username}")
                try:
                    user_to_add = client.get_input_entity(username)
                    client.send_message(user_to_add, message_text.format(username))
                    # Записываем данные в log файл, чистим список кого добавляли или писали сообщение
                    actions = "Сообщение отправлено"
                    record_inviting_results(user, phone, f"username : {username}", event, actions)
                except FloodWaitError as e:
                    actions = f'Flood! wait for {e.seconds} seconds'
                    record_and_interrupt(actions, phone, f"username : {username}", event)
                    break  # Прерываем работу и меняем аккаунт
                except PeerFloodError:
                    actions = "Предупреждение о Flood от telegram."
                    record_and_interrupt(actions, phone, f"username : {username}", event)
                    break  # Прерываем работу и меняем аккаунт
                except UserNotMutualContactError:
                    actions = "User не является взаимным контактом."
                    record_inviting_results(username, phone, f"username : {username}", event, actions)
                except (UserIdInvalidError, UsernameNotOccupiedError, ValueError, UsernameInvalidError):
                    actions = "Не корректное имя user"
                    record_inviting_results(username, phone, f"username : {username}", event, actions)
                except ChatWriteForbiddenError:
                    actions = "Вам запрещено писать в супергруппу / канал."
                    record_and_interrupt(actions, phone, f"username : {username}", event)
                    break  # Прерываем работу и меняем аккаунт
                except (TypeError, UnboundLocalError):
                    continue  # Записываем ошибку в software_database.db и продолжаем работу
        except KeyError:
            sys.exit(1)
    # Выводим уведомление, если операционная система windows 7, то выводим уведомление в консоль
    app_notifications(notification_text="Работа окончена!")


if __name__ == "__main__":
    we_send_a_message_by_members()
