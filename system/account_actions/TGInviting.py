# -*- coding: utf-8 -*-
import asyncio
import flet as ft  # Импортируем библиотеку flet
from loguru import logger
from telethon.errors import (AuthKeyDuplicatedError, PeerFloodError, FloodWaitError, UserPrivacyRestrictedError,
                             UserChannelsTooMuchError, BotGroupsBlockedError, ChatWriteForbiddenError,
                             UserBannedInChannelError, UserNotMutualContactError, ChatAdminRequiredError,
                             UserKickedError, ChannelPrivateError, UserIdInvalidError, UsernameNotOccupiedError,
                             UsernameInvalidError, InviteRequestSentError, TypeNotFoundError)
from telethon.tl.functions.channels import InviteToChannelRequest
import datetime
from system.account_actions.TGConnect import TGConnect
from system.account_actions.TGLimits import SettingLimits
from system.account_actions.TGSubUnsub import SubscribeUnsubscribeTelegram
from system.auxiliary_functions.auxiliary_functions import record_and_interrupt, record_inviting_results, find_filess
from system.auxiliary_functions.config import ConfigReader, path_inviting_folder, line_width_button, height_button
from system.localization.localization import back_button, start_inviting_button
from system.sqlite_working_tools.sqlite_working_tools import DatabaseHandler


