# -*- coding: utf-8 -*-
import asyncio
import datetime as dt

import flet as ft  # Импортируем библиотеку flet
from loguru import logger
from scheduler.asyncio import Scheduler
from telethon.errors import (AuthKeyDuplicatedError, PeerFloodError, FloodWaitError, UserPrivacyRestrictedError,
                             UserChannelsTooMuchError, BotGroupsBlockedError, ChatWriteForbiddenError,
                             UserBannedInChannelError, UserNotMutualContactError, ChatAdminRequiredError,
                             UserKickedError, ChannelPrivateError, UserIdInvalidError, UsernameNotOccupiedError,
                             UsernameInvalidError, InviteRequestSentError, TypeNotFoundError, SessionRevokedError,
                             UserDeactivatedBanError, AuthKeyUnregisteredError)
from telethon.tl.functions.channels import InviteToChannelRequest

from src.core.configs import ConfigReader, path_inviting_folder, line_width_button, BUTTON_HEIGHT
from src.core.sqlite_working_tools import DatabaseHandler
from src.core.utils import record_and_interrupt, record_inviting_results, find_filess
from src.features.account.TGConnect import TGConnect
from src.features.account.TGSubUnsub import SubscribeUnsubscribeTelegram
from src.gui.gui import start_time, end_time, list_view, log_and_display
from src.gui.menu import show_notification
from src.locales.translations_loader import translations


