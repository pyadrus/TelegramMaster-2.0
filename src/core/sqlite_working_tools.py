# -*- coding: utf-8 -*-
import datetime
import sqlite3

import flet as ft
from loguru import logger
from peewee import (SqliteDatabase, Model, CharField, BigIntegerField, TextField, DateTimeField, BooleanField, fn,
                    IntegerField)

from src.core.configs import path_folder_database
from src.gui.gui import log_and_display

db = SqliteDatabase(path_folder_database)


class WritingGroupLinks(Model):
    """
    Таблица для хранения ссылок на группы в таблице writing_group_links
    """
    writing_group_links = CharField(unique=True)  # уникальность для защиты от дубликатов

    class Meta:
        database = db
        table_name = 'writing_group_links'


async def read_writing_group_links():
    """
    Считывает все ссылки на группы из таблицы writing_group_links.

    :return: Список строк (ссылок на группы)
    """

    db.connect(reuse_if_open=True)

    links = [entry.writing_group_links for entry in WritingGroupLinks.select()]
    return links


# Запись ссылки на группу в таблицу writing_group_links
async def write_to_single_column_table_peewee(data: list[str]):
    db.connect()

    for line in set(data):
        cleaned_line = line.strip()
        try:
            WritingGroupLinks.create(writing_group_links=cleaned_line)
        except Exception as e:
            logger.exception(e)
    db.close()


class GroupsAndChannels(Model):
    """
    Список групп и каналов в таблице groups_and_channels
    """
    id = IntegerField(primary_key=True)
    title = CharField(max_length=255)
    about = TextField(null=True)
    link = CharField(max_length=255, null=True)
    members_count = IntegerField(default=0)
    parsing_time = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db
        table_name = 'groups_and_channels'


class MembersAdmin(Model):
    """
    Таблица для хранения данных администраторов групп в таблице members_admin
    """
    username = CharField(max_length=255, null=True)
    user_id = IntegerField(unique=True)
    access_hash = BigIntegerField(null=True)
    first_name = CharField(max_length=255, null=True)
    last_name = CharField(max_length=255, null=True)
    phone = CharField(max_length=255, null=True)
    online_at = DateTimeField(null=True)
    photo_status = CharField(max_length=255, null=True)
    premium_status = BooleanField(default=False)
    user_status = CharField(max_length=255, null=True)
    bio = TextField(null=True)
    group_name = CharField(max_length=255, null=True)

    class Meta:
        database = db
        table_name = 'members_admin'


def remove_duplicate_ids():
    """Удаление дублирующихся id в таблице members"""
    # Получаем все user_id, которые дублируются
    duplicate_user_ids = (
        MembersGroups.select(MembersGroups.user_id)
        .group_by(MembersGroups.user_id)
        .having(fn.COUNT(MembersGroups.user_id) > 1)
    )

    for user_id_row in duplicate_user_ids:
        user_id = user_id_row.user_id

        # Получаем все записи с этим user_id
        duplicates = MembersGroups.select().where(MembersGroups.user_id == user_id)

        # Сохраняем первую, остальные удаляем
        first = True
        for record in duplicates:
            if first:
                first = False
                continue
            record.delete_instance()


class MembersGroups(Model):
    """
    Таблица для хранения данных администраторов групп в таблице members_admin
    """
    username = CharField(max_length=255, null=True)
    user_id = BigIntegerField(unique=True)
    access_hash = BigIntegerField(null=True)
    first_name = CharField(max_length=255, null=True)
    last_name = CharField(max_length=255, null=True)
    user_phone = CharField(max_length=255, null=True)
    online_at = DateTimeField(null=True)
    photos_id = CharField(max_length=255, null=True)
    user_premium = BooleanField(default=False)

    class Meta:
        database = db
        table_name = 'members'


def read_parsed_chat_participants_from_db():
    """
    Чтение данных из базы данных.
    """
    data = []
    query = MembersGroups.select(
        MembersGroups.username, MembersGroups.user_id, MembersGroups.access_hash, MembersGroups.first_name,
        MembersGroups.last_name, MembersGroups.user_phone, MembersGroups.online_at, MembersGroups.photos_id,
        MembersGroups.user_premium
    )
    for row in query:
        data.append((
            row.username, row.user_id, row.access_hash, row.first_name, row.last_name,
            row.user_phone, row.online_at, row.photos_id, row.user_premium
        ))
    return data


def select_records_with_limit(limit):
    """Возвращает список usernames и user_id из таблицы members"""
    usernames = []
    query = MembersGroups.select(MembersGroups.username, MembersGroups.user_id)
    for row in query:
        if row.username == "":
            logger.info(f"У пользователя User ID: {row.user_id} нет username", )
        else:
            logger.info(f"Username: {row.username}, User ID: {row.user_id}", )
            usernames.append(row.username)

    if limit is None:  # Если limit не указан, возвращаем все записи
        return usernames
    return usernames[:limit]  # Возвращаем первые limit записей, если указан