class InvitingToAGroup:

    def __init__(self):
        self.db_handler = DatabaseHandler()
        self.sub_unsub_tg = SubscribeUnsubscribeTelegram()
        self.limits_class = SettingLimits()
        self.tg_connect = TGConnect()
        self.config_reader = ConfigReader()

    async def getting_an_invitation_link_from_the_database(self):
        """"
        Получение ссылки для инвайтинга
        """
        try:
            links_inviting: list = await self.db_handler.open_and_read_data("links_inviting")  # Открываем базу данных
            logger.info(f"Ссылка для инвайтинга:  {links_inviting}")
            return links_inviting
        except Exception as error:
            logger.exception(f"Ошибка: {error}")

    @staticmethod
    async def log_and_display(message: str, lv, page):
        """
        Выводит сообщение в GUI и записывает лог.

        Аргументы:
        :param message: Текст сообщения для отображения и записи в лог.
        :param lv: ListView для отображения сообщений.
        :param page: Страница интерфейса Flet для отображения элементов управления.
        """
        logger.info(message)  # записываем сообщение в лог
        lv.controls.append(ft.Text(message))  # отображаем сообщение в ListView
        page.update()  # обновляем страницу для отображения нового сообщения

    async def inviting_without_limits(self, page: ft.Page, account_limits) -> None:
        """
        Инвайтинг без лимитов

        Аргументы:
        :param account_limits: Таблица с лимитами
        :param page: Страница интерфейса Flet для отображения элементов управления.
        """
        start = datetime.datetime.now()  # фиксируем время начала выполнения кода ⏱️
        lv = ft.ListView(expand=10, spacing=1, padding=2, auto_scroll=True)
        page.controls.append(lv)  # добавляем ListView на страницу для отображения логов 📝
        page.update()  # обновляем страницу, чтобы сразу показать ListView 🔄

        async def add_items(_):
            """
            🚀 Запускает процесс инвайтинга групп и отображает статус в интерфейсе.
            """

            # Индикация начала инвайтинга
            await self.log_and_display(f"▶️ Начало инвайтинга.\n🕒 Время старта: {str(start)}", lv, page)
            page.update()  # Обновите страницу, чтобы сразу показать сообщение 🔄

            try:
                # logger.info(f"Запуск инвайтинга без лимитов")
                for session_name in find_filess(directory_path=path_inviting_folder, extension='session'):
                    client = await self.tg_connect.get_telegram_client(session_name,
                                                                       account_directory=path_inviting_folder)
                    # Получение ссылки для инвайтинга
                    for link in await self.getting_an_invitation_link_from_the_database():
                        logger.info(f"{link[0]}")
                        # Подписка на группу для инвайтинга
                        await self.sub_unsub_tg.subscribe_to_group_or_channel(client, link[0])
                        # Получение списка usernames
                        number_usernames = await self.limits_class.get_usernames_with_limits(table_name="members",
                                                                                             account_limits=account_limits)

                        if len(number_usernames) == 0:
                            await self.log_and_display(f"В таблице members нет пользователей для инвайтинга", lv, page)
                            await self.sub_unsub_tg.unsubscribe_from_the_group(client, link[0])
                            break  # Прерываем работу и меняем аккаунт

                        for username in number_usernames:
                            await self.log_and_display(f"Пользователь username:{username[0]}", lv, page)
                            # Инвайтинг в группу по полученному списку
                            time_inviting = self.config_reader.get_time_inviting()
                            try:
                                await self.log_and_display(f"Попытка приглашения {username[0]} в группу {link[0]}.", lv,
                                                           page)
                                await client(InviteToChannelRequest(link[0], [username[0]]))
                                await self.log_and_display(f"Удачно! Спим 5 секунд", lv, page)
                                await asyncio.sleep(5)
                            # Ошибка инвайтинга продолжаем работу
                            except UserChannelsTooMuchError:
                                await self.log_and_display(
                                    f"Попытка приглашения {username} в группу {link[0]}. Превышен лимит у user каналов / супергрупп.",
                                    lv, page)
                                await record_inviting_results(time_inviting[0], time_inviting[1], username)
                            except UserNotMutualContactError:
                                await self.log_and_display(
                                    f"Попытка приглашения {username} в группу {link[0]}. User не является взаимным контактом.",
                                    lv, page)
                                await record_inviting_results(time_inviting[0], time_inviting[1], username)
                            except UserKickedError:
                                await self.log_and_display(
                                    f"Попытка приглашения {username} в группу {link[0]}. Пользователь был удален ранее из супергруппы.",
                                    lv, page)
                                await record_inviting_results(time_inviting[0], time_inviting[1], username)
                            except (UserIdInvalidError, UsernameNotOccupiedError, ValueError, UsernameInvalidError):
                                logger.error(
                                    f"Попытка приглашения {username} в группу {link[0]}. Не корректное имя {username}")
                                await record_inviting_results(time_inviting[0], time_inviting[1], username)
                            except ChatAdminRequiredError:
                                logger.error(
                                    f"Попытка приглашения {username} в группу {link[0]}. Требуются права администратора.")
                                await record_inviting_results(time_inviting[0], time_inviting[1], username)
                            except UserPrivacyRestrictedError:
                                logger.error(
                                    f"Попытка приглашения {username} в группу {link[0]}. Настройки конфиденциальности {username} не позволяют вам inviting")
                                await record_inviting_results(time_inviting[0], time_inviting[1], username)
                            except BotGroupsBlockedError:
                                logger.error(
                                    f"Попытка приглашения {username} в группу {link[0]}. Вы не можете добавить бота в группу.")
                                await record_inviting_results(time_inviting[0], time_inviting[1], username)
                            except (TypeError, UnboundLocalError):
                                logger.error(f"Попытка приглашения {username} в группу {link[0]}")
                            # Ошибка инвайтинга прерываем работу
                            except ChatWriteForbiddenError:
                                logger.error(
                                    f"Попытка приглашения {username} в группу {link[0]}. Настройки в чате не дают добавлять людей в чат, возможно стоит бот админ и нужно подписаться на другие проекты")
                                await record_inviting_results(time_inviting[0], time_inviting[1], username)
                                break  # Прерываем работу и меняем аккаунт
                            except InviteRequestSentError:
                                logger.error(
                                    f"Попытка приглашения {username} в группу {link[0]}. Доступ к функциям группы станет возможен после утверждения заявки администратором на {link[0]}")
                                await record_inviting_results(time_inviting[0], time_inviting[1], username)
                                break  # Прерываем работу и меняем аккаунт
                            # except (UserIdInvalidError, UsernameNotOccupiedError, ValueError, UsernameInvalidError):
                            #     logger.error(f"Попытка приглашения {username} в группу {link[0]}. Не корректное имя {username}")
                            #     await record_inviting_results(time_inviting[0], time_inviting[1], username)
                            #     break  # Прерываем работу и меняем аккаунт
                            except (
                                    ChannelPrivateError, TypeNotFoundError, AuthKeyDuplicatedError,
                                    UserBannedInChannelError):
                                await record_and_interrupt(time_inviting[0], time_inviting[1])
                                break  # Прерываем работу и меняем аккаунт
                            except FloodWaitError as error:
                                logger.error(f'{error}')
                                await record_and_interrupt(time_inviting[0], time_inviting[1])
                                break  # Прерываем работу и меняем аккаунт
                            except PeerFloodError:
                                logger.error(
                                    f"Попытка приглашения {username} в группу {link[0]}. Настройки конфиденциальности {username} не позволяют вам inviting")
                                await record_and_interrupt(time_inviting[0], time_inviting[1])
                                break  # Прерываем работу и меняем аккаунт

                            except KeyboardInterrupt:  # Закрытие окна программы
                                client.disconnect()  # Разрываем соединение telegram
                                await self.log_and_display(f"[!] Скрипт остановлен!", lv, page)
                            except Exception as error:
                                logger.exception(f"Ошибка: {error}")
                            else:
                                logger.info(f"[+] Участник {username} добавлен, если не состоит в чате {link[0]}")
                                await record_inviting_results(time_inviting[0], time_inviting[1], username)

                        await self.sub_unsub_tg.unsubscribe_from_the_group(client, link[0])
                logger.info("[!] Инвайтинг окончен!")
            except Exception as error:
                logger.exception(f"Ошибка: {error}")

            finish = datetime.datetime.now()  # фиксируем время окончания парсинга ⏰
            # Логируем и отображаем время окончания работы
            await self.log_and_display(
                f"🔚 Конец инвайтинга.\n🕒 Время окончания: {finish}.\n⏳ Время работы: {finish - start}", lv, page)

        async def back_button_clicked(_):
            """
            ⬅️ Обрабатывает нажатие кнопки "Назад", возвращая в меню инвайтинга.
            """
            page.go("/inviting")  # переходим к основному меню инвайтинга 🏠

        # Добавляем кнопки и другие элементы управления на страницу
        page.views.append(
            ft.View(
                "/parsing",
                [
                    lv,  # отображение логов 📝
                    ft.Column(),  # резерв для приветствия или других элементов интерфейса
                    ft.ElevatedButton(width=line_width_button, height=height_button, text=start_inviting_button,
                                      on_click=add_items),  # Кнопка "🚀 Начать инвайтинг"
                    ft.ElevatedButton(width=line_width_button, height=height_button, text=back_button,
                                      on_click=back_button_clicked)  # Кнопка "⬅️ Назад"
                ],
            )
        )

        page.update()  # обновляем страницу после добавления элементов управления 🔄
