# -*- coding: utf-8 -*-
import asyncio
import random

import flet as ft  # Импортируем библиотеку flet
from loguru import logger
from telethon import functions, types
from telethon.errors import (AuthKeyUnregisteredError, ChannelPrivateError,
                             ChannelsTooMuchError, FloodWaitError,
                             InviteHashExpiredError, InviteHashInvalidError,
                             InviteRequestSentError, PeerFloodError,
                             SessionPasswordNeededError, SessionRevokedError,
                             UserDeactivatedBanError, UsernameInvalidError,
                             UserNotParticipantError)
from telethon.tl.functions.channels import (JoinChannelRequest,
                                            LeaveChannelRequest)
from telethon.tl.functions.messages import ImportChatInviteRequest

from src.core.configs import (BUTTON_HEIGHT, line_width_button,
                              path_accounts_folder, time_subscription_1,
                              time_subscription_2)
from src.core.sqlite_working_tools import db_handler
from src.core.utils import find_filess, record_and_interrupt
from src.features.account.TGConnect import TGConnect
from src.gui.gui import end_time, list_view, log_and_display, start_time
from src.locales.translations_loader import translations


class SubscribeUnsubscribeTelegram:

    def __init__(self):
        self.tg_connect = TGConnect()

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
    async def checking_links(page: ft.Page, client, link) -> None:
        """
        Проверка ссылок на подписку

        :param page: Страница интерфейса Flet для отображения элементов управления.
        :param client: Клиент Telegram
        :param link: Ссылка на подписку
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
                                              page)
                        try:
                            await log_and_display(f"Подписка на группу / канал по ссылке приглашению {link}", page)
                            try:
                                await client(ImportChatInviteRequest(
                                    link_hash))  # Подписка на группу / канал по ссылке приглашению
                            except InviteHashInvalidError:
                                await log_and_display(translations["ru"]["errors"]["invite_request_sent"], page)
                        except InviteHashExpiredError:
                            await log_and_display(translations["ru"]["errors"]["subscribe_error"], page)
                            try:
                                await client(ImportChatInviteRequest(
                                    link_hash))  # Подписка на группу / канал по ссылке приглашению
                                await log_and_display(f"Подписка на группу / канал по ссылке приглашению {link_hash}",
                                                      page)
                            except InviteHashInvalidError:
                                await log_and_display(translations["ru"]["errors"]["invite_request_sent"], page)
                    elif isinstance(result, types.ChatInviteAlready):
                        await log_and_display(
                            f"Вы уже состоите в группе: {link}, Название группы: {result.chat.title}", page)
                except FloodWaitError as e:
                    await log_and_display(f"{translations["ru"]["errors"]["flood_wait"]}{e}", page, level="error")

            elif link.startswith("https://t.me/"):
                # Извлекаем имя пользователя или группы
                username = link.split("/")[-1]
                result = await client(functions.contacts.ResolveUsernameRequest(username=username))
                chat = result.chats[0] if result.chats else None
                if chat:
                    await log_and_display(f"Публичная группа/канал: {link}, Название: {chat.title}, "
                                          f"Количество участников: {chat.participants_count if hasattr(chat, 'participants_count') else 'Неизвестно'}, "
                                          f"Мега-группа: {'Да' if getattr(chat, 'megagroup', False) else 'Нет'}",
                                          page)
                    await client(JoinChannelRequest(link))
                else:
                    await log_and_display(f"Не удалось найти публичный чат: {link}", page)

            else:
                # Считаем, что это просто хэш
                try:
                    result = await client(functions.messages.CheckChatInviteRequest(hash=link))
                    if isinstance(result, types.ChatInvite):
                        await log_and_display(f"Ссылка валидна: {link}, Название группы: {result.title}, "
                                              f"Количество участников: {result.participants_count}, "
                                              f"Мега-группа: {'Да' if result.megagroup else 'Нет'}, "
                                              f"Описание: {result.about or 'Нет описания'}",
                                              page)
                        await client(JoinChannelRequest(link))
                    elif isinstance(result, types.ChatInviteAlready):
                        await log_and_display(
                            f"Вы уже состоите в группе: {link}, Название группы: {result.chat.title}", page)
                except FloodWaitError as e:
                    await log_and_display(f"{translations["ru"]["errors"]["flood_wait"]}{e}", page, level="error")
                except InviteHashExpiredError:
                    await log_and_display(f"Повторная проверка ссылки: {link}", page)
                    result = await client(functions.contacts.ResolveUsernameRequest(username=link))
                    chat = result.chats[0] if result.chats else None
                    if chat:
                        await log_and_display(f"Публичная группа/канал: {link}, Название: {chat.title}, "
                                              f"Количество участников: {chat.participants_count if hasattr(chat, 'participants_count') else 'Неизвестно'}, "
                                              f"Мега-группа: {'Да' if getattr(chat, 'megagroup', False) else 'Нет'}",
                                              page)
                    else:
                        await log_and_display(f"Не удалось найти публичный чат: {link}", page)

                except AuthKeyUnregisteredError:
                    await log_and_display(translations["ru"]["errors"]["auth_key_unregistered"], page)
                    await asyncio.sleep(2)
                except SessionPasswordNeededError:
                    await log_and_display(translations["ru"]["errors"]["two_factor_required"], page)
                    await asyncio.sleep(2)

        except FloodWaitError as e:
            await log_and_display(f"{translations["ru"]["errors"]["flood_wait"]}{e}", page, level="error")
        except InviteRequestSentError:
            await log_and_display(translations["ru"]["errors"]["invite_request_sent"], page)
        except AuthKeyUnregisteredError:
            await log_and_display(translations["ru"]["errors"]["auth_key_unregistered"], page)
            await asyncio.sleep(2)
        except SessionPasswordNeededError:
            await log_and_display(translations["ru"]["errors"]["two_factor_required"], page)
            await asyncio.sleep(2)

    async def subscribe_telegram(self, page: ft.Page) -> None:
        """
        Подписка на группы / каналы Telegram

        :param page: Страница интерфейса Flet для отображения элементов управления.
        """
        # TODO реализовать проверку ссылок перед подпиской, что бы пользователи не подсовывали программе не рабочие
        #  ссылки или ссылки которые не являются группой или каналом

        page.controls.append(list_view)  # добавляем ListView на страницу для отображения логов 📝
        page.update()  # обновляем страницу, чтобы сразу показать ListView 🔄

        async def add_items(_):
            start = await start_time(page)
            for session_name in await find_filess(directory_path=path_accounts_folder, extension='session'):
                client = await self.tg_connect.get_telegram_client(page, session_name,
                                                                   account_directory=path_accounts_folder)
                # Получение ссылки
                links_inviting: list = await db_handler.open_and_read_data(table_name="writing_group_links",
                                                                           page=page)  # Открываем базу данных
                await log_and_display(f"Ссылка для подписки и проверки:  {links_inviting}", page)
                for link_tuple in links_inviting:
                    link = link_tuple[0]
                    await log_and_display(f"Ссылка для подписки и проверки:  {link}", page)
                    # Проверка ссылок для подписки и подписка на группу или канал
                    await self.checking_links(page, client, link)
                await client.disconnect()
            await end_time(start, page)

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
                    ft.ElevatedButton(width=line_width_button, height=BUTTON_HEIGHT,
                                      text=translations["ru"]["buttons"]["back"],
                                      on_click=back_button_clicked)  # Кнопка "⬅️ Назад"
                ],
            )
        )

        page.update()  # обновляем страницу после добавления элементов управления 🔄

    async def unsubscribe_all(self, page: ft.Page) -> None:
        """
        Отписываемся от групп, каналов, личных сообщений

        :param page: Страница интерфейса Flet для отображения элементов управления.
        """
        try:
            for session_name in await find_filess(directory_path=path_accounts_folder, extension='session'):
                client = await self.tg_connect.get_telegram_client(page, session_name,
                                                                   account_directory=path_accounts_folder)
                dialogs = client.iter_dialogs()
                await log_and_display(f"Диалоги: {dialogs}", page)
                async for dialog in dialogs:
                    await log_and_display(f"{dialog.name}, {dialog.id}", page)
                    await client.delete_dialog(dialog)
                await client.disconnect()
        except Exception as error:
            logger.exception(error)

    @staticmethod
    async def unsubscribe_from_the_group(client, group_link, page: ft.Page) -> None:
        """
        Отписываемся от группы.

        :param group_link: Группа или канал
        :param client: Телеграм клиент
        :param page: Страница интерфейса Flet для отображения элементов управления.
        """
        try:
            entity = await client.get_entity(group_link)
            if entity:
                await client(LeaveChannelRequest(entity))
        except ChannelPrivateError:  # Аккаунт Telegram не может отписаться так как не имеет доступа
            await log_and_display(translations["ru"]["errors"]["channel_private"], page)
        except UserNotParticipantError:
            await log_and_display(translations["ru"]["errors"]["unsubscribe_not_member"], page)
        except Exception as error:
            logger.exception(error)
        finally:
            await client.disconnect()  # Разрываем соединение с Telegram

    async def subscribe_to_group_or_channel(self, client, groups_wr, page: ft.Page) -> None:
        """
        Подписываемся на группу или канал

        :param groups_wr: str - группа или канал
        :param client:    TelegramClient - объект клиента
        :param page: Страница интерфейса Flet для отображения элементов управления.
        """
        # цикл for нужен для того, что бы сработала команда brake команда break в Python используется только для выхода из
        # цикла, а не выхода из программы в целом.
        await log_and_display(f"Группа для подписки {groups_wr}", page)
        try:
            await client(JoinChannelRequest(groups_wr))
            await log_and_display(f"Аккаунт подписался на группу / канал: {groups_wr}", page)
            client.disconnect()
        except SessionRevokedError:
            await log_and_display(translations["ru"]["errors"]["invalid_auth_session_terminated"], page)
        except UserDeactivatedBanError:
            await log_and_display(f"❌ Попытка подписки на группу / канал {groups_wr}. Аккаунт заблокирован.", page)
        except ChannelsTooMuchError:
            """Если аккаунт подписан на множество групп и каналов, то отписываемся от них"""
            async for dialog in client.iter_dialogs():
                await log_and_display(f"{dialog.name}, {dialog.id}", page)
                try:
                    await client.delete_dialog(dialog)
                    await client.disconnect()
                except ConnectionError:
                    break
            await log_and_display(f"❌  Список почистили, и в файл записали.", page)
        except ChannelPrivateError:
            await log_and_display(translations["ru"]["errors"]["channel_private"], page)
        except (UsernameInvalidError, ValueError, TypeError):
            await log_and_display(
                f"❌ Попытка подписки на группу / канал {groups_wr}. Не верное имя или cсылка {groups_wr} не является группой / каналом: {groups_wr}",
                page)
            await db_handler.write_data_to_db("""SELECT *
                                                      from writing_group_links""",
                                              """DELETE
                                                 from writing_group_links
                                                 where writing_group_links = ?""",
                                              groups_wr, page)
        except PeerFloodError:
            await log_and_display(translations["ru"]["errors"]["peer_flood"], page, level="error")
            await asyncio.sleep(random.randrange(50, 60))
        except FloodWaitError as e:
            await log_and_display(f"{translations["ru"]["errors"]["flood_wait"]}{e}", page, level="error")
            await record_and_interrupt(time_subscription_1, time_subscription_2, page)
            # Прерываем работу и меняем аккаунт
            raise
        except InviteRequestSentError:
            await log_and_display(
                f"❌ Попытка подписки на группу / канал {groups_wr}. Действия будут доступны после одобрения администратором на вступление в группу",
                page)
        except Exception as error:
            logger.exception(error)
