# -*- coding: utf-8 -*-
import asyncio
import random
import re

import flet as ft  # Импортируем библиотеку flet
from loguru import logger  # Импортируем библиотеку loguru для логирования
from telethon import events, types
from telethon.errors import ReactionInvalidError
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import SendReactionRequest

from src.features.account.TGConnect import TGConnect
from src.features.account.TGSubUnsub import SubscribeUnsubscribeTelegram
from src.core.configs import path_reactions_folder
from src.gui.buttons import function_button_ready_reactions
from src.core.sqlite_working_tools import DatabaseHandler
from src.core.utils import read_json_file, find_filess


class WorkingWithReactions:
    """
    Класс для работы с реакциями
    """

    def __init__(self):
        self.db_handler = DatabaseHandler()
        self.tg_connect = TGConnect()
        self.sub_unsub_tg = SubscribeUnsubscribeTelegram()

    async def send_reaction_request(self, page: ft.Page) -> None:
        """
        Ставим реакции на сообщения

        :param page: Страница интерфейса Flet для отображения элементов управления.
        """
        try:
            # Поле для ввода ссылки на чат
            chat = ft.TextField(label="Введите ссылку на группу / чат:", multiline=False, max_lines=1)
            message = ft.TextField(label="Введите ссылку на сообщение или пост:", multiline=False, max_lines=1)

            async def btn_click(e) -> None:
                # random_value = await self.choosing_random_reaction()  # Выбираем случайное значение из списка (реакция)
                for session_name in find_filess(directory_path=path_reactions_folder, extension='session'):
                    client = await self.tg_connect.get_telegram_client(page, session_name,
                                                                       account_directory=path_reactions_folder)

                    logger.info(f'[+] Работаем с группой: {chat.value}')
                    await self.sub_unsub_tg.subscribe_to_group_or_channel(client, chat.value)
                    msg_id = int(re.search(r'/(\d+)$', message.value).group(1))  # Получаем id сообщения из ссылки
                    await asyncio.sleep(5)
                    try:
                        await client(SendReactionRequest(peer=chat.value, msg_id=msg_id,
                                                         reaction=[types.ReactionEmoji(
                                                             emoticon=f'{self.choosing_random_reaction()}')]))
                        await asyncio.sleep(1)
                        await client.disconnect()
                    except ReactionInvalidError:
                        logger.info(f"Ошибка : Предоставлена неверная реакция")
                        await asyncio.sleep(1)
                        await client.disconnect()

                    # Изменение маршрута на новый (если необходимо)
                    page.go("/working_with_reactions")
                    page.update()  # Обновление страницы для отображения изменений

            def back_button_clicked(e) -> None:
                """Кнопка возврата в меню проставления реакций"""
                page.go("/working_with_reactions")

            function_button_ready_reactions(page, btn_click, back_button_clicked, chat, message)

        except Exception as error:
            logger.exception(f"❌ Ошибка: {error}")

    @staticmethod
    def choosing_random_reaction():
        """Выбираем случайное значение из списка (реакция)"""
        try:
            reaction_input = read_json_file(filename='user_data/reactions/reactions.json')
            random_value = random.choice(reaction_input)  # Выбираем случайное значение из списка
            logger.info(random_value)
            return random_value
        except Exception as error:
            logger.exception(f"❌ Ошибка: {error}")

    async def reactions_for_groups_and_messages_test(self, number, chat, page: ft.Page) -> None:
        """
        Вводим ссылку на группу и ссылку на сообщение

        :param number: Ссылка на сообщение
        :param chat: Ссылка на группу
        :param page: Страница интерфейса Flet для отображения элементов управления.
        """
        try:
            for session_name in find_filess(directory_path="user_data/accounts/reactions_list",
                                            # TODO переместить путь к файлу в конфиг файл
                                            extension='session'):
                client = await self.tg_connect.get_telegram_client(page, session_name,
                                                                   account_directory="user_data/accounts/reactions_list")
                await client(JoinChannelRequest(chat))  # Подписываемся на канал / группу
                await asyncio.sleep(5)
                # random_value = await self.choosing_random_reaction()  # Выбираем случайное значение из списка (редакция)
                try:
                    await client(SendReactionRequest(peer=chat, msg_id=int(number),
                                                     reaction=[types.ReactionEmoji(
                                                         emoticon=f'{self.choosing_random_reaction()}')]))
                    await asyncio.sleep(1)
                    await client.disconnect()
                except ReactionInvalidError:
                    logger.info(f"❌ Ошибка : Предоставлена неверная реакция")
                    await asyncio.sleep(1)
                    await client.disconnect()
        except Exception as error:
            logger.exception(f"❌ Ошибка: {error}")

    async def setting_reactions(self, page: ft.Page):
        """
        Выставление реакций на новые посты
        """
        try:
            for session_name in find_filess(directory_path=path_reactions_folder, extension='session'):
                client = await self.tg_connect.get_telegram_client(page, session_name,
                                                                   account_directory=path_reactions_folder)
                chat = read_json_file(
                    filename='user_data/reactions/link_channel.json')  # TODO переместить путь к файлу в конфиг
                logger.info(chat)
                await client(JoinChannelRequest(chat))  # Подписываемся на канал / группу

                @client.on(events.NewMessage(chats=chat))
                async def handler(event):
                    message = event.message  # Получаем сообщение из события
                    message_id = message.id  # Получаем id сообщение
                    logger.info(f"Идентификатор сообщения: {message_id}, {message}")
                    # Проверяем, является ли сообщение постом и не является ли оно нашим
                    if message.post and not message.out:
                        await self.reactions_for_groups_and_messages_test(message_id, chat, page)

                await client.run_until_disconnected()  # Запуск клиента в режиме ожидания событий
        except Exception as error:
            logger.exception(f"❌ Ошибка: {error}")
