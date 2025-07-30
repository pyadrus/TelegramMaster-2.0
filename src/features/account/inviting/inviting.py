# -*- coding: utf-8 -*-
import asyncio
import datetime as dt

import flet as ft  # Импортируем библиотеку flet
from loguru import logger
from scheduler.asyncio import Scheduler
from telethon.errors import (AuthKeyDuplicatedError, ChannelPrivateError, SessionRevokedError, TypeNotFoundError,
                             UserBannedInChannelError, UserChannelsTooMuchError)
from telethon.sessions import StringSession
from telethon.sync import TelegramClient
from telethon.tl.functions.channels import InviteToChannelRequest

from src.core.configs import (BUTTON_HEIGHT, ConfigReader, LIMITS, WIDTH_WIDE_BUTTON, path_accounts_folder,
                              time_inviting_1, time_inviting_2)
from src.core.sqlite_working_tools import select_records_with_limit, get_links_inviting, save_links_inviting
from src.core.utils import find_filess, record_and_interrupt, record_inviting_results
from src.features.account.parsing.gui_elements import GUIProgram
from src.features.account.subscribe_unsubscribe.subscribe_unsubscribe import SubscribeUnsubscribeTelegram
from src.gui.gui import end_time, list_view, log_and_display, start_time
from src.gui.notification import show_notification
from src.locales.translations_loader import translations


async def getting_account_data(client, page):
    """Получаем данные аккаунта"""
    me = await client.get_me()
    logger.info(f"🧾 Аккаунт: {me.first_name} {me.last_name} | @{me.username} | ID: {me.id} | Phone: {me.phone}")
    await log_and_display(
        f"🧾 Аккаунт: {me.first_name} {me.last_name} | @{me.username} | ID: {me.id} | Phone: {me.phone}", page)


async def get_string_session(session_name):
    """Получение строки сессии"""

    client = TelegramClient(
        session=f"{path_accounts_folder}/{session_name}",
        api_id=7655060,
        api_hash="cc1290cd733c1f1d407598e5a31be4a8",
        system_version="4.16.30-vxCUSTOM",
    )
    await client.connect()
    logger.info(f"✨ STRING SESSION: {StringSession.save(client.session)}")
    session_string = StringSession.save(client.session)
    await client.disconnect()
    return session_string


async def add_user_test(client, username_group, username, page):
    try:
        await log_and_display(f"Попытка приглашения {username} в группу {username_group}.", page)
        await client.connect()
        await client(InviteToChannelRequest(username_group, [username]))
        await log_and_display(
            f"✅  Участник {username} добавлен, если не состоит в чате {username_group}. Спим от {time_inviting_1} до {time_inviting_2}",
            page)
        await record_inviting_results(time_inviting_1, time_inviting_2, username, page)
    except UserChannelsTooMuchError:
        await log_and_display(translations["ru"]["errors"]["user_channels_too_much"], page)
        await record_inviting_results(time_inviting_1, time_inviting_2, username, page)
    except (ChannelPrivateError, TypeNotFoundError, AuthKeyDuplicatedError, UserBannedInChannelError,
            SessionRevokedError):
        await log_and_display(translations["ru"]["errors"]["invalid_auth_session_terminated"], page)
        await record_and_interrupt(time_inviting_1, time_inviting_2, page)
        await client.disconnect()
    logger.info("👥 Приглашение пользователя прошло успешно!")


