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

from src.core.configs import path_accounts_folder
from src.core.utils import find_filess, read_json_file
from src.features.account.TGConnect import TGConnect
from src.features.account.TGSubUnsub import SubscribeUnsubscribeTelegram
from src.gui.buttons import function_button_ready_reactions
from src.gui.gui import log_and_display
from src.locales.translations_loader import translations


class WorkingWithReactions:
    """
    Класс для работы с реакциями
    """

    def __init__(self):
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

            async def btn_click(_) -> None:
                # random_value = await self.choosing_random_reaction()  # Выбираем случайное значение из списка (реакция)
                for session_name in await find_filess(directory_path=path_accounts_folder, extension='session'):
                    client = await self.tg_connect.get_telegram_client(page, session_name,
                                                                       account_directory=path_accounts_folder)
                    await log_and_display(f"[+] Работаем с группой: {chat.value}", page)
                    await self.sub_unsub_tg.subscribe_to_group_or_channel(client, chat.value, page)
                    msg_id = int(re.search(r'/(\d+)$', message.value).group(1))  # Получаем id сообщения из ссылки
                    await asyncio.sleep(5)
                    try:
                        await client(SendReactionRequest(
                            peer=chat.value, msg_id=msg_id,
                            reaction=[types.ReactionEmoji(emoticon=f'{self.choosing_random_reaction(page)}')]))
                        await asyncio.sleep(1)
                        await client.disconnect()
                    except ReactionInvalidError:
                        await log_and_display(f"Ошибка : Предоставлена неверная реакция", page)
                        await asyncio.sleep(1)
                        await client.disconnect()

                    # Изменение маршрута на новый (если необходимо)
                    page.go("/working_with_reactions")
                    page.update()  # Обновление страницы для отображения изменений

            def back_button_clicked(_) -> None:
                """Кнопка возврата в меню проставления реакций"""
                page.go("/working_with_reactions")

            function_button_ready_reactions(page, btn_click, back_button_clicked, chat, message)

        except Exception as error:
            logger.exception(error)

    @staticmethod
    async def choosing_random_reaction(page):
        """Выбираем случайное значение из списка (реакция)"""
        try:
            random_value = random.choice(read_json_file(filename='user_data/reactions/reactions.json'))
            await log_and_display(f"{random_value}", page)
            return random_value
        except Exception as error:
            logger.exception(error)
            return None

    async def reactions_for_groups_and_messages_test(self, number, chat, page: ft.Page) -> None:
        """
        Вводим ссылку на группу и ссылку на сообщение

        :param number: Ссылка на сообщение
        :param chat: Ссылка на группу
        :param page: Страница интерфейса Flet для отображения элементов управления.
        """
        try:
            for session_name in await find_filess(directory_path="user_data/accounts/reactions_list",
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
                                                         emoticon=f'{self.choosing_random_reaction(page)}')]))
                    await asyncio.sleep(1)
                    await client.disconnect()
                except ReactionInvalidError:
                    await log_and_display(translations["ru"]["errors"]["invalid_reaction"], page)
                    await asyncio.sleep(1)
                    await client.disconnect()
        except Exception as error:
            logger.exception(error)

    async def setting_reactions(self, page: ft.Page) -> None:
        """
        Выставление реакций на новые посты
        """
        try:
            for session_name in await find_filess(directory_path=path_accounts_folder, extension='session'):
                client = await self.tg_connect.get_telegram_client(page, session_name,
                                                                   account_directory=path_accounts_folder)
                chat = read_json_file(filename='user_data/reactions/link_channel.json')
                await log_and_display(f"{chat}", page)
                await client(JoinChannelRequest(chat))  # Подписываемся на канал / группу

                @client.on(events.NewMessage(chats=chat))
                async def handler(event):
                    message = event.message  # Получаем сообщение из события
                    message_id = message.id  # Получаем id сообщение
                    await log_and_display(f"Идентификатор сообщения: {message_id}, {message}", page)
                    # Проверяем, является ли сообщение постом и не является ли оно нашим
                    if message.post and not message.out:
                        await self.reactions_for_groups_and_messages_test(message_id, chat, page)

                await client.run_until_disconnected()  # Запуск клиента в режиме ожидания событий
        except Exception as error:
            logger.exception(error)
