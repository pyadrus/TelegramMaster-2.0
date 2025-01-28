# -*- coding: utf-8 -*-
import asyncio
import datetime
import random

import flet as ft  # Импортируем библиотеку flet
from loguru import logger
from telethon import functions
from telethon import types
from telethon.errors import (ChannelsTooMuchError, ChannelPrivateError, UsernameInvalidError, PeerFloodError,
                             FloodWaitError, InviteRequestSentError, UserDeactivatedBanError, SessionRevokedError,
                             InviteHashExpiredError, InviteHashInvalidError, AuthKeyUnregisteredError)
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.channels import LeaveChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest

from src.core.configs import (ConfigReader, path_subscription_folder, path_unsubscribe_folder, line_width_button,
                              height_button)
from src.core.localization import back_button
from src.core.sqlite_working_tools import DatabaseHandler
from src.core.utils import record_and_interrupt, find_filess
from src.features.account.TGConnect import TGConnect
from src.gui.menu import log_and_display_info, log_and_display_error


class SubscribeUnsubscribeTelegram:

    def __init__(self):
        self.db_handler = DatabaseHandler()
        self.tg_connect = TGConnect()
        self.time_subscription_1, self.time_subscription_2 = ConfigReader().get_time_subscription()

    async def extract_channel_id(self, link):
        """Сокращает ссылку с https://t.me/+yjqd0uZQETc4NGEy до yjqd0uZQETc4NGEy"""
        # Проверяем, начинается ли ссылка с 'https://t.me/'
        if link.startswith('https://t.me/'):
            return link[len('https://t.me/'):]
        # Если ссылка начинается просто с 't.me/', удалим 't.me/'
        elif link.startswith('t.me/'):
            return link[len('t.me/'):]
        # В остальных случаях возвращаем None
        else:
            return None

    async def checking_links(self, page, client, link, lv) -> None:
        """
        Проверка ссылок на подписку

        :param page: Страница интерфейса Flet для отображения элементов управления.
        :param client: Клиент Telegram
        :param link: Ссылка на подписку
        :param lv: Лог-уровень
        """
        try:
            if link.startswith("https://t.me/+"):
                # Извлекаем хэш из ссылки на приглашение
                link_hash = link.split("+")[-1]
                try:
                    result = await client(functions.messages.CheckChatInviteRequest(hash=link_hash))
                    if isinstance(result, types.ChatInvite):
                        await log_and_display_info(f"Ссылка валидна: {link}, Название группы: {result.title}, "
                                                   f"Количество участников: {result.participants_count}, "
                                                   f"Мега-группа: {'Да' if result.megagroup else 'Нет'}, Описание: {result.about or 'Нет описания'}",
                                                   lv, page)
                        try:
                            logger.info(f"Подписка на группу / канал по ссылке приглашению {link}")
                            try:
                                await client(ImportChatInviteRequest(
                                    link_hash))  # Подписка на группу / канал по ссылке приглашению
                            except InviteHashInvalidError:
                                await log_and_display_info(
                                    f"Отправлена заявка на вступление в группу / канал по ссылке приглашению {link}",
                                    lv, page)
                                logger.error(
                                    f"Отправлена заявка на вступление в группу / канал по ссылке приглашению {link}")
                        except InviteHashExpiredError as error:
                            logger.error(f"Ошибка при подписке на группу / канал по ссылке приглашению {error}")
                            try:
                                await client(ImportChatInviteRequest(
                                    link_hash))  # Подписка на группу / канал по ссылке приглашению
                                logger.info(f"Подписка на группу / канал по ссылке приглашению {link_hash}")
                            except InviteHashInvalidError:
                                await log_and_display_info(
                                    f"Отправлена заявка на вступление в группу / канал по ссылке приглашению {link}",
                                    lv, page)
                                logger.error(
                                    f"Отправлена заявка на вступление в группу / канал по ссылке приглашению {link}")
                    elif isinstance(result, types.ChatInviteAlready):
                        await log_and_display_info(
                            f"Вы уже состоите в группе: {link}, Название группы: {result.chat.title}", lv, page)
                except FloodWaitError as e:
                    await log_and_display_error(f"❌ Попытка подписки на группу / канал {link}. Flood! wait for "
                                                f"{str(datetime.timedelta(seconds=e.seconds))}", lv, page)

            elif link.startswith("https://t.me/"):
                # Извлекаем имя пользователя или группы
                username = link.split("/")[-1]
                result = await client(functions.contacts.ResolveUsernameRequest(username=username))
                chat = result.chats[0] if result.chats else None
                if chat:
                    await log_and_display_info(f"Публичная группа/канал: {link}, Название: {chat.title}, "
                                               f"Количество участников: {chat.participants_count if hasattr(chat, 'participants_count') else 'Неизвестно'}, "
                                               f"Мега-группа: {'Да' if getattr(chat, 'megagroup', False) else 'Нет'}",
                                               lv, page)
                    logger.info(f"Публичная группа/канал: {link}, Название: {chat.title}")
                    await client(JoinChannelRequest(link))
                else:
                    await log_and_display_info(f"Не удалось найти публичный чат: {link}", lv, page)

            else:
                # Считаем, что это просто хэш
                try:
                    result = await client(functions.messages.CheckChatInviteRequest(hash=link))
                    if isinstance(result, types.ChatInvite):
                        await log_and_display_info(f"Ссылка валидна: {link}, Название группы: {result.title}, "
                                                   f"Количество участников: {result.participants_count}, "
                                                   f"Мега-группа: {'Да' if result.megagroup else 'Нет'}, "
                                                   f"Описание: {result.about or 'Нет описания'}",
                                                   lv, page)
                        await client(JoinChannelRequest(link))
                    elif isinstance(result, types.ChatInviteAlready):
                        await log_and_display_info(
                            f"Вы уже состоите в группе: {link}, Название группы: {result.chat.title}", lv, page)
                except FloodWaitError as e:
                    await log_and_display_error(f"❌ Попытка подписки на группу / канал {link}. Flood! wait for "
                                                f"{str(datetime.timedelta(seconds=e.seconds))}", lv, page)
                except InviteHashExpiredError:
                    await log_and_display_info(f"Повторная проверка ссылки: {link}", lv, page)
                    result = await client(functions.contacts.ResolveUsernameRequest(username=link))
                    chat = result.chats[0] if result.chats else None
                    if chat:
                        await log_and_display_info(f"Публичная группа/канал: {link}, Название: {chat.title}, "
                                                   f"Количество участников: {chat.participants_count if hasattr(chat, 'participants_count') else 'Неизвестно'}, "
                                                   f"Мега-группа: {'Да' if getattr(chat, 'megagroup', False) else 'Нет'}",
                                                   lv, page)
                    else:
                        await log_and_display_info(f"Не удалось найти публичный чат: {link}", lv, page)

                except AuthKeyUnregisteredError:
                    logger.info(f'❌ Ошибка subscribing: неверный ключ авторизации аккаунта, выполните проверку аккаунтов')
                    await log_and_display_error(f"❌ Ошибка subscribing: неверный ключ авторизации аккаунта, выполните проверку аккаунтов", lv, page)
                    await asyncio.sleep(2)

        except FloodWaitError as e:
            await log_and_display_error(f"❌ Попытка подписки на группу / канал {link}. Flood! wait for "
                                        f"{str(datetime.timedelta(seconds=e.seconds))}", lv, page)
        except InviteRequestSentError:
            await log_and_display_info(
                f"Отправлена заявка на вступление в группу / канал по ссылке приглашению {link}",
                lv, page
            )
            logger.info(f"Отправлена заявка на вступление в группу / канал по ссылке приглашению {link}")

        except AuthKeyUnregisteredError:
            logger.info(f'❌ Ошибка subscribing: неверный ключ авторизации аккаунта, выполните проверку аккаунтов')
            await log_and_display_error(f"❌ Ошибка subscribing: неверный ключ авторизации аккаунта, выполните проверку аккаунтов", lv, page)
            await asyncio.sleep(2)

    async def subscribe_telegram(self, page: ft.Page) -> None:
        """
        Подписка на группы / каналы Telegram

        :param page: Страница интерфейса Flet для отображения элементов управления.
        """
        # TODO реализовать проверку ссылок перед подпиской, что бы пользователи не подсовывали программе не рабочие
        #  ссылки или ссылки которые не являются группой или каналом

        lv = ft.ListView(expand=10, spacing=1, padding=2, auto_scroll=True)
        page.controls.append(lv)  # добавляем ListView на страницу для отображения логов 📝
        page.update()  # обновляем страницу, чтобы сразу показать ListView 🔄

        async def add_items(_):
            start = datetime.datetime.now()  # фиксируем время начала выполнения кода ⏱️
            # Индикация начала инвайтинга
            await log_and_display_info(f"\n▶️ Начало Подписки.\n🕒 Время старта: {str(start)}", lv, page)
            for session_name in find_filess(directory_path=path_subscription_folder, extension='session'):
                client = await self.tg_connect.get_telegram_client(page, session_name,
                                                                   account_directory=path_subscription_folder)
                # Получение ссылки
                links_inviting: list = await self.db_handler.open_and_read_data(
                    "writing_group_links")  # Открываем базу данных
                logger.info(f"Ссылка для подписки и проверки:  {links_inviting}")
                for link_tuple in links_inviting:
                    link = link_tuple[0]
                    await log_and_display_info(f"Ссылка для подписки и проверки:  {link}", lv, page)
                    # Проверка ссылок для подписки и подписка на группу или канал
                    await self.checking_links(page, client, link, lv)
                await client.disconnect()
            finish = datetime.datetime.now()  # фиксируем и выводим время окончания работы кода
            await log_and_display_info(f"🔚 Конец Подписки.\n🕒 Время окончания: {finish}.\n"
                                       f"⏳ Время работы: {finish - start}\n", lv, page)

        async def back_button_clicked(_):
            """
            ⬅️ Обрабатывает нажатие кнопки "Назад", возвращая в меню подписки на группы / каналы Telegram.
            """
            page.go("/subscribe_unsubscribe")  # Переходим к основному меню подписки на группы / каналы Telegram. 🏠

        # Добавляем кнопки и другие элементы управления на страницу
        page.views.append(
            ft.View(
                "/subscription_all",
                [
                    ft.Text(value="Подписка на группы / каналы Telegram"),  # Выбор группы для инвайтинга
                    lv,  # Отображение логов 📝
                    ft.Column(),  # Резерв для приветствия или других элементов интерфейса
                    ft.ElevatedButton(width=line_width_button, height=height_button, text="🚀 Начать подписку",
                                      on_click=add_items),  # Кнопка "🚀 Начать подписку"
                    ft.ElevatedButton(width=line_width_button, height=height_button, text=back_button,
                                      on_click=back_button_clicked)  # Кнопка "⬅️ Назад"
                ],
            )
        )

        page.update()  # обновляем страницу после добавления элементов управления 🔄

    async def unsubscribe_all(self, page) -> None:
        """
        Отписываемся от групп, каналов, личных сообщений

        :param page: Страница интерфейса Flet для отображения элементов управления.
        """
        try:
            for session_name in find_filess(directory_path=path_unsubscribe_folder, extension='session'):
                client = await self.tg_connect.get_telegram_client(page, session_name,
                                                                   account_directory=path_unsubscribe_folder)
                dialogs = client.iter_dialogs()
                logger.info(f"Диалоги: {dialogs}")
                async for dialog in dialogs:
                    logger.info(f"{dialog.name}, {dialog.id}")
                    await client.delete_dialog(dialog)
                await client.disconnect()
        except Exception as error:
            logger.exception(f"❌ Ошибка: {error}")

    @staticmethod
    async def unsubscribe_from_the_group(client, group_link) -> None:
        """
        Отписываемся от группы.

        :param group_link: Группа или канал
        :param client: Телеграм клиент
        """
        try:
            entity = await client.get_entity(group_link)
            if entity:
                await client(LeaveChannelRequest(entity))
        except ChannelPrivateError:  # Аккаунт Telegram не может отписаться так как не имеет доступа
            logger.error(
                f'Группа или канал: {group_link}, является закрытым или аккаунт не имеет доступ  к {group_link}')
        except Exception as error:
            logger.exception(f"❌ Ошибка: {error}")
        finally:
            await client.disconnect()  # Разрываем соединение с Telegram

    async def subscribe_to_group_or_channel(self, client, groups_wr) -> None:
        """
        Подписываемся на группу или канал

        :param groups_wr: str - группа или канал
        :param client:    TelegramClient - объект клиента
        """
        # цикл for нужен для того, что бы сработала команда brake команда break в Python используется только для выхода из
        # цикла, а не выхода из программы в целом.
        logger.info(f"Группа для подписки {groups_wr}")
        try:
            await client(JoinChannelRequest(groups_wr))
            logger.info(f"Аккаунт подписался на группу / канал: {groups_wr}")
        except SessionRevokedError:
            logger.error(
                f"❌ Попытка подписки на группу / канал {groups_wr}. Авторизация была признана недействительной из-за того, что пользователь завершил все сеансы.")
        except UserDeactivatedBanError:
            logger.error(f"❌ Попытка подписки на группу / канал {groups_wr}. Аккаунт заблокирован.")
        except ChannelsTooMuchError:
            """Если аккаунт подписан на множество групп и каналов, то отписываемся от них"""
            async for dialog in client.iter_dialogs():
                logger.info(f"{dialog.name}, {dialog.id}")
                try:
                    await client.delete_dialog(dialog)
                    await client.disconnect()
                except ConnectionError:
                    break
            logger.info("❌  Список почистили, и в файл записали.")
        except ChannelPrivateError:
            logger.error(f"❌ Попытка подписки на группу / канал {groups_wr}. Указанный канал / группа {groups_wr} "
                         f"является приватным, или вам запретили подписываться.")
        except (UsernameInvalidError, ValueError, TypeError):
            logger.error(
                f"❌ Попытка подписки на группу / канал {groups_wr}. Не верное имя или cсылка {groups_wr} не "
                f"является группой / каналом: {groups_wr}")
            await self.db_handler.write_data_to_db("""SELECT * from writing_group_links""",
                                                   """DELETE from writing_group_links where writing_group_links = ?""",
                                                   groups_wr)
        except PeerFloodError:
            logger.error(f"❌ Попытка подписки на группу / канал {groups_wr}. Предупреждение о Flood от Telegram.")
            await asyncio.sleep(random.randrange(50, 60))
        except FloodWaitError as e:
            logger.error(f"❌ Попытка подписки на группу / канал {groups_wr}. Flood! wait for "
                         f"{str(datetime.timedelta(seconds=e.seconds))}")
            await record_and_interrupt(self.time_subscription_1, self.time_subscription_2)
            # Прерываем работу и меняем аккаунт
            raise
        except InviteRequestSentError:
            logger.error(f"❌ Попытка подписки на группу / канал {groups_wr}. Действия будут доступны после одобрения "
                         f"администратором на вступление в группу")
        except Exception as error:
            logger.exception(f"❌ Ошибка: {error}")