class InvitingToAGroup:

    def __init__(self):
        self.db_handler = DatabaseHandler()
        self.sub_unsub_tg = SubscribeUnsubscribeTelegram()
        self.tg_connect = TGConnect()
        self.config_reader = ConfigReader()
        self.time_inviting = self.config_reader.get_time_inviting()
        self.hour, self.minutes = self.config_reader.get_hour_minutes_every_day()
        self.scheduler = Scheduler()  # Создаем экземпляр планировщика

    async def getting_an_invitation_link_from_the_database(self, page: ft.Page):
        """"
        Получение ссылки для инвайтинга
        """
        try:
            return await self.db_handler.open_and_read_data(table_name="links_inviting",
                                                            page=page)  # Открываем базу данных
        except Exception as error:
            logger.exception(f"Ошибка: {error}")
            raise

    async def data_for_inviting(self, page: ft.Page):
        """"
        Получение данных для инвайтинга
        """
        number_usernames: list = await self.db_handler.select_records_with_limit(table_name="members", limit=None)
        account_limit = ConfigReader().get_limits()
        find_filesss = await find_filess(directory_path=path_inviting_folder, extension='session')
        await log_and_display(f"Лимит на аккаунт: {account_limit}\n"
                              f"Всего участников: {len(number_usernames)}\n"
                              f"Подключенные аккаунты {find_filesss}\n"
                              f"Всего подключенных аккаунтов: {len(find_filesss)}\n", page)

    async def general_invitation_to_the_group(self, page: ft.Page, dropdown):
        """
        Основной метод для инвайтинга

        :param page: Страница интерфейса Flet для отображения элементов управления.
        :param dropdown:
        :return:
        """
        start = await start_time(page)
        page.update()  # Обновите страницу, чтобы сразу показать сообщение 🔄
        try:
            for session_name in await find_filess(directory_path=path_inviting_folder, extension='session'):
                client = await self.tg_connect.get_telegram_client(page, session_name,
                                                                   account_directory=path_inviting_folder)
                await log_and_display(f"{dropdown.value}", page)
                # Подписка на группу для инвайтинга
                await self.sub_unsub_tg.subscribe_to_group_or_channel(client, dropdown.value, page)
                # Получение списка usernames
                number_usernames: list = await self.db_handler.select_records_with_limit(table_name="members",
                                                                                         limit=ConfigReader().get_limits())
                if len(number_usernames) == 0:
                    await log_and_display(f"В таблице members нет пользователей для инвайтинга", page)
                    await self.sub_unsub_tg.unsubscribe_from_the_group(client, dropdown.value, page)
                    break  # Прерываем работу и меняем аккаунт
                for username in number_usernames:
                    await log_and_display(f"Пользователь username:{username[0]}", page)
                    # Инвайтинг в группу по полученному списку

                    try:
                        await log_and_display(f"Попытка приглашения {username[0]} в группу {dropdown.value}.", page)
                        await client(InviteToChannelRequest(dropdown.value, [username[0]]))
                        await log_and_display(f"Удачно! Спим 5 секунд", page)
                        await record_inviting_results(self.time_inviting[0], self.time_inviting[1], username, page)
                    # Ошибка инвайтинга продолжаем работу
                    except UserChannelsTooMuchError:
                        await log_and_display(translations["ru"]["notifications_errors"]["user_channels_too_much"], page)
                        await record_inviting_results(self.time_inviting[0], self.time_inviting[1], username, page)
                    except UserNotMutualContactError:
                        await log_and_display(translations["ru"]["notifications_errors"]["user_not_mutual_contact"], page)
                        await record_inviting_results(self.time_inviting[0], self.time_inviting[1], username, page)
                    except (UserKickedError, UserDeactivatedBanError):
                        await log_and_display(translations["ru"]["notifications_errors"]["user_kicked_or_banned"], page)
                        await record_inviting_results(self.time_inviting[0], self.time_inviting[1], username, page)
                    except (UserIdInvalidError, UsernameNotOccupiedError, ValueError, UsernameInvalidError):
                        await log_and_display(translations["ru"]["notifications_errors"]["invalid_username"], page)
                        await record_inviting_results(self.time_inviting[0], self.time_inviting[1], username, page)
                    except ChatAdminRequiredError:
                        await log_and_display(translations["ru"]["notifications_errors"]["admin_rights_required"], page)
                        await record_inviting_results(self.time_inviting[0], self.time_inviting[1], username, page)
                    except UserPrivacyRestrictedError:
                        await log_and_display(translations["ru"]["notifications_errors"]["user_privacy_restricted"], page)
                        await record_inviting_results(self.time_inviting[0], self.time_inviting[1], username, page)
                    except BotGroupsBlockedError:
                        await log_and_display(translations["ru"]["notifications_errors"]["bot_group_blocked"], page)
                        await record_inviting_results(self.time_inviting[0], self.time_inviting[1], username, page)
                    except (TypeError, UnboundLocalError):
                        await log_and_display(translations["ru"]["notifications_errors"]["type_or_scope"], page)

                    # Ошибка инвайтинга прерываем работу
                    except ChatWriteForbiddenError:
                        await log_and_display(translations["ru"]["notifications_errors"]["chat_write_forbidden"], page)
                        await record_inviting_results(self.time_inviting[0], self.time_inviting[1], username, page)
                        break  # Прерываем работу и меняем аккаунт
                    except InviteRequestSentError:
                        await log_and_display(translations["ru"]["notifications_errors"]["invite_request_sent"], page)
                        await record_inviting_results(self.time_inviting[0], self.time_inviting[1], username, page)
                        break  # Прерываем работу и меняем аккаунт
                    except (ChannelPrivateError, TypeNotFoundError, AuthKeyDuplicatedError, UserBannedInChannelError, SessionRevokedError):
                        await log_and_display(translations["ru"]["notifications_errors"]["invalid_auth_session_terminated"], page)
                        await record_and_interrupt(self.time_inviting[0], self.time_inviting[1], page)
                        break  # Прерываем работу и меняем аккаунт
                    except FloodWaitError as e:
                        await log_and_display(f"{translations["ru"]["notifications_errors"]["flood_wait"]}{e}", page, level="error")
                        await record_and_interrupt(self.time_inviting[0], self.time_inviting[1], page)
                        break  # Прерываем работу и меняем аккаунт
                    except AuthKeyUnregisteredError:
                        await log_and_display(translations["ru"]["notifications_errors"]["auth_key_unregistered"], page)
                        await record_and_interrupt(self.time_inviting[0], self.time_inviting[1], page)
                        break
                    except PeerFloodError:
                        await log_and_display(translations["ru"]["notifications_errors"]["peer_flood"], page, level="error")
                        await record_and_interrupt(self.time_inviting[0], self.time_inviting[1], page)
                        break  # Прерываем работу и меняем аккаунт
                    except KeyboardInterrupt:  # Закрытие окна программы
                        client.disconnect()  # Разрываем соединение telegram
                        await log_and_display(translations["ru"]["notifications_errors"]["script_stopped"], page, level="error")
                    except Exception as error:
                        logger.exception(f"❌ Ошибка: {error}")
                    else:
                        await log_and_display(
                            f"[+] Участник {username} добавлен, если не состоит в чате {dropdown.value}",
                            page)
                        await record_inviting_results(self.time_inviting[0], self.time_inviting[1], username, page)
                await self.sub_unsub_tg.unsubscribe_from_the_group(client, dropdown.value, page)
            await log_and_display(f"[!] Инвайтинг окончен!", page)
        except Exception as error:
            logger.exception(f"❌ Ошибка: {error}")
        await end_time(start, page)
        await show_notification(page, "🔚 Конец инвайтинга")  # Выводим уведомление пользователю
        page.go("/inviting")  # переходим к основному меню инвайтинга 🏠

    async def inviting_without_limits(self, page: ft.Page) -> None:
        """
        🚀 Инвайтинг. Группа для инвайтинга выбирается из выпадающего списка. Информация о работе выводится
        в графический интерфейс и записывается в лог файл.

        :param page: Страница интерфейса Flet для отображения элементов управления.
        """

        page.controls.append(list_view)  # добавляем ListView на страницу для отображения логов 📝
        page.update()  # обновляем страницу, чтобы сразу показать ListView 🔄

        links_inviting = await self.getting_an_invitation_link_from_the_database(
            page)  # Получение ссылки для инвайтинга

        await self.data_for_inviting(page)  # Отображение информации о настройках инвайтинга

        async def add_items(_):
            """
            🚀 Запускает процесс инвайтинга групп и отображает статус в интерфейсе.
            """
            await self.general_invitation_to_the_group(page, dropdown)

        # Создаем выпадающий список с названиями групп
        dropdown = ft.Dropdown(width=line_width_button,
                               options=[ft.DropdownOption(link[0]) for link in links_inviting],
                               autofocus=True)

        await self.create_invite_page(page, dropdown, add_items)

    async def launching_invite_every_day_certain_time(self, page: ft.Page) -> None:
        """
        📅 Инвайтинг каждый день. Запуск приглашения участников каждый день в определенное время, выбранное пользователем.
        """

        page.controls.append(list_view)  # добавляем ListView на страницу для отображения логов 📝
        page.update()  # обновляем страницу, чтобы сразу показать ListView 🔄

        links_inviting = await self.getting_an_invitation_link_from_the_database(
            page)  # Получение ссылки для инвайтинга

        await self.data_for_inviting(page)  # Отображение информации о настройках инвайтинга

        async def add_items(_):
            """
            🚀 Запускает процесс инвайтинга групп и отображает статус в интерфейсе.
            """

            async def general_invitation_to_the_group_scheduler():
                await self.general_invitation_to_the_group(page, dropdown)

            await log_and_display(f"Скрипт будет запускаться каждый день в {self.hour}:{self.minutes}", page)
            self.scheduler.daily(dt.time(hour=int(self.hour), minute=int(self.minutes)),
                                 general_invitation_to_the_group_scheduler)
            while True:
                await asyncio.sleep(1)

        # Создаем выпадающий список с названиями групп
        dropdown = ft.Dropdown(width=line_width_button,
                               options=[ft.DropdownOption(link[0]) for link in links_inviting],
                               autofocus=True)

        await self.create_invite_page(page, dropdown, add_items)

    async def launching_an_invite_once_an_hour(self, page: ft.Page) -> None:
        """
        ⏰ Инвайтинг 1 раз в час. Запуск приглашения участников 1 раз в час.

        :param page: Страница интерфейса Flet для отображения элементов управления.
        """

        page.controls.append(list_view)  # добавляем ListView на страницу для отображения логов 📝
        page.update()  # обновляем страницу, чтобы сразу показать ListView 🔄

        links_inviting = await self.getting_an_invitation_link_from_the_database(
            page)  # Получение ссылки для инвайтинга

        await self.data_for_inviting(page)  # Отображение информации о настройках инвайтинга

        async def add_items(_):
            """
            🚀 Запускает процесс инвайтинга групп и отображает статус в интерфейсе.
            """
            try:

                async def general_invitation_to_the_group_scheduler():
                    await self.general_invitation_to_the_group(page, dropdown)

                await log_and_display("Запуск программы в 00 минут каждого часа", page)

                self.scheduler.hourly(dt.time(minute=00, second=00),
                                      general_invitation_to_the_group_scheduler)  # Асинхронная функция для выполнения

                while True:
                    await asyncio.sleep(1)
            except Exception as error:
                logger.exception(f"❌ Ошибка: {error}")

        # Создаем выпадающий список с названиями групп
        dropdown = ft.Dropdown(width=line_width_button,
                               options=[ft.DropdownOption(link[0]) for link in links_inviting],
                               autofocus=True)

        await self.create_invite_page(page, dropdown, add_items)

    @staticmethod
    async def create_invite_page(page: ft.Page, dropdown, add_items) -> None:

        async def back_button_clicked(_):
            """
            ⬅️ Обрабатывает нажатие кнопки "Назад", возвращая в меню инвайтинга.
            """
            page.go("/inviting")  # переходим к основному меню инвайтинга 🏠

        # Добавляем кнопки и другие элементы управления на страницу
        page.views.append(
            ft.View(
                "/inviting",
                [
                    list_view,  # Отображение логов 📝
                    ft.Text(value="📂 Выберите группу для инвайтинга"),  # Выбор группы для инвайтинга
                    dropdown,  # Выпадающий список с названиями групп
                    ft.Column(),  # Резерв для приветствия или других элементов интерфейса
                    ft.ElevatedButton(width=line_width_button, height=BUTTON_HEIGHT,
                                      text=translations["ru"]["buttons"]["start"],
                                      on_click=add_items),  # Кнопка "🚀 Начать инвайтинг"
                    ft.ElevatedButton(width=line_width_button, height=BUTTON_HEIGHT,
                                      text=translations["ru"]["buttons"]["back"],
                                      on_click=back_button_clicked)  # Кнопка "⬅️ Назад"
                ],
            )
        )

        page.update()  # обновляем страницу после добавления элементов управления 🔄

    async def schedule_invite(self, page: ft.Page) -> None:
        """
        🕒 Инвайтинг в определенное время. Запуск автоматической отправки приглашений участникам каждый день в определенное время.

        :param page: Страница интерфейса Flet для отображения элементов управления.
        """

        page.controls.append(list_view)  # добавляем ListView на страницу для отображения логов 📝
        page.update()  # обновляем страницу, чтобы сразу показать ListView 🔄

        links_inviting = await self.getting_an_invitation_link_from_the_database(
            page)  # Получение ссылки для инвайтинга

        await self.data_for_inviting(page)  # Отображение информации о настройках инвайтинга

        async def add_items(_):
            """
            🚀 Запускает процесс инвайтинга групп и отображает статус в интерфейсе.
            """
            try:
                async def general_invitation_to_the_group_scheduler():
                    await self.general_invitation_to_the_group(page, dropdown)

                await log_and_display(f"Скрипт будет запускаться каждый день в {self.hour}:{self.minutes}", page)

                self.scheduler.once(dt.time(hour=int(self.hour), minute=int(self.minutes)),
                                    general_invitation_to_the_group_scheduler)
                while True:
                    await asyncio.sleep(1)

            except Exception as error:
                logger.exception(f"❌ Ошибка: {error}")

        # Создаем выпадающий список с названиями групп
        dropdown = ft.Dropdown(width=line_width_button,
                               options=[ft.DropdownOption(link[0]) for link in links_inviting],
                               autofocus=True)

        await self.create_invite_page(page, dropdown, add_items)
