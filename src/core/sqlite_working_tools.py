# -*- coding: utf-8 -*-
import datetime
import sqlite3

from loguru import logger
from peewee import fn, SqliteDatabase, Model, IntegerField, CharField, TextField, DateTimeField

db = SqliteDatabase('user_data/software_database.db')


class GroupsAndChannels(Model):
    """
    Список групп и каналов в таблице groups_and_channels
    """

    id = IntegerField(primary_key=True)
    title = CharField(max_length=255)
    about = TextField(null=True)
    link = CharField(max_length=255)
    members_count = IntegerField(default=0)
    parsing_time = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db


def remove_duplicates():
    """
    Удаление дублирующихся id в таблице groups_and_channels
    """

    # Находим все записи с дублирующимися id
    duplicate_ids = (
        GroupsAndChannels
        .select(GroupsAndChannels.id)
        .group_by(GroupsAndChannels.id)
        .having(fn.COUNT(GroupsAndChannels.id) > 1)
    )

    # Для каждого дублирующегося id оставляем только первую запись, остальные удаляем
    for duplicate in duplicate_ids:
        # Находим все записи с этим id, сортируем по времени парсинга
        duplicates = (
            GroupsAndChannels
            .select()
            .where(GroupsAndChannels.id == duplicate.id)
            .order_by(GroupsAndChannels.parsing_time)
        )

        for record in duplicates[1:]:  # Оставляем только первую запись, остальные удаляем
            record.delete_instance()