class LinksInviting(Model):
    links_inviting = CharField(unique=True)

    class Meta:
        database = db
        table_name = 'links_inviting'


def get_links_inviting():
    """Получаем ссылки на группы из таблицы links_inviting"""
    links_inviting = []
    for link in LinksInviting.select(LinksInviting.links_inviting):
        links_inviting.append(link.links_inviting)
    return links_inviting


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


class Contact(Model):
    """
    Таблица для хранения данных администраторов групп в таблице members_admin
    """
    contact = CharField(max_length=255, null=True)

    class Meta:
        database = db
        table_name = 'contact'


# TODO добавить все используемые таблицы
def cleaning_db(table_name):
    """
    Очистка базы данных
    :param table_name: Название таблицы, данные из которой требуется очистить.
    """

    if table_name == 'members':  # Удаляем все записи из таблицы members
        MembersGroups.delete().execute()
    if table_name == 'contact':  # Удаляем все записи из таблицы contact
        Contact.delete().execute()
    if table_name == 'writing_group_links':  # Удаляем все записи из таблицы writing_group_links
        WritingGroupLinks.delete().execute()
    if table_name == 'links_inviting':  # Удаляем все записи из таблицы links_inviting
        LinksInviting.delete().execute()

class DatabaseHandler:

    def __init__(self, db_file=path_folder_database):
        self.db_file = db_file

    async def connect(self) -> None:
        """Подключение к базе данных"""
        self.sqlite_connection = sqlite3.connect(self.db_file)
        self.cursor = self.sqlite_connection.cursor()

    def close(self) -> None:
        """Закрытие соединения с базой данных"""
        self.sqlite_connection.close()

    async def open_and_read_data(self, table_name, page: ft.Page):
        """
        Открываем базу и считываем данные из указанной таблицы

        :param table_name: Название таблицы, данные из которой требуется извлечь.
        :param page: Объект класса Page, который будет использоваться для отображения данных.
        :return: Список записей из таблицы

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
            await log_and_display(f"❌ Ошибка при открытии базы данных, возможно база данных повреждена: {error}",
                                  page)
            return []
        except sqlite3.Error as error:  # Ошибка при открытии базы данных
            await log_and_display(f"❌ Ошибка при открытии базы данных: {error}", page)
            return []
        finally:
            self.close()  # Закрываем соединение

    async def select_records_with_limit(self, table_name, limit) -> list:
        """
        Выбирает записи из указанной таблицы БД с возможностью ограничения количества результатов.

        Функция позволяет извлекать записи из заданной таблицы базы данных с учётом лимита на количество элементов.
        Лимит определяется параметром `limit`. Если этот аргумент равен `None`, возвращаются все записи таблицы.

        :param table_name: Имя таблицы, из которой будут извлечены данные.
        :param limit: Максимальное количество записей, которое нужно вернуть. Если `None` — вернёт все записи.
        :return list: Список кортежей с записями из таблицы.
        """
        try:
            await self.connect()  # Подключаемся к базе данных
            self.cursor.execute(f"SELECT * from {table_name}")  # Выполняем SQL-запрос на чтение всех записей из таблицы
            # Если указан лимит, используем метод fetchmany(), иначе fetchall()
            if limit is not None:
                records: list = self.cursor.fetchmany(limit)
            else:
                records: list = self.cursor.fetchall()
            self.cursor.close()
            self.close()  # Закрываем базу данных
            return records
        except Exception as error:
            logger.exception(error)
            raise

    # ToDo Убрать функцию
    async def write_parsed_chat_participants_to_db(self, entities) -> None:
        """
        Запись результатов parsing участников чата

        :param entities: список результатов parsing
        """
        await self.connect()
        for line in entities:
            # Записываем ссылку на группу для parsing в файл user_data/software_database.db"""
            self.cursor.execute(
                "CREATE TABLE IF NOT EXISTS members(username, user_id, access_hash, first_name, last_name, "
                "user_phone, online_at, photos_id, user_premium)")
            self.cursor.executemany(
                "INSERT INTO members(username, user_id, access_hash, first_name, last_name, user_phone, "
                "online_at, photos_id, user_premium) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (line,), )
            self.sqlite_connection.commit()
        self.close()  # cursor_members.close() – закрытие соединения с БД.

    async def write_data_to_db(self, creating_a_table, writing_data_to_a_table, entities, page: ft.Page) -> None:
        """
        Запись действий аккаунта в базу данных

        :param creating_a_table: создание таблицы
        :param writing_data_to_a_table: запись данных в таблицу
        :param entities: список записей в таблице
        :param page: Объект класса Page, который будет использоваться для отображения данных.
        """
        await self.connect()
        self.cursor.execute(creating_a_table)  # Считываем таблицу
        try:
            self.cursor.executemany(writing_data_to_a_table, (entities,))
            self.sqlite_connection.commit()  # cursor_members.commit() – применение всех изменений в таблицах БД
            self.close()  # cursor_members.close() – закрытие соединения с БД.
        except sqlite3.ProgrammingError as e:
            await log_and_display(f"❌ Ошибка: {e}", page)
            return  # Выходим из функции write_data_to_db

    async def deleting_an_invalid_proxy(self, proxy_type, addr, port, username, password, rdns, page: ft.Page) -> None:
        """
        Удаляем не рабочий proxy с software_database.db, таблица proxy

        :param page: Объект класса Page, который будет использоваться для отображения данных.
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
        await log_and_display(f"{self.cursor.rowcount} rows deleted", page)
        self.sqlite_connection.commit()  # cursor_members.commit() – применение всех изменений в таблицах БД
        self.close()  # cursor_members.close() – закрытие соединения с БД.

    async def delete_row_db(self, table, column, value) -> None:
        """
        Удаляет строку из таблицы

        :param table: имя таблицы
        :param column: имя колонки
        :param value: значение
        """
        await self.connect()
        self.cursor.execute(f'''SELECT * from {table}''')  # Считываем таблицу
        try:
            self.cursor.execute(f'''DELETE from {table} where {column} = ?''', (value,))  # Удаляем строку
            self.sqlite_connection.commit()  # cursor_members.commit() – применение всех изменений в таблицах БД
        except sqlite3.ProgrammingError:
            self.cursor.execute(f'''DELETE from {table} where {column} = ?''', value)
            self.sqlite_connection.commit()  # cursor_members.commit() – применение всех изменений в таблицах БД
        self.close()  # cursor_members.close() – закрытие соединения с БД.

    async def save_proxy_data_to_db(self, proxy) -> None:
        """Запись данных proxy в базу данных"""
        await self.connect()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS proxy
                               (
                                   proxy_type,
                                   addr,
                                   port,
                                   username,
                                   password,
                                   rdns
                               )''')
        self.cursor.executemany(
            '''INSERT INTO proxy(proxy_type, addr, port, username, password, rdns)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (proxy,), )
        self.sqlite_connection.commit()
        self.close()  # cursor_members.close() – закрытие соединения с БД.

    async def write_to_single_column_table(self, name_database, database_columns, into_columns, recorded_data) -> None:
        """
        Запись данных в таблицу с одной колонкой в базу данных

        :param name_database: название таблицы
        :param database_columns: название колон
        :param into_columns: название колонки в таблице
        :param recorded_data: данные для записи
        """
        await self.connect()
        # Записываем ссылку на группу для parsing в файл user_data/software_database.db"""
        self.cursor.execute(f'''CREATE TABLE IF NOT EXISTS {name_database}({database_columns})''')
        for line in recorded_data:
            # strip() - удаляет с конца и начала строки лишние пробелы, в том числе символ окончания строки
            lines = line.strip()
            self.cursor.execute(f'''INSERT INTO {into_columns} VALUES (?)''', (lines,))
            self.sqlite_connection.commit()
        self.close()  # cursor_members.close() – закрытие соединения с БД.

    # async def cleaning_db(self, name_database_table) -> None:
    #     """
    #     Очистка указанной таблицы (name_database_table) в базе данных.
    #
    #     Этот метод устанавливает соединение с базой данных, удаляет все записи из указанной таблицы (name_database_table),
    #     затем фиксирует изменения. После этого закрывает соединение с базой данных.
    #
    #     :param name_database_table: Название таблицы в базе данных
    #     """
    #     await self.connect()
    #     # Удаляем таблицу members, функция execute отвечает за SQL-запрос DELETE FROM - команда удаления базы данных
    #     # name_database_table - название таблицы в базе данных
    #     self.cursor.execute(f'''DELETE FROM {name_database_table};''')
    #     self.sqlite_connection.commit()
    #     self.close()  # cursor_members.close() – закрытие соединения с БД.

    # async def remove_records_without_username(self, page: ft.Page) -> None:
    #     """Чистка списка от участников у которых нет username"""
    #     await log_and_display(f"Чищу список software_database.db от участников у которых нет username", page)
    #     await self.connect()
    #     self.cursor.execute('''SELECT *
    #                            from members''')
    #     records: list = self.cursor.fetchall()
    #     await log_and_display(f"Всего username: {len(records)}", page)
    #     for rows in records:
    #         ints_list1 = {"username": rows[0]}
    #         username = ints_list1["username"]
    #         username_name = "NONE"
    #         if username == username_name:
    #             # Удаляем пользователя без username
    #             self.cursor.execute('''DELETE
    #                                    from members
    #                                    where username = ?''', (username_name,))
    #             self.sqlite_connection.commit()


db_handler = DatabaseHandler()
