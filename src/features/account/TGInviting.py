# -*- coding: utf-8 -*-
import asyncio
import datetime
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
from src.gui.gui import start_time
from src.gui.menu import show_notification, log_and_display
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

    async def getting_an_invitation_link_from_the_database(self, list_view: ft.ListView, page: ft.Page):
        """"
        Получение ссылки для инвайтинга
        """
        try:
            return await self.db_handler.open_and_read_data(table_name="links_inviting", list_view=list_view,
                                                            page=page)  # Открываем базу данных
        except Exception as error:
            logger.exception(f"Ошибка: {error}")
            raise

    async def data_for_inviting(self, page: ft.Page, list_view: ft.ListView):
        """"
        Получение данных для инвайтинга
        """
        number_usernames: list = await self.db_handler.select_records_with_limit(table_name="members", limit=None)
        account_limit = ConfigReader().get_limits()
        find_filesss = await find_filess(directory_path=path_inviting_folder, extension='session')
        await log_and_display(f"Лимит на аккаунт: {account_limit}\n"
                              f"Всего участников: {len(number_usernames)}\n"
                              f"Подключенные аккаунты {find_filesss}\n"
                              f"Всего подключенных аккаунтов: {len(find_filesss)}\n", list_view, page)

    async def general_invitation_to_the_group(self, page: ft.Page, list_view, dropdown):
        """
        Основной метод для инвайтинга

        :param page: Страница интерфейса Flet для отображения элементов управления.
        :param list_view:
        :param dropdown:
        :return:
        """
        start = await start_time(list_view, page)
        page.update()  # Обновите страницу, чтобы сразу показать сообщение 🔄
        try:
            for session_name in await find_filess(directory_path=path_inviting_folder, extension='session'):
                client = await self.tg_connect.get_telegram_client(page, session_name,
                                                                   account_directory=path_inviting_folder,
                                                                   list_view=list_view)
                await log_and_display(f"{dropdown.value}", list_view, page)
                # Подписка на группу для инвайтинга
                await self.sub_unsub_tg.subscribe_to_group_or_channel(client, dropdown.value, list_view, page)
                # Получение списка usernames
                number_usernames: list = await self.db_handler.select_records_with_limit(table_name="members",
                                                                                         limit=ConfigReader().get_limits())
                if len(number_usernames) == 0:
                    await log_and_display(f"В таблице members нет пользователей для инвайтинга", list_view, page)
                    await self.sub_unsub_tg.unsubscribe_from_the_group(client, dropdown.value, list_view, page)
                    break  # Прерываем работу и меняем аккаунт
                for username in number_usernames:
                    await log_and_display(f"Пользователь username:{username[0]}", list_view, page)
                    # Инвайтинг в группу по полученному списку

                    try:
                        await log_and_display(f"Попытка приглашения {username[0]} в группу {dropdown.value}.",
                                              list_view, page)
                        await client(InviteToChannelRequest(dropdown.value, [username[0]]))
                        await log_and_display(f"Удачно! Спим 5 секунд", list_view, page)
                        await record_inviting_results(self.time_inviting[0], self.time_inviting[1], username, list_view,
                                                      page)

                    # Ошибка инвайтинга продолжаем работу
                    except UserChannelsTooMuchError:
                        await log_and_display(
                            f"❌ Попытка приглашения {username} в группу {dropdown.value}. Превышен лимит у user каналов / супергрупп.",
                            list_view, page, level="error")
                        await record_inviting_results(self.time_inviting[0], self.time_inviting[1], username, list_view,
                                                      page)
                    except UserNotMutualContactError:
                        await log_and_display(
                            f"❌ Попытка приглашения {username} в группу {dropdown.value}. User не является взаимным контактом.",
                            list_view, page, level="error")
                        await record_inviting_results(self.time_inviting[0], self.time_inviting[1], username, list_view,
                                                      page)
                    except (UserKickedError, UserDeactivatedBanError):
                        await log_and_display(
                            f"❌ Попытка приглашения {username} в группу {dropdown.value}. Пользователь был удален ранее из супергруппы или забанен.",
                            list_view, page, level="error")
                        await record_inviting_results(self.time_inviting[0], self.time_inviting[1], username, list_view,
                                                      page)
                    except (UserIdInvalidError, UsernameNotOccupiedError, ValueError, UsernameInvalidError):
                        await log_and_display(
                            f"❌ Попытка приглашения {username} в группу {dropdown.value}. Не корректное имя {username}",
                            list_view, page)
                        await record_inviting_results(self.time_inviting[0], self.time_inviting[1], username, list_view,
                                                      page)
                    except ChatAdminRequiredError:
                        await log_and_display(
                            f"❌ Попытка приглашения {username} в группу {dropdown.value}. Требуются права администратора.",
                            list_view, page)
                        await record_inviting_results(self.time_inviting[0], self.time_inviting[1], username, list_view,
                                                      page)
                    except UserPrivacyRestrictedError:
                        await log_and_display(
                            f"❌ Попытка приглашения {username} в группу {dropdown.value}. Настройки конфиденциальности {username} не позволяют вам inviting",
                            list_view, page)
                        await record_inviting_results(self.time_inviting[0], self.time_inviting[1], username, list_view,
                                                      page)
                    except BotGroupsBlockedError:
                        await log_and_display(
                            f"❌ Попытка приглашения {username} в группу {dropdown.value}. Вы не можете добавить бота в группу.",
                            list_view, page)
                        await record_inviting_results(self.time_inviting[0], self.time_inviting[1], username, list_view,
                                                      page)
                    except (TypeError, UnboundLocalError):
                        await log_and_display(f"❌ Попытка приглашения {username} в группу {dropdown.value}", list_view,
                                              page)
                    # Ошибка инвайтинга прерываем работу
                    except ChatWriteForbiddenError:
                        await log_and_display(
                            f"❌ Попытка приглашения {username} в группу {dropdown.value}. Настройки в чате не дают добавлять людей в чат, возможно стоит бот админ и нужно подписаться на другие проекты",
                            list_view, page)
                        await record_inviting_results(self.time_inviting[0], self.time_inviting[1], username, list_view,
                                                      page)
                        break  # Прерываем работу и меняем аккаунт
                    except InviteRequestSentError:
                        await log_and_display(
                            f"❌ Попытка приглашения {username} в группу {dropdown.value}. Доступ к функциям группы станет возможен после утверждения заявки администратором на {dropdown.value}",
                            list_view, page)
                        await record_inviting_results(self.time_inviting[0], self.time_inviting[1], username, list_view,
                                                      page)
                        break  # Прерываем работу и меняем аккаунт
                    except (ChannelPrivateError, TypeNotFoundError, AuthKeyDuplicatedError,
                            UserBannedInChannelError, SessionRevokedError):
                        await record_and_interrupt(self.time_inviting[0], self.time_inviting[1], list_view, page)
                        break  # Прерываем работу и меняем аккаунт
                    except FloodWaitError as error:
                        await log_and_display(f"{error}", list_view, page)
                        await record_and_interrupt(self.time_inviting[0], self.time_inviting[1], list_view, page)
                        break  # Прерываем работу и меняем аккаунт
                    except AuthKeyUnregisteredError:
                        await log_and_display(
                            f"❌ Попытка приглашения {username} в группу {dropdown.value}. Ошибка авторизации аккаунта",
                            list_view, page)
                        await record_and_interrupt(self.time_inviting[0], self.time_inviting[1], list_view, page)
                        break
                    except PeerFloodError:
                        await log_and_display(
                            f"❌ Попытка приглашения {username} в группу {dropdown.value}. Настройки конфиденциальности {username} не позволяют вам inviting",
                            list_view, page)
                        await record_and_interrupt(self.time_inviting[0], self.time_inviting[1], list_view, page)
                        break  # Прерываем работу и меняем аккаунт
                    except KeyboardInterrupt:  # Закрытие окна программы
                        client.disconnect()  # Разрываем соединение telegram
                        await log_and_display(f"[!] Скрипт остановлен!", list_view, page, level="error")
                    except Exception as error:
                        logger.exception(f"❌ Ошибка: {error}")
                    else:
                        await log_and_display(
                            f"[+] Участник {username} добавлен, если не состоит в чате {dropdown.value}", list_view,
                            page)
                        await record_inviting_results(self.time_inviting[0], self.time_inviting[1], username, list_view,
                                                      page)
                await self.sub_unsub_tg.unsubscribe_from_the_group(client, dropdown.value, list_view, page)
            await log_and_display(f"[!] Инвайтинг окончен!", list_view, page)
        except Exception as error:
            logger.exception(f"❌ Ошибка: {error}")
        finish = datetime.datetime.now()  # фиксируем время окончания парсинга ⏰
        await log_and_display(
            f"🔚 Конец инвайтинга.\n🕒 Время окончания: {finish}.\n⏳ Время работы: {finish - start}", list_view, page)
        await show_notification(page, "🔚 Конец инвайтинга")  # Выводим уведомление пользователю
        page.go("/inviting")  # переходим к основному меню инвайтинга 🏠

    async def inviting_without_limits(self, page: ft.Page) -> None:
        """
        🚀 Инвайтинг. Группа для инвайтинга выбирается из выпадающего списка. Информация о работе выводится
        в графический интерфейс и записывается в лог файл.

        :param page: Страница интерфейса Flet для отображения элементов управления.
        """

        list_view = ft.ListView(expand=10, spacing=1, padding=2, auto_scroll=True)
        page.controls.append(list_view)  # добавляем ListView на страницу для отображения логов 📝
        page.update()  # обновляем страницу, чтобы сразу показать ListView 🔄

        links_inviting = await self.getting_an_invitation_link_from_the_database(list_view,
                                                                                 page)  # Получение ссылки для инвайтинга

        await self.data_for_inviting(page, list_view)  # Отображение информации о настройках инвайтинга

        async def add_items(_):
            """
            🚀 Запускает процесс инвайтинга групп и отображает статус в интерфейсе.
            """
            await self.general_invitation_to_the_group(page, list_view, dropdown)

        # Создаем выпадающий список с названиями групп
        dropdown = ft.Dropdown(width=line_width_button,
                               options=[ft.DropdownOption(link[0]) for link in links_inviting],
                               autofocus=True)

        await self.create_invite_page(page, list_view, dropdown, add_items)

    async def launching_invite_every_day_certain_time(self, page: ft.Page) -> None:
        """
        📅 Инвайтинг каждый день. Запуск приглашения участников каждый день в определенное время, выбранное пользователем.
        """

        list_view = ft.ListView(expand=10, spacing=1, padding=2, auto_scroll=True)
        page.controls.append(list_view)  # добавляем ListView на страницу для отображения логов 📝
        page.update()  # обновляем страницу, чтобы сразу показать ListView 🔄

        links_inviting = await self.getting_an_invitation_link_from_the_database(list_view,
                                                                                 page)  # Получение ссылки для инвайтинга

        await self.data_for_inviting(page, list_view)  # Отображение информации о настройках инвайтинга

        async def add_items(_):
            """
            🚀 Запускает процесс инвайтинга групп и отображает статус в интерфейсе.
            """

            async def general_invitation_to_the_group_scheduler():
                await self.general_invitation_to_the_group(page, list_view, dropdown)

            await log_and_display(f"Скрипт будет запускаться каждый день в {self.hour}:{self.minutes}", list_view, page)
            self.scheduler.daily(dt.time(hour=int(self.hour), minute=int(self.minutes)),
                                 general_invitation_to_the_group_scheduler)
            while True:
                await asyncio.sleep(1)

        # Создаем выпадающий список с названиями групп
        dropdown = ft.Dropdown(width=line_width_button,
                               options=[ft.DropdownOption(link[0]) for link in links_inviting],
                               autofocus=True)

        await self.create_invite_page(page, list_view, dropdown, add_items)

    async def launching_an_invite_once_an_hour(self, page: ft.Page) -> None:
        """
        ⏰ Инвайтинг 1 раз в час. Запуск приглашения участников 1 раз в час.

        :param page: Страница интерфейса Flet для отображения элементов управления.
        """

        list_view = ft.ListView(expand=10, spacing=1, padding=2, auto_scroll=True)
        page.controls.append(list_view)  # добавляем ListView на страницу для отображения логов 📝
        page.update()  # обновляем страницу, чтобы сразу показать ListView 🔄

        links_inviting = await self.getting_an_invitation_link_from_the_database(list_view,
                                                                                 page)  # Получение ссылки для инвайтинга

        await self.data_for_inviting(page, list_view)  # Отображение информации о настройках инвайтинга

        async def add_items(_):
            """
            🚀 Запускает процесс инвайтинга групп и отображает статус в интерфейсе.
            """
            try:

                async def general_invitation_to_the_group_scheduler():
                    await self.general_invitation_to_the_group(page, list_view, dropdown)

                await log_and_display("Запуск программы в 00 минут каждого часа", list_view, page)

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

        await self.create_invite_page(page, list_view, dropdown, add_items)

    @staticmethod
    async def create_invite_page(page: ft.Page, list_view: ft.ListView, dropdown, add_items) -> None:

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

        list_view = ft.ListView(expand=10, spacing=1, padding=2, auto_scroll=True)
        page.controls.append(list_view)  # добавляем ListView на страницу для отображения логов 📝
        page.update()  # обновляем страницу, чтобы сразу показать ListView 🔄

        links_inviting = await self.getting_an_invitation_link_from_the_database(list_view,
                                                                                 page)  # Получение ссылки для инвайтинга

        await self.data_for_inviting(page, list_view)  # Отображение информации о настройках инвайтинга

        async def add_items(_):
            """
            🚀 Запускает процесс инвайтинга групп и отображает статус в интерфейсе.
            """
            try:
                async def general_invitation_to_the_group_scheduler():
                    await self.general_invitation_to_the_group(page, list_view, dropdown)

                await log_and_display(f"Скрипт будет запускаться каждый день в {self.hour}:{self.minutes}", list_view,
                                      page)

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

        await self.create_invite_page(page, list_view, dropdown, add_items)
