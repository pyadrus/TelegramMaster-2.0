# -*- coding: utf-8 -*-
import datetime

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


def create_database():
    """Создает все таблицы в базе данных"""
    db.connect()
    db.create_tables([WritingGroupLinks, GroupsAndChannels, MembersAdmin])
    db.create_tables([LinksInviting])  # Создаем таблицу для хранения ссылок для инвайтинга
    db.create_tables([MembersGroups])  # Создаем таблицу для хранения спарсенных пользователей
    db.create_tables([Contact])  # Создаем таблицу для хранения контактов
    db.create_tables([Proxy])  # Создаем таблицу для хранения прокси


def write_to_single_column_table():
    """Запись username в таблицу members"""


"""Работа с таблицей members"""


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


def add_member_to_db(log_data):
    """
    Добавляет нового участника в базу данных или обновляет существующие данные.

    :param log_data: Словарь с информацией о пользователе
    """
    # Проверка существования пользователя в БД и атомарная запись новых данных
    with db.atomic():
        MembersGroups.get_or_create(
            user_id=log_data["user_id"],
            defaults={
                "username": log_data["username"],
                "access_hash": log_data["access_hash"],
                "first_name": log_data["first_name"],
                "last_name": log_data["last_name"],
                "user_phone": log_data["user_phone"],
                "online_at": log_data["online_at"],
                "photos_id": log_data["photos_id"],
                "user_premium": log_data["user_premium"],
            }
        )


def write_data_to_db(writing_group_links) -> None:
    """
    Запись действий аккаунта в базу данных

    :param writing_group_links: Ссылка на группу
    """
    MembersGroups.delete().where(WritingGroupLinks.writing_group_links == writing_group_links).execute()


def delete_row_db(username) -> None:
    """
    Удаляет строку из таблицы

    :param username: Имя пользователя
    """
    MembersGroups.delete().where(MembersGroups.username == username).execute()


"""Работа с таблицей proxy"""


class Proxy(Model):
    """
    Таблица для хранения прокси в таблице proxy
    """
    proxy_type = CharField(max_length=255)
    addr = CharField(max_length=255)
    port = CharField(max_length=255)
    username = CharField(max_length=255)
    password = CharField(max_length=255)
    rdns = CharField(max_length=255)

    class Meta:
        database = db
        table_name = 'proxy'


def save_proxy_data_to_db(proxy) -> None:
    """Запись данных proxy в базу данных"""
    with db.atomic():
        Proxy.get_or_create(
            proxy_type=proxy["proxy_type"],
            addr=proxy["addr"],
            port=proxy["port"],
            username=proxy["username"],
            password=proxy["password"],
            rdns=proxy["rdns"],
        )


async def deleting_an_invalid_proxy(proxy_type, addr, port, username, password, rdns, page: ft.Page) -> None:
    """
    Удаляем не рабочий proxy с software_database.db, таблица proxy

    :param page: Объект класса Page, который будет использоваться для отображения данных.
    :param proxy_type: Тип proxy
    :param addr: адрес
    :param port: порт
    :param username: имя пользователя
    :param password: пароль
    :param rdns: прокси
    """
    query = Proxy.delete().where(
        (Proxy.proxy_type == proxy_type) &
        (Proxy.addr == addr) &
        (Proxy.port == port) &
        (Proxy.username == username) &
        (Proxy.password == password) &
        (Proxy.rdns == rdns)
    )
    deleted_count = query.execute()
    await log_and_display(f"{deleted_count} rows deleted", page)


def open_and_read_data():
    pass

# 458
