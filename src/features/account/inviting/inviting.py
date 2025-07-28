# -*- coding: utf-8 -*-
import asyncio
import datetime as dt

import flet as ft  # Импортируем библиотеку flet
from loguru import logger
from scheduler.asyncio import Scheduler
from telethon.errors import (AuthKeyDuplicatedError, AuthKeyUnregisteredError, BadRequestError, BotGroupsBlockedError,
                             ChannelPrivateError, ChatAdminRequiredError, ChatWriteForbiddenError, FloodWaitError,
                             InviteRequestSentError, PeerFloodError, SessionRevokedError, TypeNotFoundError,
                             UserBannedInChannelError, UserChannelsTooMuchError, UserDeactivatedBanError,
                             UserIdInvalidError, UserKickedError, UsernameInvalidError, UsernameNotOccupiedError,
                             UserNotMutualContactError, UserPrivacyRestrictedError)
from telethon.tl.functions.channels import InviteToChannelRequest

from src.core.configs import (BUTTON_HEIGHT, ConfigReader, LIMITS, WIDTH_WIDE_BUTTON, path_accounts_folder,
                              time_inviting_1, time_inviting_2)
from src.core.sqlite_working_tools import select_records_with_limit, get_links_inviting, save_links_inviting
from src.core.utils import find_filess, record_and_interrupt, record_inviting_results
from src.features.account.TGConnect import TGConnect
from src.features.account.TGSubUnsub import SubscribeUnsubscribeTelegram
from src.features.account.parsing.gui_elements import GUIProgram
from src.gui.gui import end_time, list_view, log_and_display, start_time
from src.gui.notification import show_notification
from src.locales.translations_loader import translations


