# -*- coding: utf-8 -*-
import asyncio  # Импортируем библиотеку для работы с асинхронным кодом
import re  # Импортируем библиотеку для работы с регулярными выражениями
import sys  # Импортируем библиотеку для работы с системным вызовом

import flet as ft  # Импортируем библиотеку flet
from loguru import logger  # Импортируем библиотеку loguru для логирования
from telethon.tl.functions.messages import GetMessagesViewsRequest

from src.core.configs import path_accounts_folder
from src.core.utils import find_filess
from src.features.account.TGConnect import TGConnect
from src.features.account.subscribe_unsubscribe.subscribe_unsubscribe import SubscribeUnsubscribeTelegram
from src.gui.buttons import function_button_ready_viewing
from src.gui.gui import log_and_display


class ViewingPosts:
    """
    Накрутка просмотров постов
    """

    def __init__(self, page):
        self.page = page
        self.tg_connect = TGConnect(page=page)
        self.sub_unsub_tg = SubscribeUnsubscribeTelegram(page=page)

    async def viewing_posts_request(self) -> None:
        """
        Ставим реакции на сообщения
        """
        try:
            # Поле для ввода ссылки на чат
            link_channel = ft.TextField(label="Введите ссылку на канал:", multiline=False, max_lines=1)
            link_post = ft.TextField(label="Введите ссылку на пост:", multiline=False, max_lines=1)

            async def btn_click(_) -> None:

                for session_name in find_filess(directory_path=path_accounts_folder, extension='session'):
                    client = await self.tg_connect.get_telegram_client(page, session_name,
                                                                       account_directory=path_accounts_folder)
                    await log_and_display(f"[+] Работаем с каналом: {link_channel.value}", page)
                    await self.sub_unsub_tg.subscribe_to_group_or_channel(client, link_channel.value, page)
                    msg_id = int(re.search(r'/(\d+)$', link_post.value).group(1))  # Получаем id сообщения из ссылки
                    await self.viewing_posts(client, link_post.value, msg_id, link_channel.value, page)
                    await asyncio.sleep(1)
                    await client.disconnect()
                    # Изменение маршрута на новый (если необходимо)
                    page.go("/viewing_posts_menu")
                    page.update()  # Обновление страницы для отображения изменений

            def back_button_clicked(_) -> None:
                """Кнопка возврата в меню накрутки просмотров"""
                page.go("/viewing_posts_menu")

            function_button_ready_viewing(page, btn_click, back_button_clicked, link_channel, link_post)

        except Exception as error:
            logger.exception(error)

    async def viewing_posts(self, client, link_post, number, link_channel) -> None:
        """
        Накрутка просмотров постов

        :param client: Клиент для работы с Telegram
        :param link_post: Ссылка на пост
        :param number: Количество просмотров
        :param link_channel: Ссылка на канал
        :param page: Страница интерфейса Flet для отображения элементов управления.
        :return: None
        """
        try:
            try:
                await self.sub_unsub_tg.subscribe_to_group_or_channel(client, link_channel, page)
                channel = await client.get_entity(link_channel)  # Получение информации о канале
                await asyncio.sleep(5)
                await log_and_display(f"Ссылка на пост: {link_post}\n", page)
                await asyncio.sleep(5)
                await client(GetMessagesViewsRequest(peer=channel, id=[int(number)], increment=True))
            except KeyError:
                sys.exit(1)
        except Exception as error:
            logger.exception(error)
