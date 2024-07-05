# -*- coding: utf-8 -*-
import random
import sys
import time

from loguru import logger  # Импортируем библиотеку loguru для логирования
from telethon import TelegramClient
from telethon import events, types
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import SendReactionRequest, GetMessagesViewsRequest

from system.auxiliary_functions.auxiliary_functions import find_files
from system.auxiliary_functions.auxiliary_functions import read_json_file
from system.proxy.checking_proxy import reading_proxy_data_from_the_database
from system.sqlite_working_tools.sqlite_working_tools import DatabaseHandler


class WorkingWithReactions:  # Класс для работы с реакциями

    def __init__(self):
        self.db_handler = DatabaseHandler()

    async def users_choice_of_reaction(self) -> None:
        """Выбираем реакцию для выставления в чате / канале"""
        chat = input("[+] Введите ссылку на группу / канал: ")  # Ссылка на группу или канал
        message = input("[+] Введите ссылку на сообщение или пост: ")  # Ссылка на сообщение
        records: list = await self.choosing_a_number_of_reactions()  # Выбираем лимиты для аккаунтов
        random_value = choosing_random_reaction()  # Выбираем случайное значение из списка (редакция)
        self.send_reaction_request(records, chat, message, random_value)  # Ставим реакцию на пост, сообщение

    async def choosing_a_number_of_reactions(self) -> list:
        """Выбираем лимиты для аккаунтов"""
        # Открываем базу данных для работы с аккаунтами user_settings/software_database.db
        records: list = await self.db_handler.open_and_read_data("config")
        # Количество аккаунтов на данный момент в работе
        logger.info(f"Введите количество с которых будут поставлены реакции\nВсего accounts: {len(records)}")
        # Открываем базу данных для работы с аккаунтами user_settings/software_database.db
        number_of_accounts = input("[+] Введите количество аккаунтов для выставления реакций: ")
        records: list = await self.db_handler.open_the_db_and_read_the_data_lim(name_database_table="config",
                                                                          number_of_accounts=int(number_of_accounts))
        return records

    def send_reaction_request(self, records, chat, message_url, reaction_input) -> None:
        """Ставим реакции на сообщения"""
        for row in records:
            # Подключение к Telegram и вывод имени аккаунта в консоль / терминал
            client, phone = telegram_connect_and_output_name(row, self.db_handler)
            try:
                subscribe_to_group_or_channel(client, chat)  # Подписываемся на группу
                number = re.search(r'/(\d+)$', message_url).group(1)
                time.sleep(5)
                client(SendReactionRequest(peer=chat, msg_id=int(number),
                                           reaction=[types.ReactionEmoji(emoticon=f'{reaction_input}')]))
                time.sleep(1)
            except KeyError:
                sys.exit(1)
            finally:
                client.disconnect()

    def viewing_posts(self) -> None:
        """Накрутка просмотров постов"""
        chat = input("[+] Введите ссылку на канал: ")  # Ссылка на группу или канал
        records: list = await self.db_handler.open_and_read_data("config")
        # Количество аккаунтов на данный момент в работе
        logger.info(f"Всего accounts: {len(records)}")
        # Открываем базу данных для работы с аккаунтами user_settings/software_database.db
        number_of_accounts = input("[+] Введите количество аккаунтов для просмотра постов: ")
        records: list = await self.db_handler.open_the_db_and_read_the_data_lim(name_database_table="config",
                                                                     number_of_accounts=int(number_of_accounts))
        for row in records:
            # Подключение к Telegram и вывод имени аккаунта в консоль / терминал
            client, phone = telegram_connect_and_output_name(row)
            try:
                subscribe_to_group_or_channel(client, chat)  # Подписываемся на группу
                channel = client.get_entity(chat)  # Получение информации о канале
                time.sleep(5)
                posts = client.get_messages(channel, limit=10)  # Получение последних 10 постов из канала
                for post in posts:  # Вывод информации о постах
                    logger.info(f"Ссылка на пост:", f"{chat}/{post.id}\nDate: {post.date}\nText: {post.text}\n")
                    number = re.search(r"/(\d+)$", f"{chat}/{post.id}").group(1)
                    time.sleep(5)
                    client(GetMessagesViewsRequest(peer=channel, id=[int(number)], increment=True))
            except KeyError:
                sys.exit(1)
            finally:
                client.disconnect()

    def choosing_random_reaction(self):
        """Выбираем случайное значение из списка (реакция)"""
        reaction_input = read_json_file(filename='user_settings/reactions/reactions.json')
        random_value = random.choice(reaction_input)  # Выбираем случайное значение из списка
        logger.info(random_value)
        return random_value

    async def reactions_for_groups_and_messages_test(self, number, chat) -> None:
        """Вводим ссылку на группу и ссылку на сообщение"""
        # Открываем базу данных для работы с аккаунтами user_settings/software_database.db
        records: list = await self.db_handler.open_and_read_data("config")
        # Количество аккаунтов на данный момент в работе
        logger.info(f"Всего accounts: {len(records)}")
        number_of_accounts = read_json_file(filename='user_settings/reactions/number_accounts.json')
        logger.info(f'Всего реакций на пост: {number_of_accounts}')
        records: list = await self.db_handler.open_the_db_and_read_the_data_lim(name_database_table="config",
                                                                     number_of_accounts=int(number_of_accounts))
        for row in records:
            # Подключение к Telegram и вывод имени аккаунта в консоль / терминал
            proxy = reading_proxy_data_from_the_database(db_handler)  # Proxy IPV6 - НЕ РАБОТАЮТ
            client = TelegramClient(f"user_settings/accounts/{row[2]}", int(row[0]), row[1],
                                    system_version="4.16.30-vxCUSTOM", proxy=proxy)
            await client.connect()  # Подсоединяемся к Telegram
            try:
                await client(JoinChannelRequest(chat))  # Подписываемся на канал / группу
                time.sleep(5)
                random_value = self.choosing_random_reaction()  # Выбираем случайное значение из списка (редакция)
                await client(SendReactionRequest(peer=chat, msg_id=int(number),
                                                 reaction=[types.ReactionEmoji(emoticon=f'{random_value}')]))
                time.sleep(1)
            except KeyError:
                sys.exit(1)
            finally:
                client.disconnect()

    def writing_names_found_files_to_the_db_config_reactions(self) -> None:
        """Запись названий найденных файлов в базу данных"""
        await self.db_handler.cleaning_db(name_database_table="config_reactions")  # Call the method on the instance
        records = find_files(directory_path="user_settings/reactions/accounts", extension='session')
        for entities in records:
            logger.info(f"Записываем данные аккаунта {entities} в базу данных")
            await self.db_handler.write_data_to_db("CREATE TABLE IF NOT EXISTS config_reactions (id, hash, phone)",
                                        "INSERT INTO config_reactions (id, hash, phone) VALUES (?, ?, ?)", entities)

    async def setting_reactions(self):
        """Выставление реакций на новые посты"""
        self.writing_names_found_files_to_the_db_config_reactions()

        # Открываем базу данных для работы с аккаунтами user_settings/software_database.db
        records_ac: list = await self.db_handler.open_and_read_data("config_reactions")
        # Количество аккаунтов на данный момент в работе
        logger.info(f"Всего accounts: {len(records_ac)}")
        records_ac_json = read_json_file(filename='user_settings/reactions/number_accounts.json')
        logger.info(records_ac_json)
        records: list = await self.db_handler.open_the_db_and_read_the_data_lim(name_database_table="config_reactions",
                                                                     number_of_accounts=int(records_ac_json))
        logger.info(records)
        for row in records:
            client = await telegram_connects(db_handler, session=f"user_settings/reactions/accounts/{row[2]}")
            chat = read_json_file(filename='user_settings/reactions/link_channel.json')
            logger.info(chat)
            await client(JoinChannelRequest(chat))  # Подписываемся на канал / группу

            @client.on(events.NewMessage(chats=chat))
            async def handler(event):
                message = event.message  # Получаем сообщение из события
                message_id = message.id  # Получаем id сообщение
                logger.info(f"Идентификатор сообщения: {message_id}, {message}")
                # Проверяем, является ли сообщение постом и не является ли оно нашим
                if message.post and not message.out:
                    await event.reactions_for_groups_and_messages_test(message_id, chat)

        client.run_until_disconnected()  # Запуск клиента