class InvitingToAGroup:

    def __init__(self):
        self.sub_unsub_tg = SubscribeUnsubscribeTelegram()
        self.tg_connect = TGConnect()
        self.config_reader = ConfigReader()
        self.hour, self.minutes = self.config_reader.get_hour_minutes_every_day()
        self.scheduler = Scheduler()  # Создаем экземпляр планировщика

    async def inviting_menu(self, page: ft.Page):
        """
        Меню инвайтинг

        :param page: Страница интерфейса Flet для отображения элементов управления.
        """
        list_view.controls.clear()  # ✅ Очистка логов перед новым запуском
        page.controls.append(list_view)  # Добавляем ListView на страницу для отображения логов 📝
        page.update()  # обновляем страницу, чтобы сразу показать ListView 🔄
        links_inviting = get_links_inviting()  # Получаем список ссылок на группы для инвайтинга из базы данных
        await self.data_for_inviting(page)  # Отображение информации о настройках инвайтинга

        # Создаем выпадающий список с названиями групп
        dropdown = ft.Dropdown(width=WIDTH_WIDE_BUTTON, options=[ft.DropdownOption(link) for link in links_inviting],
                               autofocus=True)

        async def save(_):
            """Запись ссылки для инвайтинга в базу данных"""
            links = link_entry_field.value.strip().split()
            logger.info(f"Пользователь ввел ссылку(и): {links}")
            data_to_save = {
                "links_inviting": links,
            }
            save_links_inviting(data_to_save)
            logger.success(f"Сохранено в базу данных: {data_to_save}")
            await log_and_display("✅ Ссылки успешно сохранены.", page)

            # 🔄 Обновляем список в выпадающем списке
            updated_links = get_links_inviting()
            dropdown.options = [ft.dropdown.Option(link) for link in updated_links]
            dropdown.value = links[0] if links else None  # Автоматически выбрать первую новую ссылку (если нужно)
            page.update()  # Обновляем интерфейс

        async def inviting_without_limits(_):
            """
            🚀 Запускает процесс инвайтинга групп и отображает статус в интерфейсе.
            🚀 Инвайтинг. Группа для инвайтинга выбирается из выпадающего списка. Информация о работе выводится
            в графический интерфейс и записывается в лог файл.
            """
            await self.general_invitation_to_the_group(page, dropdown)

        async def launching_an_invite_once_an_hour(_):
            """
            🚀 Запускает процесс инвайтинга групп и отображает статус в интерфейсе.
            ⏰ Инвайтинг 1 раз в час. Запуск приглашения участников 1 раз в час.
            """
            try:
                async def general_invitation_group_scheduler():
                    await self.general_invitation_to_the_group(page, dropdown)

                await log_and_display("Запуск программы в 00 минут каждого часа", page)
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
                    await self.general_invitation_to_the_group(page, dropdown)

                await log_and_display(f"Скрипт будет запускаться каждый день в {self.hour}:{self.minutes}", page)
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
                await self.general_invitation_to_the_group(page, dropdown)

            await log_and_display(f"Скрипт будет запускаться каждый день в {self.hour}:{self.minutes}", page)
            self.scheduler.daily(dt.time(hour=int(self.hour), minute=int(self.minutes)),
                                 general_invitation_group_scheduler)
            while True:
                await asyncio.sleep(1)

        # Поле ввода, для ссылок для инвайтинга
        link_entry_field = ft.TextField(label="Введите ссылку на группу для инвайтинга",
                                        label_style=ft.TextStyle(color=ft.Colors.GREY_400), width=700
                                        )
        save_button = ft.IconButton(visible=True, icon=ft.Icons.SAVE, on_click=save, icon_size=50)

        page.views.append(
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
                                           on_click=inviting_without_limits),
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
        page.update()  # обновляем страницу после добавления элементов управления 🔄

    async def data_for_inviting(self, page: ft.Page):
        """"
        Получение данных для инвайтинга
        """
        usernames = select_records_with_limit(limit=None)
        logger.info(usernames)
        find_filesss = await find_filess(directory_path=path_accounts_folder, extension='session')
        await log_and_display(f"Лимит на аккаунт: {LIMITS}\n"
                              f"Всего usernames: {len(usernames)}\n"
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
            for session_name in await find_filess(directory_path=path_accounts_folder, extension='session'):
                client = await self.tg_connect.get_telegram_client(page, session_name,
                                                                   account_directory=path_accounts_folder)
                await log_and_display(f"{dropdown.value}", page)
                # Подписка на группу для инвайтинга
                await self.sub_unsub_tg.subscribe_to_group_or_channel(client, dropdown.value, page)
                # Получение списка usernames
                usernames = select_records_with_limit(limit=LIMITS)
                if len(usernames) == 0:
                    await log_and_display(f"В таблице members нет пользователей для инвайтинга", page)
                    await self.sub_unsub_tg.unsubscribe_from_the_group(client, dropdown.value, page)
                    break  # Прерываем работу и меняем аккаунт
                for username in usernames:
                    await log_and_display(f"Пользователь username:{username[0]}", page)
                    # Инвайтинг в группу по полученному списку

                    try:
                        await log_and_display(f"Попытка приглашения {username[0]} в группу {dropdown.value}.", page)
                        await client(InviteToChannelRequest(dropdown.value, [username[0]]))
                        await log_and_display(f"Удачно! Спим 5 секунд", page)
                        await record_inviting_results(time_inviting_1, time_inviting_2, username, page)
                    # Ошибка инвайтинга продолжаем работу
                    except UserChannelsTooMuchError:
                        await log_and_display(translations["ru"]["errors"]["user_channels_too_much"], page)
                        await record_inviting_results(time_inviting_1, time_inviting_2, username, page)
                    except UserNotMutualContactError:
                        await log_and_display(translations["ru"]["errors"]["user_not_mutual_contact"], page)
                        await record_inviting_results(time_inviting_1, time_inviting_2, username, page)
                    except (UserKickedError, UserDeactivatedBanError):
                        await log_and_display(translations["ru"]["errors"]["user_kicked_or_banned"], page)
                        await record_inviting_results(time_inviting_1, time_inviting_2, username, page)
                    except (UserIdInvalidError, UsernameNotOccupiedError, ValueError, UsernameInvalidError):
                        await log_and_display(translations["ru"]["errors"]["invalid_username"], page)
                        await record_inviting_results(time_inviting_1, time_inviting_2, username, page)
                    except ChatAdminRequiredError:
                        await log_and_display(translations["ru"]["errors"]["admin_rights_required"], page)
                        await record_inviting_results(time_inviting_1, time_inviting_2, username, page)
                    except UserPrivacyRestrictedError:
                        await log_and_display(translations["ru"]["errors"]["user_privacy_restricted"], page)
                        await record_inviting_results(time_inviting_1, time_inviting_2, username, page)
                    except BotGroupsBlockedError:
                        await log_and_display(translations["ru"]["errors"]["bot_group_blocked"], page)
                        await record_inviting_results(time_inviting_1, time_inviting_2, username, page)
                    except (TypeError, UnboundLocalError):
                        await log_and_display(translations["ru"]["errors"]["type_or_scope"], page)
                    except BadRequestError:
                        await log_and_display(translations["ru"]["errors"]["chat_member_add_failed"], page)
                    # Ошибка инвайтинга прерываем работу
                    except ChatWriteForbiddenError:
                        await log_and_display(translations["ru"]["errors"]["chat_write_forbidden"], page)
                        await record_inviting_results(time_inviting_1, time_inviting_2, username, page)
                        break  # Прерываем работу и меняем аккаунт
                    except InviteRequestSentError:
                        await log_and_display(translations["ru"]["errors"]["invite_request_sent"], page)
                        await record_inviting_results(time_inviting_1, time_inviting_2, username, page)
                        break  # Прерываем работу и меняем аккаунт
                    except (ChannelPrivateError, TypeNotFoundError, AuthKeyDuplicatedError, UserBannedInChannelError,
                            SessionRevokedError):
                        await log_and_display(translations["ru"]["errors"]["invalid_auth_session_terminated"], page)
                        await record_and_interrupt(time_inviting_1, time_inviting_2, page)
                        break  # Прерываем работу и меняем аккаунт
                    except FloodWaitError as e:
                        await log_and_display(f"{translations["ru"]["errors"]["flood_wait"]}{e}", page, level="error")
                        await record_and_interrupt(time_inviting_1, time_inviting_2, page)
                        break  # Прерываем работу и меняем аккаунт
                    except AuthKeyUnregisteredError:
                        await log_and_display(translations["ru"]["errors"]["auth_key_unregistered"], page)
                        await record_and_interrupt(time_inviting_1, time_inviting_2, page)
                        break
                    except PeerFloodError:
                        await log_and_display(translations["ru"]["errors"]["peer_flood"], page, level="error")
                        await record_and_interrupt(time_inviting_1, time_inviting_2, page)
                        break  # Прерываем работу и меняем аккаунт
                    except KeyboardInterrupt:  # Закрытие окна программы
                        client.disconnect()  # Разрываем соединение telegram
                        await log_and_display(translations["ru"]["errors"]["script_stopped"], page, level="error")
                    except Exception as error:
                        logger.exception(error)
                    else:
                        await log_and_display(
                            f"[+] Участник {username} добавлен, если не состоит в чате {dropdown.value}",
                            page=page)
                        await record_inviting_results(time_inviting_1, time_inviting_2, username, page=page)
                await self.sub_unsub_tg.unsubscribe_from_the_group(client, dropdown.value, page=page)
            await log_and_display(f"[!] Инвайтинг окончен!", page=page)
        except Exception as error:
            logger.exception(error)
        await end_time(start, page=page)
        await show_notification(page, "🔚 Конец инвайтинга")  # Выводим уведомление пользователю
        page.go("/inviting")  # переходим к основному меню инвайтинга 🏠
