# -*- coding: utf-8 -*-
import asyncio
import random
import sqlite3

import flet as ft  # Импортируем библиотеку flet
from loguru import logger
from telethon import functions, types
from telethon.errors import (AuthKeyUnregisteredError, ChannelPrivateError, ChannelsTooMuchError, FloodWaitError,
                             InviteHashExpiredError, InviteHashInvalidError, InviteRequestSentError, PeerFloodError,
                             SessionPasswordNeededError, SessionRevokedError, UserDeactivatedBanError,
                             UsernameInvalidError, UserNotParticipantError)
from telethon.tl.functions.channels import JoinChannelRequest, LeaveChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest

from src.core.configs import (BUTTON_HEIGHT, path_accounts_folder, time_subscription_1,
                              time_subscription_2, WIDTH_WIDE_BUTTON)
from src.core.sqlite_working_tools import write_data_to_db, write_writing_group_links_to_db, get_writing_group_links
from src.core.utils import find_filess, record_and_interrupt
from src.features.account.TGConnect import TGConnect
from src.features.account.parsing.gui_elements import GUIProgram
from src.features.account.subscribe_unsubscribe.subscribe_unsubscribe_gui import (SubscriptionLinkInputSection,
                                                                                  TimeIntervalInputSection)
from src.features.settings.setting import writing_settings_to_a_file, recording_limits_file
from src.gui.gui import end_time, list_view, log_and_display, start_time
from src.gui.notification import show_notification
from src.locales.translations_loader import translations


