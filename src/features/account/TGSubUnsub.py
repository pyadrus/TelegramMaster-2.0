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
                             InviteHashExpiredError, InviteHashInvalidError, AuthKeyUnregisteredError,
                             SessionPasswordNeededError, UserNotParticipantError)
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.channels import LeaveChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest

from src.core.configs import (ConfigReader, path_subscription_folder, path_unsubscribe_folder, line_width_button,
                              BUTTON_HEIGHT)
from src.core.localization import back_button
from src.core.sqlite_working_tools import DatabaseHandler
from src.core.utils import record_and_interrupt, find_filess
from src.features.account.TGConnect import TGConnect
from src.gui.menu import log_and_display


class SubscribeUnsubscribeTelegram:

    def __init__(self):
        self.db_handler = DatabaseHandler()
        self.tg_connect = TGConnect()
        self.time_subscription_1, self.time_subscription_2 = ConfigReader().get_time_subscription()

    @staticmethod
    async def extract_channel_id(link):
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

    @staticmethod
    async def checking_links(page: ft.Page, client, link, list_view) -> None:
        """
        Проверка ссылок на подписку

        :param page: Страница интерфейса Flet для отображения элементов управления.
        :param client: Клиент Telegram
        :param link: Ссылка на подписку
        :param list_view: Лог-уровень
        """
        try:
            if link.startswith("https://t.me/+"):
                # Извлекаем хэш из ссылки на приглашение
                link_hash = link.split("+")[-1]
                try:
                    result = await client(functions.messages.CheckChatInviteRequest(hash=link_hash))
                    if isinstance(result, types.ChatInvite):
                        await log_and_display(f"Ссылка валидна: {link}, Название группы: {result.title}, "
                                              f"Количество участников: {result.participants_count}, "
                                              f"Мега-группа: {'Да' if result.megagroup else 'Нет'}, Описание: {result.about or 'Нет описания'}",
                                              list_view, page)
                        try:
                            await log_and_display(f"Подписка на группу / канал по ссылке приглашению {link}", list_view,
                                                  page)
                            try:
                                await client(ImportChatInviteRequest(
                                    link_hash))  # Подписка на группу / канал по ссылке приглашению
                            except InviteHashInvalidError:
                                await log_and_display(
                                    f"Отправлена заявка на вступление в группу / канал по ссылке приглашению {link}",
                                    list_view, page)
                        except InviteHashExpiredError as error:
                            await log_and_display(
                                f"Ошибка при подписке на группу / канал по ссылке приглашению {error}", list_view, page)
                            try:
                                await client(ImportChatInviteRequest(
                                    link_hash))  # Подписка на группу / канал по ссылке приглашению
                                await log_and_display(f"Подписка на группу / канал по ссылке приглашению {link_hash}",
                                                      list_view, page)
                            except InviteHashInvalidError:
                                await log_and_display(
                                    f"Отправлена заявка на вступление в группу / канал по ссылке приглашению {link}",
                                    list_view, page)
                    elif isinstance(result, types.ChatInviteAlready):
                        await log_and_display(
                            f"Вы уже состоите в группе: {link}, Название группы: {result.chat.title}", list_view, page)
                except FloodWaitError as e:
                    await log_and_display(f"❌ Попытка подписки на группу / канал {link}. Flood! wait for "
                                          f"{str(datetime.timedelta(seconds=e.seconds))}", list_view, page)

            elif link.startswith("https://t.me/"):
                # Извлекаем имя пользователя или группы
                username = link.split("/")[-1]
                result = await client(functions.contacts.ResolveUsernameRequest(username=username))
                chat = result.chats[0] if result.chats else None
                if chat:
                    await log_and_display(f"Публичная группа/канал: {link}, Название: {chat.title}, "
                                          f"Количество участников: {chat.participants_count if hasattr(chat, 'participants_count') else 'Неизвестно'}, "
                                          f"Мега-группа: {'Да' if getattr(chat, 'megagroup', False) else 'Нет'}",
                                          list_view, page)
                    await client(JoinChannelRequest(link))
                else:
                    await log_and_display(f"Не удалось найти публичный чат: {link}", list_view, page)

            else:
                # Считаем, что это просто хэш
                try:
                    result = await client(functions.messages.CheckChatInviteRequest(hash=link))
                    if isinstance(result, types.ChatInvite):
                        await log_and_display(f"Ссылка валидна: {link}, Название группы: {result.title}, "
                                              f"Количество участников: {result.participants_count}, "
                                              f"Мега-группа: {'Да' if result.megagroup else 'Нет'}, "
                                              f"Описание: {result.about or 'Нет описания'}",
                                              list_view, page)
                        await client(JoinChannelRequest(link))
                    elif isinstance(result, types.ChatInviteAlready):
                        await log_and_display(
                            f"Вы уже состоите в группе: {link}, Название группы: {result.chat.title}", list_view, page)
                except FloodWaitError as e:
                    await log_and_display(
                        f"❌ Попытка подписки на группу / канал {link}. Flood! wait for {str(datetime.timedelta(seconds=e.seconds))}",
                        list_view, page, level="error")
                except InviteHashExpiredError:
                    await log_and_display(f"Повторная проверка ссылки: {link}", list_view, page)
                    result = await client(functions.contacts.ResolveUsernameRequest(username=link))
                    chat = result.chats[0] if result.chats else None
                    if chat:
                        await log_and_display(f"Публичная группа/канал: {link}, Название: {chat.title}, "
                                              f"Количество участников: {chat.participants_count if hasattr(chat, 'participants_count') else 'Неизвестно'}, "
                                              f"Мега-группа: {'Да' if getattr(chat, 'megagroup', False) else 'Нет'}",
                                              list_view, page)
                    else:
                        await log_and_display(f"Не удалось найти публичный чат: {link}", list_view, page)

                except AuthKeyUnregisteredError:
                    await log_and_display(
                        f"❌ Ошибка subscribing: неверный ключ авторизации аккаунта, выполните проверку аккаунтов",
                        list_view,
                        page, level="error")
                    await asyncio.sleep(2)

                except SessionPasswordNeededError:
                    await log_and_display(
                        f"❌ Ошибка subscribing: ошибка авторизации аккаунта, выполните проверку аккаунтов", list_view,
                        page,
                        level="error")
                    await asyncio.sleep(2)

        except FloodWaitError as e:
            await log_and_display(
                f"❌ Попытка подписки на группу / канал {link}. Flood! wait for {str(datetime.timedelta(seconds=e.seconds))}",
                list_view, page, level="error")
        except InviteRequestSentError:
            await log_and_display(f"Отправлена заявка на вступление в группу / канал по ссылке приглашению {link}",
                                  list_view,
                                  page, level="error")

        except AuthKeyUnregisteredError:
            await log_and_display(
                f"❌ Ошибка subscribing: неверный ключ авторизации аккаунта, выполните проверку аккаунтов", list_view,
                page,
                level="error")
            await asyncio.sleep(2)

        except SessionPasswordNeededError:
            await log_and_display(f"❌ Ошибка subscribing: ошибка авторизации аккаунта, выполните проверку аккаунтов",
                                  list_view, page, level="error")
            await asyncio.sleep(2)

    async def subscribe_telegram(self, page: ft.Page) -> None:
        """
        Подписка на группы / каналы Telegram

        :param page: Страница интерфейса Flet для отображения элементов управления.
        """
        # TODO реализовать проверку ссылок перед подпиской, что бы пользователи не подсовывали программе не рабочие
        #  ссылки или ссылки которые не являются группой или каналом

        list_view = ft.ListView(expand=10, spacing=1, padding=2, auto_scroll=True)
        page.controls.append(list_view)  # добавляем ListView на страницу для отображения логов 📝
        page.update()  # обновляем страницу, чтобы сразу показать ListView 🔄

        async def add_items(_):
            start = datetime.datetime.now()  # фиксируем время начала выполнения кода ⏱️
            # Индикация начала инвайтинга
            await log_and_display(f"\n▶️ Начало Подписки.\n🕒 Время старта: {str(start)}", list_view, page)
            for session_name in await find_filess(directory_path=path_subscription_folder, extension='session'):
                client = await self.tg_connect.get_telegram_client(page, session_name,
                                                                   account_directory=path_subscription_folder,
                                                                   list_view=list_view)
                # Получение ссылки
                links_inviting: list = await self.db_handler.open_and_read_data(table_name="writing_group_links",
                                                                                list_view=list_view,
                                                                                page=page)  # Открываем базу данных
                await log_and_display(f"Ссылка для подписки и проверки:  {links_inviting}", list_view, page)
                for link_tuple in links_inviting:
                    link = link_tuple[0]
                    await log_and_display(f"Ссылка для подписки и проверки:  {link}", list_view, page)
                    # Проверка ссылок для подписки и подписка на группу или канал
                    await self.checking_links(page, client, link, list_view)
                await client.disconnect()
            finish = datetime.datetime.now()  # фиксируем и выводим время окончания работы кода
            await log_and_display(f"🔚 Конец Подписки.\n🕒 Время окончания: {finish}.\n"
                                  f"⏳ Время работы: {finish - start}\n", list_view, page)

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
                    list_view,  # Отображение логов 📝
                    ft.Column(),  # Резерв для приветствия или других элементов интерфейса
                    ft.ElevatedButton(width=line_width_button, height=BUTTON_HEIGHT, text="🚀 Начать подписку",
                                      on_click=add_items),  # Кнопка "🚀 Начать подписку"
                    ft.ElevatedButton(width=line_width_button, height=BUTTON_HEIGHT, text=back_button,
                                      on_click=back_button_clicked)  # Кнопка "⬅️ Назад"
                ],
            )
        )

        page.update()  # обновляем страницу после добавления элементов управления 🔄

    async def unsubscribe_all(self, page: ft.Page, list_view) -> None:
        """
        Отписываемся от групп, каналов, личных сообщений

        :param page: Страница интерфейса Flet для отображения элементов управления.
        :param list_view: ListView для отображения логов.
        """
        try:
            for session_name in await find_filess(directory_path=path_unsubscribe_folder, extension='session'):
                client = await self.tg_connect.get_telegram_client(page, session_name,
                                                                   account_directory=path_unsubscribe_folder,
                                                                   list_view=list_view)
                dialogs = client.iter_dialogs()
                await log_and_display(f"Диалоги: {dialogs}", list_view, page)
                async for dialog in dialogs:
                    await log_and_display(f"{dialog.name}, {dialog.id}", list_view, page)
                    await client.delete_dialog(dialog)
                await client.disconnect()
        except Exception as error:
            logger.exception(f"❌ Ошибка: {error}")

    @staticmethod
    async def unsubscribe_from_the_group(client, group_link, list_view, page: ft.Page) -> None:
        """
        Отписываемся от группы.

        :param group_link: Группа или канал
        :param client: Телеграм клиент
        :param list_view: ListView для отображения логов.
        :param page: Страница интерфейса Flet для отображения элементов управления.
        """
        try:
            entity = await client.get_entity(group_link)
            if entity:
                await client(LeaveChannelRequest(entity))
        except ChannelPrivateError:  # Аккаунт Telegram не может отписаться так как не имеет доступа
            await log_and_display(
                f"Группа или канал: {group_link}, является закрытым или аккаунт не имеет доступ  к {group_link}",
                list_view, page)
        except UserNotParticipantError:
            await log_and_display(f"❌ Попытка отписки от группы / канала {group_link}. Аккаунт не является участником.",
                                  list_view, page)
        except Exception as error:
            logger.exception(f"❌ Ошибка: {error}")
        finally:
            await client.disconnect()  # Разрываем соединение с Telegram

    async def subscribe_to_group_or_channel(self, client, groups_wr, list_view, page: ft.Page) -> None:
        """
        Подписываемся на группу или канал

        :param groups_wr: str - группа или канал
        :param client:    TelegramClient - объект клиента
        :param list_view: ListView для отображения логов.
        :param page: Страница интерфейса Flet для отображения элементов управления.
        """
        # цикл for нужен для того, что бы сработала команда brake команда break в Python используется только для выхода из
        # цикла, а не выхода из программы в целом.
        await log_and_display(f"Группа для подписки {groups_wr}", list_view, page)
        try:
            await client(JoinChannelRequest(groups_wr))
            await log_and_display(f"Аккаунт подписался на группу / канал: {groups_wr}", list_view, page)
        except SessionRevokedError:
            await log_and_display(
                f"❌ Попытка подписки на группу / канал {groups_wr}. Авторизация была признана недействительной из-за того, что пользователь завершил все сеансы.",
                list_view, page)
        except UserDeactivatedBanError:
            await log_and_display(f"❌ Попытка подписки на группу / канал {groups_wr}. Аккаунт заблокирован.", list_view,
                                  page)
        except ChannelsTooMuchError:
            """Если аккаунт подписан на множество групп и каналов, то отписываемся от них"""
            async for dialog in client.iter_dialogs():
                await log_and_display(f"{dialog.name}, {dialog.id}", list_view, page)
                try:
                    await client.delete_dialog(dialog)
                    await client.disconnect()
                except ConnectionError:
                    break
            await log_and_display(f"❌  Список почистили, и в файл записали.", list_view, page)
        except ChannelPrivateError:
            await log_and_display(
                f"❌ Попытка подписки на группу / канал {groups_wr}. Указанный канал / группа {groups_wr} является приватным, или вам запретили подписываться.",
                list_view, page)
        except (UsernameInvalidError, ValueError, TypeError):
            await log_and_display(
                f"❌ Попытка подписки на группу / канал {groups_wr}. Не верное имя или cсылка {groups_wr} не является группой / каналом: {groups_wr}",
                list_view, page)
            await self.db_handler.write_data_to_db("""SELECT *
                                                      from writing_group_links""",
                                                   """DELETE
                                                      from writing_group_links
                                                      where writing_group_links = ?""",
                                                   groups_wr, list_view, page)
        except PeerFloodError:
            await log_and_display(
                f"❌ Попытка подписки на группу / канал {groups_wr}. Предупреждение о Flood от Telegram.", list_view,
                page)
            await asyncio.sleep(random.randrange(50, 60))
        except FloodWaitError as e:
            await log_and_display(
                f"❌ Попытка подписки на группу / канал {groups_wr}. Flood! wait for {str(datetime.timedelta(seconds=e.seconds))}",
                list_view, page)
            await record_and_interrupt(self.time_subscription_1, self.time_subscription_2, list_view, page)
            # Прерываем работу и меняем аккаунт
            raise
        except InviteRequestSentError:
            await log_and_display(
                f"❌ Попытка подписки на группу / канал {groups_wr}. Действия будут доступны после одобрения администратором на вступление в группу",
                list_view, page)
        except Exception as error:
            logger.exception(f"❌ Ошибка: {error}")
