import sqlite3

from rich import print

""" 
Работа с базой данных sqlite3
https://proproprogs.ru/modules/podklyuchenie-k-bd-sozdanie-i-udalenie-tablic

IF NOT EXISTS поможет при попытке повторного подключения к базе данных.
Запрос проверит, существует ли таблица. Если да — проверит, ничего ли не поменялось.

Методы:
con.commit() – применение всех изменений в таблицах БД;
con.close() – закрытие соединения с БД.

execute - метод для выполнения одного выражения SQL
executemany - метод позволяет выполнить одно выражение SQL для последовательности параметров (или для итератора)
executescript - метод позволяет выполнить несколько выражений SQL за один раз

cursor.close() освобождает память, в которой делали предварительные изменения.
sqlite_connection.close() освобождает память, нужную для управления связью с базой данных.
(Эта команда соответствует закрытию файла - «закрывает» базу данных.)

cursor — это объект в памяти компьютера с методами для проведения SQL команд, хранения итогов их 
выполнения (например части таблицы или (view)) и методов доступа к ним.

Пока работаем с курсором, мы только делаем предварительные изменения 
(например готовимся что-то изменить в реальной базе данных). 
Без применения sqlite_connection.commit() итоги предварительные изменения мы потеряем — они не запишутся в 
реальную базу данных.
Когда нужно прочитать базу данных, команду sqlite_connection.commit() применять не нужно.
"""


def connecting_to_the_database():
    """Подключение к базе данных"""
    with sqlite3.connect('user_settings/software_database.db') as sqlite_connection:
        cursor = sqlite_connection.cursor()

        return sqlite_connection, cursor


def add_columns_to_table():
    """Добавляем новые колонки в базу данных"""
    sqlite_connection, cursor = connecting_to_the_database()
    try:
        # Добавьте столбец member_count
        cursor.execute("ALTER TABLE groups_and_channels ADD COLUMN members_count INTEGER")
        # Add the parsing_time column
        cursor.execute("ALTER TABLE groups_and_channels ADD COLUMN parsing_time TEXT")
        sqlite_connection.commit()
    except sqlite3.OperationalError:
        print("Columns already exist")
    finally:
        sqlite_connection.close()


