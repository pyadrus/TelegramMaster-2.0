import random
import time

from rich import print
from telethon import functions
from telethon import types

from system.auxiliary_functions.global_variables import console
from system.error.telegram_errors import handle_exceptions_pars
from system.sqlite_working_tools.sqlite_working_tools import delete_row_db
from system.sqlite_working_tools.sqlite_working_tools import open_the_db_and_read_the_data
from system.sqlite_working_tools.sqlite_working_tools import writing_data_to_the_db
from system.telegram_actions.telegram_actions import connect_to_telegram_account_and_output_name

creating_a_table = "CREATE TABLE IF NOT EXISTS members_contacts(username, id, access_hash, name, user_phone,online_at)"
writing_data_to_a_table = "INSERT INTO members_contacts(username, id, access_hash, name, user_phone, online_at) " \
                          "VALUES (?, ?, ?, ?, ?, ?)"


def we_record_phone_numbers_in_the_db() -> None:
    """Записываем номера телефонов в базу данных"""
    print("[bold green]Контакты которые были добавлены в телефонную книгу, будем записывать с файл "
          "software_database.db, в папке setting_user")
    # Вводим имя файла с которым будем работать
    file_name_input = console.input("[bold green][+] Введите имя файла с контактами, в папке contacts, имя вводим без "
                                    "txt: ")
    # Открываем файл с которым будем работать
    with open(f"setting_user/{file_name_input}.txt", "r") as file_contact:
        for line in file_contact.readlines():
            print(line.strip())
            # strip() - удаляет с конца и начала строки лишние пробелы, в том числе символ окончания строки
            lines = line.strip()
            entities = [lines]
            creating_a_table = "CREATE TABLE IF NOT EXISTS contact(phone)"
            writing_data_to_a_table = "INSERT INTO contact(phone) VALUES (?)"
            writing_data_to_the_db(creating_a_table, writing_data_to_a_table, entities)


@handle_exceptions_pars
def show_account_contact_list() -> None:
    """Показать список контактов аккаунтов и запись результатов в файл"""
    # Открываем базу данных для работы с аккаунтами setting_user/software_database.db
    records: list = open_the_db_and_read_the_data(name_database_table="config")
    for row in records:
        # Подключение к Telegram и вывод имя аккаунта в консоль / терминал
        client, phone = connect_to_telegram_account_and_output_name(row)
        parsing_and_recording_contacts_in_the_database(client)
        client.disconnect()  # Разрываем соединение telegram


def parsing_and_recording_contacts_in_the_database(client) -> None:
    """Парсинг и запись контактов в базу данных"""
    all_participants: list = []
    result = client(functions.contacts.GetContactsRequest(hash=0))
    all_participants.extend(result.users)  # Печатаем результат
    for contact in all_participants:  # Выводим результат parsing
        entities = formation_of_account_data(contact)
        writing_data_to_the_db(creating_a_table, writing_data_to_a_table, entities)


def formation_of_account_data(user) -> list:
    """Формирование данных аккаунта"""
    username = user.username if user.username else ""
    user_phone = user.phone if user.phone else ""
    first_name = user.first_name if user.first_name else ""
    last_name = user.last_name if user.last_name else ""
    online_at = user.status.was_online if isinstance(user.status, types.UserStatusOffline) else ""
    name = (first_name + ' ' + last_name).strip()
    entities = [username, user.id, user.access_hash, name, user_phone, online_at]
    return entities


def we_get_the_account_id(client) -> None:
    """Получаем id аккаунта"""
    all_participants: list = []
    result = client(functions.contacts.GetContactsRequest(hash=0))
    print(result)  # Печатаем результат
    all_participants.extend(result.users)
    # Выводим результат parsing
    for user in all_participants:
        entities = formation_of_account_data(user)
        we_show_and_delete_the_contact_of_the_phone_book(entities, client, user)


def we_show_and_delete_the_contact_of_the_phone_book(entities, client, user) -> None:
    """Показываем и удаляем контакт телефонной книги"""
    print(f"[bold green]{entities}")
    client(functions.contacts.DeleteContactsRequest(id=[user.id]))
    print("[bold green] Подождите 2 - 4 секунды")
    time.sleep(random.randrange(2, 3, 4))  # Спим для избежания ошибки о flood


@handle_exceptions_pars
def delete_contact() -> None:
    """Удаляем контакты с аккаунтов"""
    # Открываем базу данных для работы с аккаунтами setting_user/software_database.db
    records: list = open_the_db_and_read_the_data(name_database_table="config")
    for row in records:
        # Подключение к Telegram и вывод имя аккаунта в консоль / терминал
        client, phone = connect_to_telegram_account_and_output_name(row)
        we_get_the_account_id(client)
        client.disconnect()  # Разрываем соединение telegram


@handle_exceptions_pars
def inviting_contact() -> None:
    """Добавление данных в телефонную книгу с последующим формированием списка software_database.db, для inviting"""
    # Открываем базу данных для работы с аккаунтами setting_user/software_database.db
    records: list = open_the_db_and_read_the_data(name_database_table="config")
    print(f"[bold red]Всего accounts: {len(records)}")
    for row in records:
        # Подключение к Telegram и вывод имя аккаунта в консоль / терминал
        client, phone = connect_to_telegram_account_and_output_name(row)
        adding_a_contact_to_the_phone_book(client)


def adding_a_contact_to_the_phone_book(client) -> None:
    """Добавляем контакт в телефонную книгу"""
    # Открываем сформированный список setting_user/software_database.db
    records: list = open_the_db_and_read_the_data(name_database_table="contact")
    print(f"[bold red]Всего номеров: {len(records)}")
    for rows in records:
        user = {'phone': rows[0]}
        phone = user['phone']
        # Добавляем контакт в телефонную книгу
        client(functions.contacts.ImportContactsRequest(contacts=[
            types.InputPhoneContact(client_id=0, phone=phone, first_name="Номер", last_name=phone)]))
        try:
            # Получаем данные номера телефона https://docs.telethon.dev/en/stable/concepts/entities.html
            contact = client.get_entity(phone)
            entities: list = formation_of_account_data(contact)
            print(f"[bold green][+] Контакт с добавлен в телефонную книгу!")
            # Запись результатов parsing в файл members_contacts.db, для дальнейшего inviting
            writing_data_to_the_db(creating_a_table, writing_data_to_a_table, entities)
            # После работы с номером телефона, программа удаляет номер со списка
            delete_row_db(table="contact", column="phone", value=user['phone'])
        except ValueError:
            print(f"[bold green][+] Контакт с номером {phone} не зарегистрирован или отсутствует "
                  f"возможность добавить в телефонную книгу!")
            # После работы с номером телефона, программа удаляет номер со списка
            delete_row_db(table="contact", column="phone", value=user['phone'])
    client.disconnect()  # Разрываем соединение telegram


if __name__ == "__main__":
    show_account_contact_list()
    delete_contact()
    inviting_contact()