class InvitingToAGroup:

    def __init__(self, page: ft.Page):
        self.sub_unsub_tg = SubscribeUnsubscribeTelegram(page=page)
        # self.connect = TGConnect(page=page)
        self.config_reader = ConfigReader()
        self.hour, self.minutes = self.config_reader.get_hour_minutes_every_day()
        self.scheduler = Scheduler()  # Создаем экземпляр планировщика
        self.page = page
        self.config_reader = ConfigReader()
        self.api_id_api_hash = self.config_reader.get_api_id_data_api_hash_data()
        self.api_id = self.api_id_api_hash[0]
        self.api_hash = self.api_id_api_hash[1]

    async def inviting_menu(self):
        """
        Меню инвайтинг
        """
        list_view.controls.clear()  # ✅ Очистка логов перед новым запуском
        self.page.controls.append(list_view)  # Добавляем ListView на страницу для отображения логов 📝
        self.page.update()  # обновляем страницу, чтобы сразу показать ListView 🔄
        links_inviting = get_links_inviting()  # Получаем список ссылок на группы для инвайтинга из базы данных
        await self.data_for_inviting(self.page)  # Отображение информации о настройках инвайтинга

        async def general_invitation_to_the_group(_):
            """
            Основной метод для инвайтинга
            """
            start = await start_time(self.page)
            self.page.update()  # Обновите страницу, чтобы сразу показать сообщение 🔄
            # try:
            for session_name in find_filess(directory_path=path_accounts_folder, extension='session'):
                session_string = await get_string_session(session_name)
                # Создаем клиент, используя StringSession и вашу строку
                client = TelegramClient(
                    StringSession(session_string),  # <-- Используем StringSession
                    api_id=7655060,
                    api_hash="cc1290cd733c1f1d407598e5a31be4a8",
                    system_version="4.16.30-vxCUSTOM",
                )
                await client.connect()

                await getting_account_data(client, self.page)

                await SubscribeUnsubscribeTelegram(self.page).subscribe_to_group_or_channel(client, dropdown.value)
                logger.info(f"Подписка на группу {dropdown.value} выполнена")

                await log_and_display(f"{dropdown.value}", self.page)
                # Подписка на группу для инвайтинга

                # Получение списка usernames
                usernames = select_records_with_limit(limit=LIMITS)
                logger.info(f"Список usernames: {usernames}")
                if len(usernames) == 0:
                    await log_and_display(f"В таблице members нет пользователей для инвайтинга", self.page)
                    # await self.sub_unsub_tg.unsubscribe_from_the_group(client, dropdown.value, self.page)
                    break  # Прерываем работу и меняем аккаунт
                for username in usernames:
                    logger.info(f"Пользователь: {username}")
                    await log_and_display(f"Пользователь username: {username}", self.page)
                    # Инвайтинг в группу по полученному списку
                    try:
                        # await log_and_display(f"[DEBUG] Попытка инвайта: {username}", page)
                        await add_user_test(client, dropdown.value, username, self.page)
                        # Выполняем приглашение
                        # await log_and_display(f"✅ Участник {username} добавлен в {dropdown.value}.", page)
                        # await client(functions.channels.InviteToChannelRequest(
                        # channel=dropdown.value,
                        # users=[username]
                        # ))
                        # input_user = await client.get_input_entity(username)
                        # input_channel = await client.get_input_entity(username_group)
                        # await client(InviteToChannelRequest(
                        #     channel=input_channel,
                        #     users=[input_user]
                        # ))
                        # await client(InviteToChannelRequest(username_group, [username]))
                        # await client(AddChatUserRequest(
                        #     chat_id=dropdown.value,
                        #     user_to_add=username,
                        #     fwd_limit=10  # Allow the user to see the 10 last messages
                        # ))
                        # timeout=2  # 15 секунд — настрой по необходимости
                        # )
                        # await log_and_display(f"[DEBUG] Инвайт выполнен: {username}", page)
                        # await log_and_display(f"Удачно! Спим 5 секунд", page)
                        # await record_inviting_results(time_inviting_1, time_inviting_2, username, page=page)
                    # Ошибка инвайтинга продолжаем работу
                    # except UserNotMutualContactError:
                    #     await log_and_display(translations["ru"]["errors"]["user_not_mutual_contact"], page)
                    #     await record_inviting_results(time_inviting_1, time_inviting_2, username, page)
                    # except (UserKickedError, UserDeactivatedBanError):
                    #     await log_and_display(translations["ru"]["errors"]["user_kicked_or_banned"], page)
                    #     await record_inviting_results(time_inviting_1, time_inviting_2, username, page)
                    # except (UserIdInvalidError, UsernameNotOccupiedError, ValueError, UsernameInvalidError):
                    #     await log_and_display(translations["ru"]["errors"]["invalid_username"], page)
                    #     await record_inviting_results(time_inviting_1, time_inviting_2, username, page)
                    # except ChatAdminRequiredError:
                    #     await log_and_display(translations["ru"]["errors"]["admin_rights_required"], page)
                    #     await record_inviting_results(time_inviting_1, time_inviting_2, username, page)
                    # except UserPrivacyRestrictedError:
                    #     await log_and_display(translations["ru"]["errors"]["user_privacy_restricted"], page)
                    #     await record_inviting_results(time_inviting_1, time_inviting_2, username, page)
                    # except BotGroupsBlockedError:
                    #     await log_and_display(translations["ru"]["errors"]["bot_group_blocked"], page)
                    #     await record_inviting_results(time_inviting_1, time_inviting_2, username, page)
                    # except (TypeError, UnboundLocalError):
                    #     await log_and_display(translations["ru"]["errors"]["type_or_scope"], page)
                    # except BadRequestError:
                    #     await log_and_display(translations["ru"]["errors"]["chat_member_add_failed"], page)
                    # Ошибка инвайтинга прерываем работу
                    # except ChatWriteForbiddenError:
                    #     await log_and_display(translations["ru"]["errors"]["chat_write_forbidden"], page)
                    #     await record_inviting_results(time_inviting_1, time_inviting_2, username, page)
                    #     break  # Прерываем работу и меняем аккаунт
                    # except InviteRequestSentError:
                    #     await log_and_display(translations["ru"]["errors"]["invite_request_sent"], page)
                    #     await record_inviting_results(time_inviting_1, time_inviting_2, username, page)
                    #     break  # Прерываем работу и меняем аккаунт
                    # except FloodWaitError as e:
                    #     await log_and_display(f"{translations["ru"]["errors"]["flood_wait"]}{e}", page, level="error")
                    #     await record_and_interrupt(time_inviting_1, time_inviting_2, page)
                    #     break  # Прерываем работу и меняем аккаунт
                    # except AuthKeyUnregisteredError:
                    #     await log_and_display(translations["ru"]["errors"]["auth_key_unregistered"], page)
                    #     await record_and_interrupt(time_inviting_1, time_inviting_2, page)
                    #     break
                    # except PeerFloodError:
                    #     await log_and_display(translations["ru"]["errors"]["peer_flood"], page, level="error")
                    #     await record_and_interrupt(time_inviting_1, time_inviting_2, page)
                    #     break  # Прерываем работу и меняем аккаунт
                    except KeyboardInterrupt:  # Закрытие окна программы
                        # client.disconnect()  # Разрываем соединение telegram
                        await log_and_display(translations["ru"]["errors"]["script_stopped"], self.page, level="error")
                    # except sqlite3.DatabaseError:
                    #     await log_and_display(f"❌ Ошибка базы данных, аккаунта или аккаунт заблокирован.", page)
                    # except Exception as error:
                    #     logger.exception(error)
                # await self.sub_unsub_tg.unsubscribe_from_the_group(client, dropdown.value, page=self.page)
                await log_and_display(f"[!] Инвайтинг окончен!", page=self.page)
            # except Exception as error:
            #     logger.exception(error)
            await end_time(start, page=self.page)
            await show_notification(self.page, "🔚 Конец инвайтинга")  # Выводим уведомление пользователю
            self.page.go("/inviting")  # переходим к основному меню инвайтинга 🏠

        async def save(_):
            """Запись ссылки для инвайтинга в базу данных"""
            links = link_entry_field.value.strip().split()

            logger.info(f"Пользователь ввел ссылку(и): {links}")
            data_to_save = {
                "links_inviting": links,
            }
            save_links_inviting(data_to_save)
            logger.success(f"Сохранено в базу данных: {data_to_save}")
            await log_and_display("✅ Ссылки успешно сохранены.", self.page)

            # 🔄 Обновляем список в выпадающем списке
            updated_links = get_links_inviting()
            dropdown.options = [ft.dropdown.Option(link) for link in updated_links]
            dropdown.value = links[0] if links else None  # Автоматически выбрать первую новую ссылку (если нужно)
            self.page.update()  # Обновляем интерфейс

        async def launching_an_invite_once_an_hour(_):
            """
            🚀 Запускает процесс инвайтинга групп и отображает статус в интерфейсе.
            ⏰ Инвайтинг 1 раз в час. Запуск приглашения участников 1 раз в час.
            """
            try:
                async def general_invitation_group_scheduler():
                    await general_invitation_to_the_group(_)

                await log_and_display("Запуск программы в 00 минут каждого часа", self.page)
                self.scheduler.hourly(dt.time(minute=00, second=00),
                                      general_invitation_group_scheduler)  # Асинхронная функция для выполнения
                while True:
                    await asyncio.sleep(1)
            except Exception as error:
                logger.exception(error)

        async def schedule_invite(_):
            """
            🚀 Запускает процесс инвайтинга групп и отображает статус в интерфейсе.
            🕒 Инвайтинг в определенное время. Запуск автоматической отправки приглашений участникам каждый день в определенное время.
            """
            try:
                async def general_invitation_group_scheduler():
                    await general_invitation_to_the_group(_)

                await log_and_display(f"Скрипт будет запускаться каждый день в {self.hour}:{self.minutes}", self.page)
                self.scheduler.once(dt.time(hour=int(self.hour), minute=int(self.minutes)),
                                    general_invitation_group_scheduler)
                while True:
                    await asyncio.sleep(1)
            except Exception as error:
                logger.exception(error)

        async def launching_invite_every_day_certain_time(_):
            """
            🚀 Запускает процесс инвайтинга групп и отображает статус в интерфейсе.
            📅 Инвайтинг каждый день. Запуск приглашения участников каждый день в определенное время, выбранное пользователем.
            """

            async def general_invitation_group_scheduler():
                await general_invitation_to_the_group(_)

            await log_and_display(f"Скрипт будет запускаться каждый день в {self.hour}:{self.minutes}", self.page)
            self.scheduler.daily(dt.time(hour=int(self.hour), minute=int(self.minutes)),
                                 general_invitation_group_scheduler)
            while True:
                await asyncio.sleep(1)

        # Создаем выпадающий список с названиями групп
        dropdown = ft.Dropdown(width=WIDTH_WIDE_BUTTON,
                               options=[ft.DropdownOption(link) for link in links_inviting],
                               autofocus=True)

        # Поле ввода, для ссылок для инвайтинга
        link_entry_field = ft.TextField(label="Введите ссылку на группу для инвайтинга",
                                        label_style=ft.TextStyle(color=ft.Colors.GREY_400), width=700
                                        )
        save_button = ft.IconButton(visible=True, icon=ft.Icons.SAVE, on_click=save, icon_size=50)

        self.page.views.append(
            ft.View("/inviting",
                    [await GUIProgram().key_app_bar(),
                     ft.Text(spans=[ft.TextSpan(
                         translations["ru"]["inviting_menu"]["inviting"],
                         ft.TextStyle(size=20, weight=ft.FontWeight.BOLD,
                                      foreground=ft.Paint(
                                          gradient=ft.PaintLinearGradient((0, 20), (150, 20), [ft.Colors.PINK,
                                                                                               ft.Colors.PURPLE])), ), ), ], ),
                     list_view,  # Отображение логов 📝

                     ft.Row(
                         controls=[link_entry_field, save_button],
                         alignment=ft.MainAxisAlignment.SPACE_BETWEEN  # или .START
                     ),

                     ft.Text(value="📂 Выберите группу для инвайтинга"),  # Выбор группы для инвайтинга
                     dropdown,  # Выпадающий список с названиями групп

                     ft.Column([  # Добавляет все чекбоксы и кнопку на страницу (page) в виде колонок.
                         # 🚀 Инвайтинг
                         ft.ElevatedButton(width=WIDTH_WIDE_BUTTON, height=BUTTON_HEIGHT,
                                           text=translations["ru"]["inviting_menu"]["inviting"],
                                           on_click=general_invitation_to_the_group  # Используем синхронную обёртку
                                           ),
                         # ⏰ Инвайтинг 1 раз в час
                         ft.ElevatedButton(width=WIDTH_WIDE_BUTTON, height=BUTTON_HEIGHT,
                                           text=translations["ru"]["inviting_menu"]["invitation_1_time_per_hour"],
                                           on_click=launching_an_invite_once_an_hour),
                         # 🕒 Инвайтинг в определенное время
                         ft.ElevatedButton(width=WIDTH_WIDE_BUTTON, height=BUTTON_HEIGHT,
                                           text=translations["ru"]["inviting_menu"]["invitation_at_a_certain_time"],
                                           on_click=schedule_invite),
                         # 📅 Инвайтинг каждый день
                         ft.ElevatedButton(width=WIDTH_WIDE_BUTTON, height=BUTTON_HEIGHT,
                                           text=translations["ru"]["inviting_menu"]["inviting_every_day"],
                                           on_click=launching_invite_every_day_certain_time),
                     ])]))
        self.page.update()  # обновляем страницу после добавления элементов управления 🔄

    async def data_for_inviting(self, page: ft.Page):
        """"
        Получение данных для инвайтинга
        """
        usernames = select_records_with_limit(limit=None)
        logger.info(usernames)
        find_filesss = find_filess(directory_path=path_accounts_folder, extension='session')
        await log_and_display(f"Лимит на аккаунт: {LIMITS}\n"
                              f"Всего usernames: {len(usernames)}\n"
                              f"Подключенные аккаунты {find_filesss}\n"
                              f"Всего подключенных аккаунтов: {len(find_filesss)}\n", page)
