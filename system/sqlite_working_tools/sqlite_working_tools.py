import sqlite3
import time

from rich import print


class DatabaseHandler:
    def __init__(self, db_file="user_settings/software_database.db"):
        self.db_file = db_file

    def connect(self) -> None:
        """Подключение к базе данных"""
        self.sqlite_connection = sqlite3.connect(self.db_file)
        self.cursor = self.sqlite_connection.cursor()

    def close(self) -> None:
        """Закрытие соединения с базой данных"""
        self.sqlite_connection.close()

    def open_and_read_data(self, table_name) -> list:
        """Открываем базу и считываем данные из указанной таблицы"""
        self.connect()
        self.cursor.execute(f"SELECT * FROM {table_name}")
        records = self.cursor.fetchall()
        self.close()
        return records

    def delete_duplicates(self, table_name, column_name) -> None:
        """
        Этот запрос удаляет все дублирующиеся записи в поле id. Данный запрос использует функцию MIN(), которая возвращает
        минимальное значение из списка значений. Функция MIN() будет применена к полю rowid, которое является уникальным
        идентификатором каждой записи в таблице members. Данный запрос сначала выбирает минимальное значение rowid для
        каждой записи в поле id. Затем он удаляет все записи, у которых rowid не равен минимальному значению.
        Это позволяет оставить только уникальные значения в поле id.
        """
        self.connect()
        self.cursor.execute(f"DELETE FROM {table_name} WHERE row{column_name} NOT IN (SELECT MIN(row{column_name}) "
                            f"FROM {table_name} GROUP BY {column_name})")
        self.sqlite_connection.commit()
        self.close()

    def open_the_db_and_read_the_data_lim(self, name_database_table, number_of_accounts: int) -> list:
        """
        Открытие базы данных для inviting (рассылка сообщений) c лимитами
        Если number_of_accounts равно None, возвращаем весь список
        """
        self.connect()
        self.cursor.execute(f"SELECT * from {name_database_table}")  # Считываем таблицу
        if number_of_accounts is not None:
            records: list = self.cursor.fetchmany(number_of_accounts)  # fetchmany(size) – возвращает число записей

        else:
            records: list = self.cursor.fetchall()  # Если number_of_accounts равно None, возвращаем весь список

        self.cursor.close()
        self.close()  # Закрываем базу данных
        return records

    def write_data_to_db(self, creating_a_table, writing_data_to_a_table, entities) -> None:
        """Запись действий аккаунта в базу данных"""
        self.connect()
        self.cursor.execute(creating_a_table)  # Считываем таблицу
        try:
            self.cursor.executemany(writing_data_to_a_table, (entities,))
            self.sqlite_connection.commit()  # cursor_members.commit() – применение всех изменений в таблицах БД
            self.close()  # cursor_members.close() – закрытие соединения с БД.
        except sqlite3.ProgrammingError as e:
            print(e)
            time.sleep(5)

    def deleting_an_invalid_proxy(self, proxy_type, addr, port, username, password, rdns) -> None:
        """Удаляем не рабочий proxy с software_database.db, таблица proxy"""
        self.connect()
        self.cursor.execute(
            f"DELETE FROM proxy WHERE proxy_type='{proxy_type}' AND addr='{addr}' AND port='{port}' AND "
            f"username='{username}' AND password='{password}' AND rdns='{rdns}'"
        )
        print(f"{self.cursor.rowcount} rows deleted")
        self.sqlite_connection.commit()  # cursor_members.commit() – применение всех изменений в таблицах БД
        self.close()  # cursor_members.close() – закрытие соединения с БД.

    def delete_row_db(self, table, column, value) -> None:
        """Удаляет строку из таблицы"""
        self.connect()
        self.cursor.execute(f"SELECT * from {table}")  # Считываем таблицу
        self.cursor.execute(f"DELETE from {table} where {column} = ?", (value,))  # Удаляем строку
        self.sqlite_connection.commit()  # cursor_members.commit() – применение всех изменений в таблицах БД
        self.close()  # cursor_members.close() – закрытие соединения с БД.

    def write_parsed_chat_participants_to_db(self, entities) -> None:
        """Запись результатов parsing участников чата"""
        self.connect()
        for line in entities:
            # Записываем ссылку на группу для parsing в файл user_settings/software_database.db"""
            self.cursor.execute("CREATE TABLE IF NOT EXISTS members(username, id, access_hash, first_name, last_name, "
                                "user_phone, online_at, photos_id, user_premium)")
            self.cursor.executemany("INSERT INTO members(username, id, access_hash, first_name, last_name, user_phone, "
                                    "online_at, photos_id, user_premium) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (line,), )
            self.sqlite_connection.commit()
        self.close()  # cursor_members.close() – закрытие соединения с БД.

    def write_parsed_chat_participants_to_db_active(self, entities) -> None:
        """Запись результатов parsing участников чата"""
        self.connect()
        # for line in entities:
        # Записываем ссылку на группу для parsing в файл user_settings/software_database.db"""
        self.cursor.execute("CREATE TABLE IF NOT EXISTS members(username, id, access_hash, first_name, last_name, "
                            "user_phone, online_at, photos_id, user_premium)")
        self.cursor.executemany("INSERT INTO members(username, id, access_hash, first_name, last_name, user_phone, "
                                "online_at, photos_id, user_premium) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                [entities])
        self.sqlite_connection.commit()
        self.close()  # cursor_members.close() – закрытие соединения с БД.

    def add_columns_to_table(self) -> None:
        """Добавляем новые колонки в базу данных"""
        self.connect()
        try:
            # Добавьте столбец member_count
            self.cursor.execute("ALTER TABLE groups_and_channels ADD COLUMN members_count INTEGER")
            # Add the parsing_time column
            self.cursor.execute("ALTER TABLE groups_and_channels ADD COLUMN parsing_time TEXT")
            self.sqlite_connection.commit()
        except sqlite3.OperationalError:
            print("Columns already exist")
        finally:
            self.close()  # cursor_members.close() – закрытие соединения с БД.

    def save_proxy_data_to_db(self, proxy) -> None:
        """Запись данных proxy в базу данных"""
        self.connect()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS proxy(proxy_type, addr, port, username, password, rdns)")
        self.cursor.executemany("INSERT INTO proxy(proxy_type, addr, port, username, password, rdns) "
                                "VALUES (?, ?, ?, ?, ?, ?)", (proxy,), )
        self.sqlite_connection.commit()
        self.close()  # cursor_members.close() – закрытие соединения с БД.

    def creating_table(self, CREATE_TABLE):
        self.connect()
        self.cursor.execute(CREATE_TABLE)
        self.sqlite_connection.commit()
        self.close()

    def write_members_column_table(self, recorded_data) -> None:
        """Запись данных в таблицу с одной колонкой в базу данных"""
        self.connect()
        # Создание таблицы, если она еще не существует
        self.cursor.execute("CREATE TABLE IF NOT EXISTS members (username, id, access_hash, first_name, last_name, "
                            "user_phone, online_at, photos_id, user_premium)")
        for line in recorded_data:
            # Записываем значение username
            username = line.strip()
            # Вставляем данные в таблицу, используя параметризованный запрос
            self.cursor.execute("INSERT INTO members (username) VALUES (?)", (username,))
            self.sqlite_connection.commit()
        self.close()  # cursor_members.close() – закрытие соединения с БД.

    def write_to_single_column_table(self, name_database, recorded_data) -> None:
        """Запись данных в таблицу с одной колонкой в базу данных"""
        self.connect()
        for line in recorded_data:
            # Записываем ссылку на группу для parsing в файл user_settings/software_database.db"""
            self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {name_database}({name_database})")
            # strip() - удаляет с конца и начала строки лишние пробелы, в том числе символ окончания строки
            lines = line.strip()
            self.cursor.execute(f"INSERT INTO {name_database} VALUES (?)", (lines,))
            self.sqlite_connection.commit()
        self.close()  # cursor_members.close() – закрытие соединения с БД.

    def cleaning_db(self, name_database_table) -> None:
        """
        Очистка указанной таблицы (name_database_table) в базе данных.

        Этот метод устанавливает соединение с базой данных, удаляет все записи из указанной таблицы (name_database_table),
        затем фиксирует изменения. После этого закрывает соединение с базой данных.
        """
        self.connect()
        # Удаляем таблицу members, функция execute отвечает за SQL-запрос DELETE FROM - команда удаления базы данных
        # name_database_table - название таблицы в базе данных
        self.cursor.execute(f"DELETE FROM {name_database_table};")
        self.sqlite_connection.commit()
        self.close()  # cursor_members.close() – закрытие соединения с БД.

    def cleaning_list_of_participants_who_do_not_have_username(self) -> None:
        """Чистка списка от участников у которых нет username"""
        print("[medium_purple3]Чищу список software_database.db от участников у которых нет username")
        self.connect()
        self.cursor.execute("""SELECT * from members""")
        records: list = self.cursor.fetchall()
        print(f"[medium_purple3]Всего username: {len(records)}")
        for rows in records:
            ints_list1 = {"username": rows[0]}
            username = ints_list1["username"]
            username_name = "NONE"
            if username == username_name:
                # Удаляем пользователя без username
                self.cursor.execute("""DELETE from members where username = ?""", (username_name,))
                self.sqlite_connection.commit()
