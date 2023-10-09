import os
import os.path

from rich import print
from telethon import TelegramClient
from telethon.tl.functions.users import GetFullUserRequest

from system.proxy.checking_proxy import reading_proxy_data_from_the_database
from system.setting.setting import reading_the_id_and_hash
from system.sqlite_working_tools.sqlite_working_tools import cleaning_db, DatabaseHandler


def connect_to_telegram_account_and_output_name(row):
    """Подключаемся телеграмм аккаунту и выводим имя"""
    phone, api_id, api_hash = get_from_the_list_phone_api_id_api_hash(row)  # Получаем со списка phone, api_id, api_hash
    proxy = reading_proxy_data_from_the_database()  # Proxy IPV6 - НЕ РАБОТАЮТ
    client = TelegramClient(f"user_settings/accounts/{phone}", api_id, api_hash, proxy=proxy)
    client.connect()  # Подсоединяемся к Telegram
    # Выводим командой print: имя, фамилию, номер телефона аккаунта
    first_name, last_name, phone = account_name(client, name_account="me")
    # Выводим результат полученного имени и номера телефона
    print(f"[bold red][!] Account connect {first_name} {last_name} {phone}")
    return client, phone


def account_name(client, name_account):
    """Показываем имя аккаунта с которого будем взаимодействовать"""
    full = client(GetFullUserRequest(name_account))
    for user in full.users:
        first_name = user.first_name if user.first_name else ""
        last_name = user.last_name if user.last_name else ""
        phone = user.phone if user.phone else ""
        return first_name, last_name, phone


def get_from_the_list_phone_api_id_api_hash(row):
    """Получаем со списка phone, api_id, api_hash"""
    users = {'id': int(row[0]), 'hash': row[1], 'phone': row[2]}
    # Вытягиваем данные из кортежа, для подстановки в функцию
    phone = users['phone']
    api_id = users['id']
    api_hash = users['hash']
    return phone, api_id, api_hash


def we_get_username_user_id_access_hash(rows):
    """Получаем username, user_id, access_hash"""
    user = {'username': rows[0]}
    # Вытягиваем данные из кортежа, для подстановки в функцию
    username = user["username"]
    return username, user


def writing_names_found_files_to_the_db() -> None:
    """Запись названий найденных файлов в базу данных """
    creating_a_table = "CREATE TABLE IF NOT EXISTS config(id, hash, phone)"
    writing_data_to_a_table = "INSERT INTO config (id, hash, phone) VALUES (?, ?, ?)"
    cleaning_db(name_database_table="config")  # Чистим базу данных с аккаунтами
    records = connecting_account_sessions()
    for entities in records:
        print(f"Записываем данные аккаунта {entities} в базу данных")
        db_handler = DatabaseHandler()
        db_handler.write_data_to_db(creating_a_table, writing_data_to_a_table, entities)


def connecting_account_sessions() -> list[list[str]]:
    """Подключение сессий аккаунтов
    Функция listdir() модуля os возвращает список, содержащий имена файлов и директорий в каталоге, заданном путем
    path user_settings/accounts
    Функция str.endswith() возвращает True, если строка заканчивается заданным суффиксом (.session), в противном
    случае возвращает False.
    Os.path.splitext(path) - разбивает путь на пару (root, ext), где ext начинается с точки и содержит не
    более одной точки.
    """
    entities = []  # Создаем словарь с именами найденных аккаунтов в папке user_settings/accounts
    for x in os.listdir(path='user_settings/accounts'):
        if x.endswith('.session'):
            file = os.path.splitext(x)[0]
            print(f"Найденные аккаунты: {file}.session")  # Выводим имена найденных аккаунтов
            api_id_data, api_hash_data = reading_the_id_and_hash()  # Файл с настройками
            entities.append([api_id_data, api_hash_data, file])
    return entities


def renaming_a_session(client, phone_old, phone) -> None:
    """Переименование session файлов"""
    client.disconnect()  # Отключаемся от аккаунта для освобождения session файла
    try:
        # Переименование session файла
        os.rename(f"user_settings/accounts/{phone_old}.session", f"user_settings/accounts/{phone}.session")
    except FileExistsError:
        # Если файл существует, то удаляем дубликат
        os.remove(f"user_settings/accounts/{phone_old}.session")


if __name__ == "__main__":
    reading_proxy_data_from_the_database()
    connecting_account_sessions()
