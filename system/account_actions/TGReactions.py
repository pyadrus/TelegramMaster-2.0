# -*- coding: utf-8 -*-
import random
import re
import sys
import time

from loguru import logger  # Импортируем библиотеку loguru для логирования
from telethon import events, types
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import SendReactionRequest, GetMessagesViewsRequest

from system.account_actions.TGConnect import TGConnect
from system.account_actions.TGLimits import SettingLimits
from system.account_actions.TGSubUnsub import SubscribeUnsubscribeTelegram
from system.auxiliary_functions.auxiliary_functions import find_files
from system.auxiliary_functions.auxiliary_functions import read_json_file
from system.sqlite_working_tools.sqlite_working_tools import DatabaseHandler


class WorkingWithReactions:  # Класс для работы с реакциями

    def __init__(self):
        self.db_handler = DatabaseHandler()
        self.tg_connect = TGConnect()
        self.limits_class = SettingLimits()
        self.sub_unsub_tg = SubscribeUnsubscribeTelegram()

    async def send_reaction_request(self, records, chat, message_url, reaction_input) -> None:
        """Ставим реакции на сообщения"""
        message = input("[+] Введите ссылку на сообщение или пост: ")  # Ссылка на сообщение
        random_value = self.choosing_random_reaction()  # Выбираем случайное значение из списка (редакция)
        chat = input("[+] Введите ссылку на группу / канал: ")  # Ссылка на группу или канал

        entities = find_files(directory_path="user_settings/accounts/inviting", extension='session')
        for file in entities:
            client = await self.tg_connect.connect_to_telegram(file, directory_path="user_settings/accounts/inviting")

            try:
                # Открываем базу с группами для дальнейшего parsing
                records: list = await self.db_handler.open_and_read_data("writing_group_links")
                for groups in records:  # Поочередно выводим записанные группы
                    logger.info(f'[+] Парсинг группы: {groups[0]}')
                    await self.sub_unsub_tg.subscribe_to_group_or_channel(client, groups[0])

                    umber = re.search(r'/(\d+)$', message_url).group(1)
                    time.sleep(5)
                    await client(SendReactionRequest(peer=chat, msg_id=int(1),
                                               reaction=[types.ReactionEmoji(emoticon=f'{reaction_input}')]))
                    time.sleep(1)
            except KeyError:
                sys.exit(1)
            finally:
                await client.disconnect()

    async def viewing_posts(self) -> None:
        """Накрутка просмотров постов"""
        entities = find_files(directory_path="user_settings/accounts/inviting", extension='session')
        for file in entities:
            client = await self.tg_connect.connect_to_telegram(file, directory_path="user_settings/accounts/inviting")
            records: list = await self.db_handler.open_and_read_data("writing_group_links")  # Открываем базу данных
            logger.info(f"Всего групп: {len(records)}")
            for groups in records:  # Поочередно выводим записанные группы
                logger.info(f"Группа: {groups}")
                try:
                    await self.sub_unsub_tg.subscribe_to_group_or_channel(client, groups[0])
                    channel = await client.get_entity(groups[0])  # Получение информации о канале
                    time.sleep(5)
                    posts = await client.get_messages(channel, limit=10)  # Получение последних 10 постов из канала
                    for post in posts:  # Вывод информации о постах
                        logger.info(f"Ссылка на пост:", f"{groups[0]}/{post.id}\nDate: {post.date}\nText: {post.text}\n")
                        number = re.search(r"/(\d+)$", f"{groups[0]}/{post.id}").group(1)
                        time.sleep(5)
                        await client(GetMessagesViewsRequest(peer=channel, id=[int(number)], increment=True))
                except KeyError:
                    sys.exit(1)
                finally:
                    client.disconnect()

    async def choosing_random_reaction(self):
        """Выбираем случайное значение из списка (реакция)"""
        reaction_input = read_json_file(filename='user_settings/reactions/reactions.json')
        random_value = random.choice(reaction_input)  # Выбираем случайное значение из списка
        logger.info(random_value)
        return random_value

    async def reactions_for_groups_and_messages_test(self, number, chat) -> None:
        """Вводим ссылку на группу и ссылку на сообщение"""
        entities = find_files(directory_path="user_settings/accounts/reactions", extension='session')
        for file in entities:
            client = await self.tg_connect.connect_to_telegram(file, directory_path="user_settings/accounts/reactions")
            try:
                await client(JoinChannelRequest(chat))  # Подписываемся на канал / группу
                time.sleep(5)
                random_value = await self.choosing_random_reaction()  # Выбираем случайное значение из списка (редакция)
                await client(SendReactionRequest(peer=chat, msg_id=int(number),
                                                 reaction=[types.ReactionEmoji(emoticon=f'{random_value}')]))
                time.sleep(1)
            except KeyError:
                sys.exit(1)
            finally:
                await client.disconnect()

    async def setting_reactions(self):
        """Выставление реакций на новые посты"""
        entities = find_files(directory_path="user_settings/accounts/reactions", extension='session')
        for file in entities:
            client = await self.tg_connect.connect_to_telegram(file, directory_path="user_settings/accounts/reactions")
            records_ac_json = read_json_file(filename='user_settings/reactions/number_accounts.json')
            logger.info(records_ac_json)
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