class DatabaseHandler:
    def __init__(self, db_file="user_data/software_database.db"):
        self.db_file = db_file

    async def connect(self) -> None:
        """Подключение к базе данных"""
        self.sqlite_connection = sqlite3.connect(self.db_file)
        self.cursor = self.sqlite_connection.cursor()

    def close(self) -> None:
        """Закрытие соединения с базой данных"""
        self.sqlite_connection.close()

    async def open_and_read_data(self, table_name) -> list:
        """
        Открываем базу и считываем данные из указанной таблицы

        Аргументы:
        :param table_name: Название таблицы, данные из которой требуется извлечь.

        Возвращаемое значение:
        :return: список записей из таблицы

        Исключения:
        В случае ошибок базы данных (например, поврежденный файл базы данных или некорректный запрос)
        метод ловит исключения типа `sqlite3.Error` и записывает ошибку в лог, но не выбрасывает её дальше.
        Это предотвращает аварийное завершение работы программы и позволяет продолжить выполнение.
        """
        try:
            await self.connect()
            self.cursor.execute(f"SELECT * FROM {table_name}")
            records = self.cursor.fetchall()
            self.close()
            return records
        except sqlite3.DatabaseError as error:  # Ошибка при открытии базы данных
            logger.error(f"❌ Ошибка при открытии базы данных, возможно база данных повреждена: {error}")
            return []
        except sqlite3.Error as error:  # Ошибка при открытии базы данных
            logger.error(f"❌ Ошибка при открытии базы данных: {error}")
            return []
        finally:
            self.close()  # Закрываем соединение

    async def remove_duplicate_ids(self, table_name, column_name) -> None:
        """
        Этот запрос удаляет все дублирующиеся записи в поле id. Данный запрос использует функцию MIN(), которая возвращает
        минимальное значение из списка значений. Функция MIN() будет применена к полю rowid, которое является уникальным
        идентификатором каждой записи в таблице members. Данный запрос сначала выбирает минимальное значение rowid для
        каждой записи в поле id. Затем он удаляет все записи, у которых rowid не равен минимальному значению.
        Это позволяет оставить только уникальные значения в поле id.

        Аргументы:
        :param table_name: Название таблицы, данные из которой требуется извлечь.
        :param column_name: Имя столбца
        """
        await self.connect()
        self.cursor.execute(f"DELETE FROM {table_name} WHERE row{column_name} NOT IN (SELECT MIN(row{column_name}) "
                            f"FROM {table_name} GROUP BY {column_name})")
        self.sqlite_connection.commit()
        self.close()

    async def open_db_func_lim(self, table_name, account_limit) -> list:
        """
        Открытие базы данных для inviting (рассылка сообщений) с лимитами. Если number_of_accounts равно None,
        возвращаем весь список

        Аргументы:
        :param table_name: Название таблицы, данные из которой требуется извлечь.
        :param account_limit: Количество аккаунтов
        :return list: полученный список
        """
        try:
            await self.connect()
            self.cursor.execute(f"SELECT * from {table_name}")  # Считываем таблицу
            if account_limit is not None:
                records: list = self.cursor.fetchmany(account_limit)  # fetchmany(size) – возвращает число записей
            else:
                records: list = self.cursor.fetchall()  # Если number_of_accounts равно None, возвращаем весь список

            self.cursor.close()
            self.close()  # Закрываем базу данных
            return records
        except Exception as error:
            logger.exception(f"❌ Ошибка: {error}")

    async def write_parsed_chat_participants_to_db_active(self, entities) -> None:
        """
        Запись результатов parsing участников чата

        Аргументы:
        :param entities: список результатов parsing
        """
        await self.connect()
        # Записываем ссылку на группу для parsing в файл user_data/software_database.db"""
        self.cursor.execute("CREATE TABLE IF NOT EXISTS members(username, id, access_hash, first_name, last_name, "
                            "user_phone, online_at, photos_id, user_premium)")
        self.cursor.executemany("INSERT INTO members(username, id, access_hash, first_name, last_name, user_phone, "
                                "online_at, photos_id, user_premium) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                [entities])
        self.sqlite_connection.commit()
        self.close()  # cursor_members.close() – закрытие соединения с БД.

    async def write_data_to_db(self, creating_a_table, writing_data_to_a_table, entities) -> None:
        """
        Запись действий аккаунта в базу данных

        Аргументы:
        :param creating_a_table: создание таблицы
        :param writing_data_to_a_table: запись данных в таблицу
        :param entities: список записей в таблице
        """
        await self.connect()
        self.cursor.execute(creating_a_table)  # Считываем таблицу
        try:
            self.cursor.executemany(writing_data_to_a_table, (entities,))
            self.sqlite_connection.commit()  # cursor_members.commit() – применение всех изменений в таблицах БД
            self.close()  # cursor_members.close() – закрытие соединения с БД.
        except sqlite3.ProgrammingError as e:
            logger.error(e)
            return  # Выходим из функции write_data_to_db

    async def write_parsed_chat_participants_to_db(self, entities) -> None:
        """
        Запись результатов parsing участников чата

        Аргументы:
        :param entities: список результатов parsing
        """
        await self.connect()
        for line in entities:
            # Записываем ссылку на группу для parsing в файл user_data/software_database.db"""
            self.cursor.execute("CREATE TABLE IF NOT EXISTS members(username, id, access_hash, first_name, last_name, "
                                "user_phone, online_at, photos_id, user_premium)")
            self.cursor.executemany("INSERT INTO members(username, id, access_hash, first_name, last_name, user_phone, "
                                    "online_at, photos_id, user_premium) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (line,), )
            self.sqlite_connection.commit()
        self.close()  # cursor_members.close() – закрытие соединения с БД.

    async def deleting_an_invalid_proxy(self, proxy_type, addr, port, username, password, rdns) -> None:
        """
        Удаляем не рабочий proxy с software_database.db, таблица proxy

        Аргументы:
        :param proxy_type: тип proxy
        :param addr: адрес
        :param port: порт
        :param username: имя пользователя
        :param password: пароль
        :param rdns: прокси
        """
        await self.connect()
        self.cursor.execute(
            f"DELETE FROM proxy WHERE proxy_type='{proxy_type}' AND addr='{addr}' AND port='{port}' AND "
            f"username='{username}' AND password='{password}' AND rdns='{rdns}'"
        )
        logger.info(f"{self.cursor.rowcount} rows deleted")
        self.sqlite_connection.commit()  # cursor_members.commit() – применение всех изменений в таблицах БД
        self.close()  # cursor_members.close() – закрытие соединения с БД.

    async def delete_row_db(self, table, column, value) -> None:
        """
        Удаляет строку из таблицы

        Аргументы:
        :param table: имя таблицы
        :param column: имя колонки
        :param value: значение
        """
        await self.connect()
        self.cursor.execute(f"SELECT * from {table}")  # Считываем таблицу
        try:
            self.cursor.execute(f"DELETE from {table} where {column} = ?", (value,))  # Удаляем строку
            self.sqlite_connection.commit()  # cursor_members.commit() – применение всех изменений в таблицах БД
        except sqlite3.ProgrammingError:
            self.cursor.execute(f"DELETE from {table} where {column} = ?", value)
            self.sqlite_connection.commit()  # cursor_members.commit() – применение всех изменений в таблицах БД
        self.close()  # cursor_members.close() – закрытие соединения с БД.

    async def save_proxy_data_to_db(self, proxy) -> None:
        """Запись данных proxy в базу данных"""
        await self.connect()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS proxy(proxy_type, addr, port, username, password, rdns)")
        self.cursor.executemany("INSERT INTO proxy(proxy_type, addr, port, username, password, rdns) "
                                "VALUES (?, ?, ?, ?, ?, ?)", (proxy,), )
        self.sqlite_connection.commit()
        self.close()  # cursor_members.close() – закрытие соединения с БД.

    async def write_to_single_column_table(self, name_database, database_columns, into_columns, recorded_data) -> None:
        """
        Запись данных в таблицу с одной колонкой в базу данных

        Аргументы:
        :param name_database: название таблицы
        :param database_columns: название колон
        :param into_columns: название колонки в таблице
        :param recorded_data: данные для записи
        """
        await self.connect()
        # Записываем ссылку на группу для parsing в файл user_data/software_database.db"""
        self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {name_database}({database_columns})")
        for line in recorded_data:
            # strip() - удаляет с конца и начала строки лишние пробелы, в том числе символ окончания строки
            lines = line.strip()
            self.cursor.execute(f"INSERT INTO {into_columns} VALUES (?)", (lines,))
            self.sqlite_connection.commit()
        self.close()  # cursor_members.close() – закрытие соединения с БД.

    async def cleaning_db(self, name_database_table) -> None:
        """
        Очистка указанной таблицы (name_database_table) в базе данных.

        Этот метод устанавливает соединение с базой данных, удаляет все записи из указанной таблицы (name_database_table),
        затем фиксирует изменения. После этого закрывает соединение с базой данных.

        Аргументы:
        :param name_database_table: Название таблицы в базе данных
        """
        await self.connect()
        # Удаляем таблицу members, функция execute отвечает за SQL-запрос DELETE FROM - команда удаления базы данных
        # name_database_table - название таблицы в базе данных
        self.cursor.execute(f"DELETE FROM {name_database_table};")
        self.sqlite_connection.commit()
        self.close()  # cursor_members.close() – закрытие соединения с БД.

    async def remove_records_without_username(self) -> None:
        """Чистка списка от участников у которых нет username"""
        logger.info("Чищу список software_database.db от участников у которых нет username")
        await self.connect()
        self.cursor.execute("""SELECT * from members""")
        records: list = self.cursor.fetchall()
        logger.info(f"Всего username: {len(records)}")
        for rows in records:
            ints_list1 = {"username": rows[0]}
            username = ints_list1["username"]
            username_name = "NONE"
            if username == username_name:
                # Удаляем пользователя без username
                self.cursor.execute("""DELETE from members where username = ?""", (username_name,))
                self.sqlite_connection.commit()

    async def read_parsed_chat_participants_from_db(self):
        """
        Чтение данных из базы данных.
        """
        await self.connect()
        self.cursor.execute("SELECT * FROM members")
        data = self.cursor.fetchall()
        self.close()
        return data