def write_parsed_chat_participants_to_db(entities) -> None:
    """Запись результатов parsing участников чата"""
    sqlite_connection, cursor = connecting_to_the_database()
    for line in entities:
        # Записываем ссылку на группу для parsing в файл user_settings/software_database.db"""
        cursor.execute("CREATE TABLE IF NOT EXISTS members(username, id, access_hash, first_name, last_name, "
                       "user_phone, online_at, photos_id, user_premium)")
        cursor.executemany("INSERT INTO members(username, id, access_hash, first_name, last_name, user_phone, "
                           "online_at, photos_id, user_premium) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (line,))
        sqlite_connection.commit()
    cursor.close()
    sqlite_connection.close()  # Закрываем базу данных


def save_proxy_data_to_db(proxy) -> None:
    """Запись данных proxy в базу данных"""
    sqlite_connection, cursor = connecting_to_the_database()
    cursor.execute("CREATE TABLE IF NOT EXISTS proxy(proxy_type, addr, port, username, password, rdns)")
    cursor.executemany("INSERT INTO proxy(proxy_type, addr, port, username, password, rdns) "
                       "VALUES (?, ?, ?, ?, ?, ?)", (proxy,))
    sqlite_connection.commit()
    cursor.close()
    sqlite_connection.close()  # Закрываем базу данных


def delete_row_db(table, column, value) -> None:
    """Удаляет строку из таблицы"""
    sqlite_connection, cursor = connecting_to_the_database()
    cursor.execute(f"SELECT * from {table}")  # Считываем таблицу
    cursor.execute(f"DELETE from {table} where {column} = ?", (value,))  # Удаляем строку
    sqlite_connection.commit()  # cursor_members.commit() – применение всех изменений в таблицах БД
    cursor.close()  # cursor_members.close() – закрытие соединения с БД.


def write_data_to_db(creating_a_table, writing_data_to_a_table, entities) -> None:
    """Запись действий аккаунта в базу данных"""
    sqlite_connection, cursor = connecting_to_the_database()
    cursor.execute(creating_a_table)  # Считываем таблицу
    cursor.executemany(writing_data_to_a_table, (entities,))
    sqlite_connection.commit()  # cursor_members.commit() – применение всех изменений в таблицах БД
    cursor.close()  # cursor_members.close() – закрытие соединения с БД.


def write_members_column_table(recorded_data) -> None:
    """Запись данных в таблицу с одной колонкой в базу данных"""
    sqlite_connection, cursor = connecting_to_the_database()
    # Создание таблицы, если она еще не существует
    cursor.execute("CREATE TABLE IF NOT EXISTS members (username, id, access_hash, first_name, last_name, "
                   "user_phone, online_at, photos_id, user_premium)")
    for line in recorded_data:
        # Записываем значение username
        username = line.strip()
        # Вставляем данные в таблицу, используя параметризованный запрос
        cursor.execute("INSERT INTO members (username) VALUES (?)", (username,))
        sqlite_connection.commit()

    cursor.close()
    sqlite_connection.close()  # Закрываем базу данных


def write_to_single_column_table(name_database, recorded_data) -> None:
    """Запись данных в таблицу с одной колонкой в базу данных """
    sqlite_connection, cursor = connecting_to_the_database()
    for line in recorded_data:
        # Записываем ссылку на группу для parsing в файл user_settings/software_database.db"""
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {name_database}({name_database})")
        # strip() - удаляет с конца и начала строки лишние пробелы, в том числе символ окончания строки
        lines = line.strip()
        cursor.execute(f"INSERT INTO {name_database} VALUES (?)", (lines,))
        sqlite_connection.commit()
    cursor.close()
    sqlite_connection.close()  # Закрываем базу данных


def open_the_db_and_read_the_data(name_database_table) -> list:
    """Открываем базу считываем данные в качестве аргумента передаем имя таблицы"""
    sqlite_connection, cursor = connecting_to_the_database()
    cursor.execute(f"SELECT * from {name_database_table}")
    # fetchall() – возвращает число записей в виде упорядоченного списка
    records: list = cursor.fetchall()
    cursor.close()
    sqlite_connection.close()  # Закрываем базу данных
    return records


def open_the_db_and_read_the_data_lim(name_database_table, number_of_accounts: int) -> list:
    """Открытие базы данных для inviting c лимитами"""
    sqlite_connection, cursor = connecting_to_the_database()
    cursor.execute(f"SELECT * from {name_database_table}")  # Считываем таблицу
    # fetchmany(size) – возвращает число записей не более size;
    records: list = cursor.fetchmany(number_of_accounts)  # number_of_accounts - количество добавляемых username
    cursor.close()
    sqlite_connection.close()  # Закрываем базу данных
    return records


def cleaning_db(name_database_table) -> None:
    """Чистка базы данных"""
    sqlite_connection, cursor = connecting_to_the_database()
    # Удаляем таблицу members, функция execute отвечает за SQL-запрос DELETE FROM - команда удаления базы данных
    # name_database_table - название таблицы в базе данных
    cursor.execute(f'DELETE FROM {name_database_table};')
    sqlite_connection.commit()
    cursor.close()
    sqlite_connection.close()  # Закрываем базу данных


def cleaning_list_of_participants_who_do_not_have_username() -> None:
    """Чистка списка от участников у которых нет username"""
    print("[bold red]Чищу список software_database.db от участников у которых нет username")
    sqlite_connection, cursor = connecting_to_the_database()
    cursor.execute("""SELECT * from members""")
    records: list = cursor.fetchall()
    print(f"[bold red]Всего username: {len(records)}")
    for rows in records:
        ints_list1 = {'username': rows[0]}
        username = ints_list1["username"]
        username_name = "NONE"
        if username == username_name:
            # Удаляем пользователя без username
            cursor.execute("""DELETE from members where username = ?""", (username_name,))
            sqlite_connection.commit()


def deleting_an_invalid_proxy(proxy_type, addr, port, username, password, rdns) -> None:
    """Удаляем не рабочий proxy с software_database.db, таблица proxy """
    sqlite_connection, cursor = connecting_to_the_database()
    cursor.execute(f"DELETE FROM proxy WHERE proxy_type='{proxy_type}' AND addr='{addr}' AND port='{port}' AND "
                   f"username='{username}' AND password='{password}' AND rdns='{rdns}'")
    print(f"{cursor.rowcount} rows deleted")
    sqlite_connection.commit()  # cursor_members.commit() – применение всех изменений в таблицах БД
    cursor.close()  # cursor_members.close() – закрытие соединения с БД.


def delete_duplicates(table_name, column_name) -> None:
    """
    Этот запрос удаляет все дублирующиеся записи в поле id. Данный запрос использует функцию MIN(), которая возвращает
    минимальное значение из списка значений. Функция MIN() будет применена к полю rowid, которое является уникальным
    идентификатором каждой записи в таблице members. Данный запрос сначала выбирает минимальное значение rowid для
    каждой записи в поле id. Затем он удаляет все записи, у которых rowid не равен минимальному значению.
    Это позволяет оставить только уникальные значения в поле id.
    """
    sqlite_connection, cursor = connecting_to_the_database()
    # Выполнить запрос на удаление дубликатов из таблицы по заданному столбцу
    cursor.execute(f"DELETE FROM {table_name} WHERE row{column_name} NOT IN (SELECT MIN(row{column_name}) "
                   f"FROM {table_name} GROUP BY {column_name})")
    sqlite_connection.commit()  # Сохранить изменения в базе данных
    sqlite_connection.close()  # Закрыть соединение с базой данных user_settings/software_database.db


if __name__ == "__main__":
    cleaning_list_of_participants_who_do_not_have_username()
    add_columns_to_table()
