# -*- coding: utf-8 -*-
import time

from loguru import logger
from telethon import functions
from telethon import types
from telethon.tl.functions.channels import GetFullChannelRequest  # Не удалять
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import ChannelParticipantsSearch
from telethon.tl.types import InputPeerEmpty
from telethon.tl.types import UserStatusEmpty
from telethon.tl.types import UserStatusLastMonth
from telethon.tl.types import UserStatusLastWeek
from telethon.tl.types import UserStatusOffline
from telethon.tl.types import UserStatusOnline
from telethon.tl.types import UserStatusRecently

from system.account_actions.TGConnect import TGConnect
from system.account_actions.TGSubUnsub import SubscribeUnsubscribeTelegram
from system.auxiliary_functions.auxiliary_functions import find_files
from system.auxiliary_functions.global_variables import ConfigReader
from system.sqlite_working_tools.sqlite_working_tools import DatabaseHandler


class ParsingGroupMembers:
    """Парсинг групп"""

    def __init__(self):
        self.db_handler = DatabaseHandler()
        self.tg_connect = TGConnect()
        self.config_reader = ConfigReader()
        self.sub_unsub_tg = SubscribeUnsubscribeTelegram()

    async def parse_groups(self) -> None:
        """Парсинг групп"""
        entities = find_files(directory_path="user_settings/accounts/parsing", extension='session')
        for file in entities:
            client = await self.tg_connect.get_telegram_client(file, account_directory="user_settings/accounts/parsing")

            # Открываем базу с группами для дальнейшего parsing
            records: list = await self.db_handler.open_and_read_data("writing_group_links")
            for groups in records:  # Поочередно выводим записанные группы
                logger.info(f'[+] Парсинг группы: {groups[0]}')
                await self.sub_unsub_tg.subscribe_to_group_or_channel(client, groups[0])
                await self.parse_group(client, groups[0])  # Parsing групп
                await self.db_handler.delete_row_db(table="writing_group_links", column="writing_group_links",
                                                    value=groups)
            await self.db_handler.clean_no_username()  # Чистка списка parsing списка, если нет username
            await self.db_handler.delete_duplicates(table_name="members",
                                                    column_name="id")  # Чистка дублирующих username по столбцу id
            await client.disconnect()

    async def choose_group_for_parsing(self) -> None:
        """Выбираем группу из подписанных для parsing"""
        entities = find_files(directory_path="user_settings/accounts/parsing", extension='session')
        for file in entities:
            client = await self.tg_connect.get_telegram_client(file, account_directory="user_settings/accounts/parsing")
            groups_wr = await self.list_groups(client)
            await self.parse_group(client, groups_wr)
            await self.db_handler.clean_no_username()  # Чистка списка parsing списка, если нет username
            await self.db_handler.delete_duplicates(table_name="members",
                                                    column_name="id")  # Чистка дублирующих username по столбцу id
            await client.disconnect()  # Разрываем соединение telegram

    async def parse_group(self, client, groups_wr) -> None:
        """
        Эта функция выполняет парсинг групп, на которые пользователь подписался. Аргумент phone используется декоратором
        @handle_exceptions для отлавливания ошибок и записи их в базу данных user_settings/software_database.db.
        """
        all_participants: list = await self.parse_users(client, groups_wr)
        logger.info(f"[+] Спарсили данные с группы {groups_wr}")
        # Записываем parsing данные в файл user_settings/software_database.db
        entities: list = await self.get_all_participants(all_participants)
        await self.db_handler.write_parsed_chat_participants_to_db(entities)

    async def parse_active_users(self, chat_input, limit_active_user) -> None:
        """
        Parsing участников, которые пишут в чат (активных участников)
        :param chat_input: ссылка на чат
        :param limit_active_user: лимит активных участников
        """
        entities = find_files(directory_path="user_settings/accounts/parsing", extension='session')
        for file in entities:
            client = await self.tg_connect.get_telegram_client(file, account_directory="user_settings/accounts/parsing")

            await self.sub_unsub_tg.subscribe_to_group_or_channel(client, chat_input)
            time_activity_user_1, time_activity_user_2 = self.config_reader.get_time_activity_user()
            time.sleep(time_activity_user_2)
            await self.get_active_users(client, chat_input, limit_active_user)
            await client.disconnect()  # Разрываем соединение telegram
        await self.db_handler.clean_no_username()  # Чистка списка parsing списка, если нет username
        await self.db_handler.delete_duplicates(table_name="members",
                                                column_name="id")  # Чистка дублирующих username по столбцу id

    async def parse_subscribed_groups(self) -> None:
        """Parsing групп / каналов на которые подписан аккаунт и сохраняем в файл software_database.db"""
        # Открываем базу данных для работы с аккаунтами user_settings/software_database.db
        entities = find_files(directory_path="user_settings/accounts/parsing", extension='session')
        for file in entities:
            # Подключение к Telegram и вывод имя аккаунта в консоль / терминал
            client = await self.tg_connect.get_telegram_client(file, account_directory="user_settings/accounts/parsing")
            logger.info("""Parsing групп / каналов на которые подписан аккаунт""")
            await self.forming_a_list_of_groups(client)
            await client.disconnect()  # Разрываем соединение telegram
        await self.db_handler.delete_duplicates(table_name="groups_and_channels",
                                                column_name="id")  # Чистка дубликатов в базе данных

    async def get_active_users(self, client, chat, limit_active_user) -> None:
        """
        Получаем данные участников группы которые писали сообщения
        :param client: клиент Telegram
        :param chat: ссылка на чат
        :param limit_active_user: лимит активных участников
        """
        async for message in client.iter_messages(chat, limit=int(limit_active_user)):
            if message.from_id is not None and hasattr(message.from_id, 'user_id'):
                from_user = await client.get_entity(message.from_id.user_id)  # Получаем отправителя по ИД
                entities = await self.get_active_user_data(from_user)
                logger.info(entities)
                await self.db_handler.write_parsed_chat_participants_to_db_active(entities)
            else:
                logger.warning(f"Message {message.id} does not have a valid from_id.")

    async def list_groups(self, client):
        """Выводим список групп, выбираем группу, которую будем parsing user с группы telegram
        :param client: объект клиента
        """
        chats: list = []
        last_date = None
        groups: list = []
        result = await client(GetDialogsRequest(offset_date=last_date, offset_id=0,
                                                offset_peer=InputPeerEmpty(), limit=200, hash=0))
        chats.extend(result.chats)
        for chat in chats:

            try:
                if chat.megagroup:
                    groups.append(chat)
            except AttributeError:
                continue  # Игнорируем объекты, у которых нет атрибута 'megagroup'

        i = 0
        for g in groups:
            logger.info(f"[{str(i)}] - {g.title}")
            i += 1
        logger.info("")

        logger.info("[+] Введите номер группы: ")
        # TODO: Убрать input() в коде
        g_index = input("")

        target_group = groups[int(g_index)]
        return target_group

    async def parse_users(self, client, target_group) -> list:
        """Собираем данные user и записываем в файл members.db (создание нового файла members.db)"""

        logger.info("[+] Ищем участников... Сохраняем в файл software_database.db...")

        all_participants: list = []
        while_condition = True
        my_filter = ChannelParticipantsSearch("")
        offset = 0
        while while_condition:
            try:
                participants = await client(
                    GetParticipantsRequest(channel=target_group, offset=offset, filter=my_filter,
                                           limit=200, hash=0))

                all_participants.extend(participants.users)
                offset += len(participants.users)
                if len(participants.users) < 1:
                    while_condition = False
            except TypeError:
                logger.info(
                    f'Ошибка parsing: не верное имя или cсылка {target_group} не является группой / каналом: {target_group}')
                time.sleep(2)
                break
        return all_participants

    async def get_all_participants(self, all_participants) -> list:
        """Формируем список user_settings/software_database.db"""
        entities: list = []  # Создаем словарь
        for user in all_participants:
            await self.get_user_data(user, entities)
        return entities  # Возвращаем словарь пользователей

    async def get_user_data(self, user, entities) -> None:
        """Получаем данные пользователя"""
        username = user.username if user.username else "NONE"
        user_phone = user.phone if user.phone else "Номер телефона скрыт"
        first_name = user.first_name if user.first_name else ""
        last_name = user.last_name if user.last_name else ""
        photos_id = (
            "Пользователь с фото" if isinstance(user.photo, types.UserProfilePhoto) else "Пользователь без фото")
        online_at = "Был(а) недавно"
        # Статусы пользователя https://core.telegram.org/type/UserStatus
        if isinstance(user.status, (
                UserStatusRecently, UserStatusOffline, UserStatusLastWeek, UserStatusLastMonth, UserStatusOnline,
                UserStatusEmpty)):
            if isinstance(user.status, UserStatusOffline):
                online_at = user.status.was_online
            if isinstance(user.status, UserStatusRecently):
                online_at = "Был(а) недавно"
            if isinstance(user.status, UserStatusLastWeek):
                online_at = "Был(а) на этой неделе"
            if isinstance(user.status, UserStatusLastMonth):
                online_at = "Был(а) в этом месяце"
            if isinstance(user.status, UserStatusOnline):
                online_at = user.status.expires
            if isinstance(user.status, UserStatusEmpty):
                online_at = "статус пользователя еще не определен"
        user_premium = "Пользователь с premium" if user.premium else ""

        entities.append(
            [username, user.id, user.access_hash, first_name, last_name, user_phone, online_at, photos_id,
             user_premium])

    async def get_active_user_data(self, user):
        """Получаем данные пользователя"""
        username = user.username if user.username else "NONE"
        user_phone = user.phone if user.phone else "Номер телефона скрыт"
        first_name = user.first_name if user.first_name else ""
        last_name = user.last_name if user.last_name else ""
        photos_id = (
            "Пользователь с фото" if isinstance(user.photo, types.UserProfilePhoto) else "Пользователь без фото")
        online_at = "Был(а) недавно"
        # Статусы пользователя https://core.telegram.org/type/UserStatus
        if isinstance(user.status, (
                UserStatusRecently, UserStatusOffline, UserStatusLastWeek, UserStatusLastMonth, UserStatusOnline,
                UserStatusEmpty)):
            if isinstance(user.status, UserStatusOffline):
                online_at = user.status.was_online
            if isinstance(user.status, UserStatusRecently):
                online_at = "Был(а) недавно"
            if isinstance(user.status, UserStatusLastWeek):
                online_at = "Был(а) на этой неделе"
            if isinstance(user.status, UserStatusLastMonth):
                online_at = "Был(а) в этом месяце"
            if isinstance(user.status, UserStatusOnline):
                online_at = user.status.expires
            if isinstance(user.status, UserStatusEmpty):
                online_at = "статус пользователя еще не определен"
        user_premium = "Пользователь с premium" if user.premium else ""

        entity = (username, user.id, user.access_hash,
                  first_name, last_name, user_phone,
                  online_at, photos_id, user_premium)

        return entity

    async def forming_a_list_of_groups(self, client) -> None:
        """Формируем список групп"""
        async for dialog in client.iter_dialogs():
            try:
                dialog_id = dialog.id
                ch = await client.get_entity(dialog_id)
                result = await client(functions.channels.GetFullChannelRequest(channel=ch))
                chs = await client.get_entity(result.full_chat)
                chat_about = result.full_chat.about
                chs_title = chs.title
                username = chs.username
                # Получение количества участников в группе или канале
                if hasattr(result.full_chat, "participants_count"):
                    members_count = result.full_chat.participants_count
                else:
                    members_count = 0
                # Запишите время синтаксического анализа
                parsing_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                log_message = f"{dialog_id}, {chs_title}, {chat_about}, https://t.me/{username}, {members_count}, {parsing_time}"
                logger.info(log_message)
                entities = [dialog_id, chs_title, chat_about, f"https://t.me/{username}", members_count, parsing_time]
                await self.db_handler.write_data_to_db(
                    creating_a_table="CREATE TABLE IF NOT EXISTS groups_and_channels(id, title, about, link, members_count, parsing_time)",
                    writing_data_to_a_table="INSERT INTO groups_and_channels (id, title, about, link, members_count, parsing_time) VALUES (?, ?, ?, ?, ?, ?)",
                    entities=entities)
            except TypeError:
                continue  # Записываем ошибку в software_database.db и продолжаем работу