class SubscribeUnsubscribeTelegram:

    def __init__(self):
        self.tg_connect = TGConnect()

    async def subscribe_and_unsubscribe_menu(self, page: ft.Page):
        """
        Меню подписка и отписка

        :param page: Страница интерфейса Flet для отображения элементов управления.
        """

        page.controls.append(list_view)  # добавляем ListView на страницу для отображения логов 📝
        page.update()  # обновляем страницу, чтобы сразу показать ListView 🔄

        async def unsubscribe_all(_) -> None:
            """
            Отписываемся от групп, каналов, личных сообщений
            """
            start = await start_time(page)
            try:
                for session_name in find_filess(directory_path=path_accounts_folder, extension='session'):
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
            await end_time(start, page)

        async def add_items(_):
            """Подписываемся на группы и каналы"""
            start = await start_time(page)
            for session_name in find_filess(directory_path=path_accounts_folder, extension='session'):
                client = await self.tg_connect.get_telegram_client(page, session_name,
                                                                            account_directory=path_accounts_folder)
                if client is None:
                    logger.error("❌ Не удалось подключиться к Telegram")
                    # pass  # Пропустить аккаунт, если не удалось подключиться
                # string_session = string_session.session.save()
                # logger.info("📦 String session:", string_session)
                # Получение ссылки
                links_inviting: list = get_writing_group_links()  # Открываем базу данных
                await log_and_display(f"Ссылка для подписки и проверки:  {links_inviting}", page)
                for link_tuple in links_inviting:
                    # link = link_tuple[0]
                    await log_and_display(f"Ссылка для подписки и проверки:  {link_tuple}", page)
                    # Проверка ссылок для подписки и подписка на группу или канал
                    logger.info(f"Работа с аккаунтом {session_name}")
                    await self.checking_links(page, client, link_tuple)
                try:
                    await client.disconnect()
                except sqlite3.DatabaseError:
                    logger.error("❌ Не удалось подписаться на канал / группу, так как файл аккаунта повреждён")
            await end_time(start, page)

        async def save(e):
            """Сохраняет ссылки в базу данных в таблицу writing_group_links, для последующей подписки"""
            logger.info(f"Сохранение ссылок для подписки")
            writing_group_links = link_entry_field.value.strip().split()
            data_to_save = {
                "writing_group_links": writing_group_links,
            }
            write_writing_group_links_to_db(data_to_save)
            logger.info(f"Сохранение ссылок для подписки завершено")

        async def btn_click(_) -> None:
            """Обработчик клика по кнопке"""
            try:
                smaller_times = int(smaller_timex.value)
                larger_times = int(larger_timex.value)
                if smaller_times < larger_times:  # Проверяем, что первое время меньше второго
                    # Если условие прошло проверку, то возвращаем первое и второе время
                    writing_settings_to_a_file(
                        await recording_limits_file(str(smaller_times), str(larger_times), variable="time_subscription",
                                                    page=page))
                    list_view.controls.append(ft.Text("Данные успешно записаны!"))  # отображаем сообщение в ListView
                    await show_notification(page, "Данные успешно записаны!")
                    # page.go("/settings")  # Изменение маршрута в представлении существующих настроек
                else:
                    list_view.controls.append(ft.Text("Ошибка: первое время должно быть меньше второго!"))
            except ValueError:
                list_view.controls.append(ft.Text("Ошибка: введите числовые значения!"))
            page.update()  # обновляем страницу

        time_range = [time_subscription_1, time_subscription_2]
        page.controls.append(list_view)  # добавляем ListView на страницу для отображения логов 📝
        for time_range_message in time_range: list_view.controls.append(
            ft.Text(f"Записанные данные в файле {time_range_message}"))  # отображаем сообщение в ListView

        # Поле ввода ссылок и кнопка сохранения для подписки
        link_entry_field, save_button = await SubscriptionLinkInputSection().create_link_input_and_save_button(save)
        # Два поля ввода для времени и кнопка сохранить
        smaller_timex, larger_timex, save_button_time = await TimeIntervalInputSection().create_time_inputs_and_save_button(
            btn_click)

        page.views.append(
            ft.View("/subscribe_unsubscribe",
                    [await GUIProgram().key_app_bar(),
                     ft.Text(spans=[ft.TextSpan(
                         translations["ru"]["menu"]["subscribe_unsubscribe"],
                         ft.TextStyle(
                             size=20, weight=ft.FontWeight.BOLD,
                             foreground=ft.Paint(
                                 gradient=ft.PaintLinearGradient((0, 20), (150, 20), [ft.Colors.PINK,
                                                                                      ft.Colors.PURPLE])), ), ), ], ),

                     list_view,  # Отображение логов 📝

                     ft.Divider(),  # Горизонтальная линия
                     ft.Text(
                         value="⏱ Укажите интервал времени (в секундах) между подписками на группы.\n"
                               "🤖 После каждой подписки аккаунт сделает паузу на случайное время из указанного диапазона,\n"
                               "🔁 затем продолжит подписку на следующую группу.",
                         size=14
                     ),
                     await TimeIntervalInputSection().build_time_input_row(smaller_timex, larger_timex,
                                                                           save_button_time),
                     ft.Divider(),  # Горизонтальная линия
                     ft.Text(
                         value="🔗 Укажите ссылки на группы или каналы для подписки.\n"
                               "📌 Если вы уже вводили их ранее — ввод не обязателен, данные сохранены в системе.",
                         size=14
                     ),
                     await SubscriptionLinkInputSection().build_link_input_row(link_entry_field, save_button),
                     ft.Divider(),  # Горизонтальная линия
                     ft.Column([  # Добавляет все чекбоксы и кнопку на страницу (page) в виде колонок.
                         # 🔔 Подписка
                         ft.ElevatedButton(width=WIDTH_WIDE_BUTTON, height=BUTTON_HEIGHT,
                                           text=translations["ru"]["subscribe_unsubscribe_menu"]["subscription"],
                                           on_click=add_items),
                         # 🚫 Отписываемся
                         ft.ElevatedButton(width=WIDTH_WIDE_BUTTON, height=BUTTON_HEIGHT,
                                           text=translations["ru"]["subscribe_unsubscribe_menu"]["unsubscribe"],
                                           on_click=unsubscribe_all),
                     ])]))

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
                    logger.info(f"Подписка на группу / канал по ссылке {link}")
                    try:
                        await client(JoinChannelRequest(link))
                    except sqlite3.DatabaseError:
                        logger.error("❌ Не удалось подписаться на канал / группу, так как файл аккаунта повреждён")
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

    # async def subscribe_telegram(self, page: ft.Page) -> None:
    #     """
    #     Подписка на группы / каналы Telegram
    #
    #     :param page: Страница интерфейса Flet для отображения элементов управления.
    #     """
    #
    #     # TODO реализовать проверку ссылок перед подпиской, что бы пользователи не подсовывали программе не рабочие
    #     #  ссылки или ссылки которые не являются группой или каналом
    #
    #     async def back_button_clicked(_):
    #         """
    #         ⬅️ Обрабатывает нажатие кнопки "Назад", возвращая в меню подписки на группы / каналы Telegram.
    #         """
    #         page.go("/subscribe_unsubscribe")  # Переходим к основному меню подписки на группы / каналы Telegram. 🏠
    #
    #     # Добавляем кнопки и другие элементы управления на страницу
    #     page.views.append(
    #         ft.View(
    #             "/subscription_all",
    #             [
    #                 ft.Text(value="Подписка на группы / каналы Telegram"),  # Выбор группы для инвайтинга
    #                 list_view,  # Отображение логов 📝
    #                 ft.Column(),  # Резерв для приветствия или других элементов интерфейса
    #                 # ft.ElevatedButton(width=WIDTH_WIDE_BUTTON, height=BUTTON_HEIGHT, text="🚀 Начать подписку",
    #                 #                   on_click=add_items),  # Кнопка "🚀 Начать подписку"
    #                 ft.ElevatedButton(width=WIDTH_WIDE_BUTTON, height=BUTTON_HEIGHT,
    #                                   text=translations["ru"]["buttons"]["back"],
    #                                   on_click=back_button_clicked)  # Кнопка "⬅️ Назад"
    #             ],
    #         )
    #     )
    #
    #     page.update()  # обновляем страницу после добавления элементов управления 🔄

    @staticmethod
    async def unsubscribe_from_the_group(client, group_link, page: ft.Page) -> None:
        """
        Отписываемся от группы.

        :param group_link: Группа или канал
        :param client: Телеграм клиент
        :param page: Страница интерфейса Flet для отображения элементов управления.
        """
        logger.info(f"Отписываемся от группы: {group_link}")
        try:
            entity = await client.get_entity(group_link)
            if entity:
                await client(LeaveChannelRequest(entity))
            # await client.disconnect()  # Разрываем соединение с Telegram
        except ChannelPrivateError:  # Аккаунт Telegram не может отписаться так как не имеет доступа
            await log_and_display(translations["ru"]["errors"]["channel_private"], page)
        except UserNotParticipantError:
            await log_and_display(translations["ru"]["errors"]["unsubscribe_not_member"], page)
        except SessionRevokedError:
            await log_and_display(translations["ru"]["errors"]["invalid_auth_session_terminated"], page)
        except sqlite3.DatabaseError:
            await log_and_display(
                f"❌ Попытка подписки на группу / канал {group_link}. Ошибка базы данных, аккаунта или аккаунт заблокирован.",
                page)
        except ConnectionError:
            await log_and_display("Ошибка соединения с Telegram", page)
        # except Exception as error:
        #     logger.exception(error)

        # finally:
        #     await client.disconnect()  # Разрываем соединение с Telegram

    async def subscribe_to_group_or_channel(self, client, groups_wr, page: ft.Page) -> None:
        """
        Подписываемся на группу или канал

        :param groups_wr: Str - группа или канал
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
            write_data_to_db(groups_wr)
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
        except sqlite3.DatabaseError:
            await log_and_display(
                f"❌ Попытка подписки на группу / канал {groups_wr}. Ошибка базы данных, аккаунта или аккаунт заблокирован.",
                page)
        # except Exception as error:
        #     logger.exception(error)

# 409
