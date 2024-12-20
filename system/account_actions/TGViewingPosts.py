# -*- coding: utf-8 -*-
import asyncio  # Импортируем библиотеку для работы с асинхронным кодом
import re  # Импортируем библиотеку для работы с регулярными выражениями
import sys  # Импортируем библиотеку для работы с системным вызовом

import flet as ft  # Импортируем библиотеку flet
from loguru import logger  # Импортируем библиотеку loguru для логирования
from telethon.tl.functions.messages import GetMessagesViewsRequest

from system.account_actions.TGConnect import TGConnect
from system.account_actions.TGSubUnsub import SubscribeUnsubscribeTelegram
from system.utils.utils import find_filess
from system.config.configs import path_viewing_folder
from system.localization.localization import done_button
from system.sqlite_working_tools.sqlite_working_tools import DatabaseHandler


class ViewingPosts:
    """
    Класс для накрутки просмотров постов
    """

    def __init__(self):
        self.db_handler = DatabaseHandler()
        self.tg_connect = TGConnect()
        self.sub_unsub_tg = SubscribeUnsubscribeTelegram()

    async def viewing_posts_request(self, page: ft.Page) -> None:
        """
        Ставим реакции на сообщения

        Аргументы:
        :param page: Страница интерфейса Flet для отображения элементов управления.
        :return: None
        """
        try:
            # Поле для ввода ссылки на чат
            link_channel = ft.TextField(label="Введите ссылку на канал:", multiline=False, max_lines=1)
            link_post = ft.TextField(label="Введите ссылку на пост:", multiline=False, max_lines=1)

            async def btn_click(e) -> None:

                for session_name in find_filess(directory_path=path_viewing_folder, extension='session'):
                    client = await self.tg_connect.get_telegram_client(page, session_name,
                                                                       account_directory=path_viewing_folder)
                    logger.info(f'[+] Работаем с каналом: {link_channel.value}')
                    await self.sub_unsub_tg.subscribe_to_group_or_channel(client, link_channel.value)
                    msg_id = int(re.search(r'/(\d+)$', link_post.value).group(1))  # Получаем id сообщения из ссылки
                    await self.viewing_posts(client, link_post.value, msg_id, link_channel.value)
                    await asyncio.sleep(1)
                    await client.disconnect()
                    # Изменение маршрута на новый (если необходимо)
                    page.go("/viewing_posts_menu")
                    page.update()  # Обновление страницы для отображения изменений

            # Кнопка для подтверждения и запуска парсинга
            button = ft.ElevatedButton(done_button, on_click=btn_click)

            # Добавление представления на страницу
            page.views.append(
                ft.View(
                    "/working_with_reactions",  # Маршрут для этого представления
                    [
                        link_channel,  # Поле ввода ссылки на чат
                        link_post,  # Поле ввода ссылки пост
                        ft.Column(),  # Колонка для размещения других элементов (при необходимости)
                        button  # Кнопка "Готово"
                    ]
                )
            )
        except Exception as error:
            logger.exception(f"❌ Ошибка: {error}")

    async def viewing_posts(self, client, link_post, number, link_channel) -> None:
        """
        Накрутка просмотров постов

        Аргументы:
        :param client: Клиент для работы с Telegram
        :param link_post: Ссылка на пост
        :param number: Количество просмотров
        :param link_channel: Ссылка на канал
        :return: None
        """
        try:
            try:
                await self.sub_unsub_tg.subscribe_to_group_or_channel(client, link_channel)
                channel = await client.get_entity(link_channel)  # Получение информации о канале
                await asyncio.sleep(5)
                logger.info(f"Ссылка на пост: {link_post}\n")
                await asyncio.sleep(5)
                await client(GetMessagesViewsRequest(peer=channel, id=[int(number)], increment=True))
            except KeyError:
                sys.exit(1)
        except Exception as error:
            logger.exception(f"❌ Ошибка: {error}")
