# -*- coding: utf-8 -*-
import asyncio # Импортируем библиотеку для работы с асинхронным кодом
import re # Импортируем библиотеку для работы с регулярными выражениями
import sys # Импортируем библиотеку для работы с системным вызовом

import flet as ft  # Импортируем библиотеку flet
from loguru import logger  # Импортируем библиотеку loguru для логирования
from telethon import types
from telethon.tl.functions.messages import SendReactionRequest, GetMessagesViewsRequest

from system.account_actions.TGConnect import TGConnect
from system.account_actions.TGSubUnsub import SubscribeUnsubscribeTelegram
from system.auxiliary_functions.auxiliary_functions import find_filess
from system.auxiliary_functions.config import path_reactions_folder, path_viewing_folder
from system.localization.localization import done_button
from system.sqlite_working_tools.sqlite_working_tools import DatabaseHandler


class ViewingPosts:  # Класс для работы с реакциями

    def __init__(self):
        self.db_handler = DatabaseHandler()
        self.tg_connect = TGConnect()
        self.sub_unsub_tg = SubscribeUnsubscribeTelegram()

    async def send_reaction_request(self, page: ft.Page) -> None:
        """
        Ставим реакции на сообщения
        """
        try:
            # Поле для ввода ссылки на чат
            chat = ft.TextField(label="Введите ссылку на группу / чат:", multiline=False, max_lines=1)
            message = ft.TextField(label="Введите ссылку на сообщение или пост:", multiline=False, max_lines=1)

            async def btn_click(e) -> None:
                # random_value = await self.choosing_random_reaction()  # Выбираем случайное значение из списка (реакция)
                for session_name in find_filess(directory_path=path_reactions_folder, extension='session'):
                    client = await self.tg_connect.get_telegram_client(session_name,
                                                                       account_directory=path_reactions_folder)

                    logger.info(f'[+] Работаем с группой: {chat.value}')
                    await self.sub_unsub_tg.subscribe_to_group_or_channel(client, chat.value)
                    msg_id = int(re.search(r'/(\d+)$', message.value).group(1))  # Получаем id сообщения из ссылки
                    await asyncio.sleep(5)
                    await client(SendReactionRequest(peer=chat.value, msg_id=msg_id,
                                                     reaction=[types.ReactionEmoji(
                                                         emoticon=f'{self.choosing_random_reaction()}')]))
                    await asyncio.sleep(1)
                    await client.disconnect()

                    # Изменение маршрута на новый (если необходимо)
                    page.go("/working_with_reactions")
                    page.update()  # Обновление страницы для отображения изменений

            # Кнопка для подтверждения и запуска парсинга
            button = ft.ElevatedButton(done_button, on_click=btn_click)

            # Добавление представления на страницу
            page.views.append(
                ft.View(
                    "/working_with_reactions",  # Маршрут для этого представления
                    [
                        chat,  # Поле ввода ссылки на чат
                        message,  # Поле ввода ссылки пост
                        # limit_active_user, # Поле ввода количества сообщений
                        ft.Column(),  # Колонка для размещения других элементов (при необходимости)
                        button  # Кнопка "Готово"
                    ]
                )
            )
        except Exception as error:
            logger.exception(f"Ошибка: {error}")


    async def viewing_posts(self) -> None:
        """
        Накрутка просмотров постов
        """
        try:
            for session_name in find_filess(directory_path=path_viewing_folder, extension='session'):
                client = await self.tg_connect.get_telegram_client(session_name, account_directory=path_viewing_folder)
                records: list = await self.db_handler.open_and_read_data("writing_group_links")  # Открываем базу данных
                logger.info(f"Всего групп: {len(records)}")
                for groups in records:  # Поочередно выводим записанные группы
                    logger.info(f"Группа: {groups}")
                    try:
                        await self.sub_unsub_tg.subscribe_to_group_or_channel(client, groups[0])
                        channel = await client.get_entity(groups[0])  # Получение информации о канале
                        await asyncio.sleep(5)

                        for post in await client.get_messages(channel, limit=10):  # Вывод информации о постах, Получение последних 10 постов из канала
                            logger.info(f"Ссылка на пост:",
                                        f"{groups[0]}/{post.id}\nDate: {post.date}\nText: {post.text}\n")
                            number = re.search(r"/(\d+)$", f"{groups[0]}/{post.id}").group(1)
                            await asyncio.sleep(5)
                            await client(GetMessagesViewsRequest(peer=channel, id=[int(number)], increment=True))
                    except KeyError:
                        sys.exit(1)
                    finally:
                        client.disconnect()
        except Exception as error:
            logger.exception(f"Ошибка: {error}")
