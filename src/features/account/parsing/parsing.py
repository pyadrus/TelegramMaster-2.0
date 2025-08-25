# -*- coding: utf-8 -*-
import asyncio
import os
import os.path
import sqlite3

import flet as ft  # Импортируем библиотеку flet
from loguru import logger
from telethon import functions
from telethon.errors import (AuthKeyUnregisteredError, ChannelPrivateError, ChatAdminRequiredError, FloodWaitError,
                             UsernameInvalidError)
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import ChannelParticipantsAdmins, ChannelParticipantsSearch, InputPeerEmpty, InputUser

from src.core.configs import WIDTH_WIDE_BUTTON, path_accounts_folder, TIME_ACTIVITY_USER_2, BUTTON_HEIGHT
from src.core.sqlite_working_tools import (MembersAdmin, add_member_to_db, save_group_channel_info,
                                           administrators_entries_in_database)
from src.features.account.TGConnect import TGConnect
from src.features.account.parsing.gui_elements import GUIProgram
from src.features.account.parsing.switch_controller import ToggleController
from src.features.account.parsing.user_info import UserInfo
from src.features.account.subscribe_unsubscribe.subscribe_unsubscribe import SubscribeUnsubscribeTelegram
from src.gui.gui import end_time, list_view, log_and_display, start_time
from src.locales.translations_loader import translations


class ParsingGroupMembers:
    """Класс для парсинга групп, на которые подписан аккаунт."""

    def __init__(self, page):
        self.page = page
        self.tg_connect = TGConnect(page)

    async def collect_user_log_data(self, user):
        return {
            "username": await UserInfo().get_username(user),
            "user_id": await UserInfo().get_user_id(user),
            "access_hash": await UserInfo().get_access_hash(user),
            "first_name": await UserInfo().get_first_name(user),
            "last_name": await UserInfo().get_last_name(user),
            "user_phone": await UserInfo().get_user_phone(user),
            "online_at": await UserInfo().get_user_online_status(user),
            "photos_id": await UserInfo().get_photo_status(user),
            "user_premium": await UserInfo().get_user_premium_status(user),
        }

    async def parse_group(self, groups_wr) -> None:
        """
        Выполняет парсинг групп, на которые пользователь подписался. Аргумент phone используется декоратором
        @handle_exceptions для отлавливания ошибок и записи их в базу данных user_data/software_database.db.

        :param groups_wr: ссылка на группу
        """
        phone = self.page.session.get("selected_sessions") or []
        logger.debug(f"Аккаунт: {phone}")
        client = await TGConnect(self.page).get_telegram_client(phone[0], account_directory=path_accounts_folder)
        await log_and_display("🔍 Ищем участников... 💾 Сохраняем в файл software_database.db...", self.page)
        try:
            all_participants: list = []
            while_condition = True
            my_filter = ChannelParticipantsSearch("")
            offset = 0
            while while_condition:
                try:
                    logger.warning(f"🔍 Получаем участников группы: {groups_wr}")
                    participants = await client(
                        GetParticipantsRequest(channel=groups_wr, offset=offset, filter=my_filter, limit=200, hash=0, ))
                    all_participants.extend(participants.users)
                    offset += len(participants.users)
                    if len(participants.users) < 1:
                        while_condition = False
                except TypeError:
                    await log_and_display(f"❌ Ошибка: {groups_wr} не является группой / каналом.", self.page,
                                          level="error", )
                    await asyncio.sleep(2)
                    break
                except ChatAdminRequiredError:
                    await log_and_display(translations["ru"]["errors"]["admin_rights_required"], self.page)
                    await asyncio.sleep(2)
                    break
                except ChannelPrivateError:
                    await log_and_display(translations["ru"]["errors"]["channel_private"], self.page)
                    await asyncio.sleep(2)
                    break
                except AuthKeyUnregisteredError:
                    await log_and_display(translations["ru"]["errors"]["auth_key_unregistered"], self.page)
                    await asyncio.sleep(2)
                    break
                except sqlite3.DatabaseError:  # TODO Обработка ошибок базы данных (придумать универсальнео наименование)
                    await log_and_display("Ошибка дазы данных аккаунта", self.page)
                    await asyncio.sleep(2)
                    break

            for user in all_participants:
                await log_and_display(f"Полученные данные: {user}", self.page)
                logger.info(f"Полученные данные: {user}")
                # user_premium = "Пользователь с premium" if user.premium else "Обычный пользователь"
                log_data = await self.collect_user_log_data(user)
                add_member_to_db(log_data)

        except TypeError as error:
            logger.exception(f"❌ Ошибка: {error}")
            return []  # Возвращаем пустой список в случае ошибки
        except Exception as error:
            logger.exception(error)

    async def account_selection_menu(self):

        async def btn_click_file_picker(e: ft.FilePickerResultEvent):
            if not e.files:
                file_text.value = "❌ Файл не выбран"
                file_text.color = ft.Colors.RED
                self.page.update()
                return

            file = e.files[0]
            if not file.name.endswith(".session"):
                file_text.value = f"❌ Неверный файл: {file.name}"
                file_text.color = ft.Colors.RED
                self.page.update()
                return

            # Просто сохраняем путь к session-файлу
            phone = os.path.splitext(os.path.basename(file.name))[0]  # например, "77076324730"
            # Сохраняем название session-файла
            self.page.session.set("selected_sessions", [phone])

            # Показываем успешный выбор
            file_text.value = f"✅ Аккаунт выбран: {phone}"
            file_text.color = ft.Colors.GREEN

            # 🔓 Разблокируем интерфейс
            admin_switch.disabled = False
            members_switch.disabled = False
            account_groups_switch.disabled = False
            active_switch.disabled = False

            chat_input.disabled = False
            limit_active_user.disabled = False

            dropdown.disabled = False
            parse_button.disabled = False

            self.page.update()

        # Создание элементов управления
        file_text = ft.Text(value="📂 Выберите .session файл", size=14)
        file_picker = ft.FilePicker(on_result=btn_click_file_picker)
        self.page.overlay.append(file_picker)
        pick_button = ft.ElevatedButton(text="📁 Выбрать session файл", width=WIDTH_WIDE_BUTTON, height=BUTTON_HEIGHT,
                                        on_click=lambda _: file_picker.pick_files(allow_multiple=False))

        # Кнопки-переключатели
        account_groups_switch = ft.CupertinoSwitch(label="Группы аккаунта", value=False, disabled=True)
        admin_switch = ft.CupertinoSwitch(label="Администраторов", value=False, disabled=True)
        members_switch = ft.CupertinoSwitch(label="Участников", value=False, disabled=True)
        # Todo добавить работу
        active_switch = ft.CupertinoSwitch(label="Активные", value=False, disabled=True)
        account_group_selection_switch = ft.CupertinoSwitch(label="Выбрать группу", value=False, disabled=True)
        # Todo добавить работу
        contacts_switch = ft.CupertinoSwitch(label="Контакты", value=False, disabled=True)

        ToggleController(admin_switch, account_groups_switch, members_switch, account_group_selection_switch,
                         active_switch).element_handler(self.page)

        async def add_items(_):
            """🚀 Запускает процесс парсинга групп и отображает статус в интерфейсе."""
            try:
                data = chat_input.value.split()
                logger.info(f"Полученные данные: {data}")  # Отладка
                # Удаляем дубликаты ссылок введенных пользователем
                start = await start_time(self.page)
                self.page.update()  # Обновите страницу, чтобы сразу показать сообщение 🔄
                try:
                    if account_groups_switch.value:  # Парсинг групп, на которые подписан аккаунт
                        await self.parsing_account_groups()
                    if admin_switch.value:  # Если выбрано парсить администраторов, выполняем парсинг администраторов 👤
                        for groups in data:
                            await self.obtaining_administrators(groups)
                    if members_switch.value:  # Парсинг участников
                        for groups in data:
                            await self.parse_group(groups)
                    if active_switch.value:  # Парсинг активных пользователей
                        await self.start_active_parsing(self.page, limit_active_user)
                    if account_group_selection_switch.value:  # Парсинг выбранной группы
                        await self.load_groups(dropdown, result_text)  # ⬅️ Подгружаем группы
                        await self.start_group_parsing(dropdown, result_text)
                    await end_time(start, self.page)
                except Exception as error:
                    logger.exception(error)
            except Exception as error:
                logger.exception(error)

        chat_input = ft.TextField(label="🔗 Введите ссылку на чат...", disabled=True)
        limit_active_user = ft.TextField(label="💬 Кол-во сообщений", expand=True, disabled=True)
        # Выпадающий список для выбора группы
        dropdown = ft.Dropdown(width=WIDTH_WIDE_BUTTON, options=[], autofocus=True, disabled=True)
        result_text = ft.Text(value="📂 Группы не загружены")
        parse_button = ft.ElevatedButton(text="🔍 Парсить", width=WIDTH_WIDE_BUTTON, height=BUTTON_HEIGHT,
                                         on_click=add_items, disabled=True)

        # После успешного выбора файла:
        admin_switch.disabled = False
        members_switch.disabled = False
        account_groups_switch.disabled = False
        account_group_selection_switch.disabled = False
        active_switch.disabled = False
        chat_input.disabled = False
        limit_active_user.disabled = False
        dropdown.disabled = False
        parse_button.disabled = False

        # Выравнивание элементов управления
        admin_switch.expand = True
        members_switch.expand = True
        account_groups_switch.expand = True

        account_group_selection_switch.expand = True
        active_switch.expand = True
        contacts_switch.expand = True
        self.page.update()

        # Представление (View)
        view = ft.View(
            route="/parsing",
            controls=[
                await GUIProgram().key_app_bar(),
                await GUIProgram().outputs_text_gradient(),
                list_view,
                ft.Column([
                    file_text,
                    pick_button,
                    ft.Row([admin_switch, members_switch, account_groups_switch, ]),
                    ft.Row([account_group_selection_switch, active_switch, contacts_switch, ]),
                    chat_input,
                    await GUIProgram().diver_castom(),  # Горизонтальная линия
                    ft.Row([limit_active_user]),
                    await GUIProgram().diver_castom(),  # Горизонтальная линия
                    result_text,
                    dropdown,
                    parse_button,  # ⬅️ Кнопка для парсинга
                ])
            ]
        )
        self.page.views.append(view)
        self.page.update()

    async def start_group_parsing(self, dropdown, result_text):
        phone = await self.load_groups(dropdown, result_text)
        logger.warning(f"🔍 Аккаунт: {phone}")
        client = await self.tg_connect.get_telegram_client(phone, path_accounts_folder)
        if not dropdown.value:
            await log_and_display("⚠️ Группа не выбрана", self.page)
            return
        await log_and_display(f"▶️ Парсинг группы: {dropdown.value}", self.page)
        logger.warning(f"🔍 Парсим группу: {dropdown.value}")
        await self.parse_group(dropdown.value)
        await client.disconnect()
        await log_and_display("🔚 Парсинг завершен", self.page)

    async def start_active_parsing(self, chat_input_active, limit_active_user):
        selected = self.page.session.get("selected_sessions") or []
        if not selected:
            await log_and_display("⚠️ Сначала выберите аккаунт", self.page)
            return

        phone = self.page.session.get("selected_sessions") or []
        logger.debug(f"Аккаунт: {phone}")
        chat = chat_input_active.value
        try:
            limit = int(limit_active_user.value)
        except ValueError:
            await log_and_display("⚠️ Некорректное число сообщений", self.page)
            return

        await log_and_display(f"🔍 Сканируем чат: {chat} на {limit} сообщений", self.page)
        await self.parse_active_users(chat, limit, phone[0])

    async def load_groups(self, dropdown, result_text):
        try:
            selected = self.page.session.get("selected_sessions") or []
            if not selected:
                await log_and_display("⚠️ Сначала выберите аккаунт", self.page)
                return

            session_path = selected[0]
            phone = os.path.splitext(os.path.basename(session_path))[0]
            logger.warning(f"🔍 Работаем с аккаунтом {phone}")
            client = await self.tg_connect.get_telegram_client(phone, path_accounts_folder)
            result = await client(
                GetDialogsRequest(offset_date=None, offset_id=0, offset_peer=InputPeerEmpty(), limit=200, hash=0))
            groups = await self.filtering_groups(result.chats)
            titles = await self.name_of_the_groups(groups)
            dropdown.options = [ft.dropdown.Option(t) for t in titles]
            result_text.value = f"🔽 Найдено групп: {len(titles)}"
            self.page.update()
            return phone
        except Exception as e:
            logger.exception(e)
            return None

    async def obtaining_administrators(self, groups):
        """
        Получает информацию об администраторах группы, включая их биографию, статус, фото и премиум-статус.
        """
        try:
            phone = self.page.session.get("selected_sessions") or []
            logger.debug(f"Аккаунт: {phone}")
            try:
                client = await self.tg_connect.get_telegram_client(phone[0],
                                                                   account_directory=path_accounts_folder)
                await log_and_display(f"🔍 Парсинг группы: {groups}", self.page)
                try:
                    entity = await client.get_entity(groups)  # Получаем сущность группы/канала
                    # Проверяем, является ли сущность супергруппой
                    if hasattr(entity, "megagroup") and entity.megagroup:
                        # Получаем итератор администраторов
                        async for user in client.iter_participants(entity, filter=ChannelParticipantsAdmins):
                            # Формируем отображаемое имя администратора
                            admin_name = (user.first_name or "").strip()
                            if user.last_name:
                                admin_name += f" {user.last_name}"

                            # Получаем полную информацию о пользователе
                            log_data = {
                                "username": await UserInfo().get_username(user),
                                "user_id": await UserInfo().get_user_id(user),
                                "access_hash": await UserInfo().get_access_hash(user),
                                "first_name": await UserInfo().get_first_name(user),
                                "last_name": await UserInfo().get_last_name(user),
                                "phone": await UserInfo().get_user_phone(user),
                                "online_at": await UserInfo().get_user_online_status(user),
                                "photo_status": await UserInfo().get_photo_status(user),
                                "premium_status": await UserInfo().get_user_premium_status(user),
                                "user_status": "Admin",
                                "bio": await UserInfo().get_bio_user(await UserInfo().get_full_user_info(user, client)),
                                "group": groups,
                            }
                            # Задержка для избежания ограничений Telegram API
                            await asyncio.sleep(0.5)
                            await log_and_display(f"Полученные данные: {log_data}", self.page)

                            existing_user = MembersAdmin.select().where(
                                MembersAdmin.user_id == log_data["user_id"]).first()
                            if not existing_user:
                                administrators_entries_in_database(log_data)
                            else:
                                await log_and_display(
                                    f"⚠️ Пользователь с user_id {log_data['user_id']} уже есть в базе. Пропущен.",
                                    self.page)
                    else:
                        try:
                            await log_and_display(f"Это не группа, а канал: {entity.title}", self.page)
                            # Удаляем группу из списка после завершения парсинга 🗑️
                        except AttributeError:
                            await log_and_display(f"⚠️ Ошибка при получении сущности группы {groups[0]}", self.page)
                except UsernameInvalidError:
                    await log_and_display(translations["ru"]["errors"]["group_entity_error"], self.page)
                except ValueError:
                    await log_and_display(translations["ru"]["errors"]["group_entity_error"], self.page)
                await client.disconnect()
            except FloodWaitError as e:
                await log_and_display(f"{translations["ru"]["errors"]["flood_wait"]}{e}", self.page, level="error", )
                await client.disconnect()
        except Exception as error:
            logger.exception(error)

    async def parsing_account_groups(self):
        # Обрабатываем все файлы сессий по очереди 📂
        phone = self.page.session.get("selected_sessions") or []
        logger.debug(f"🔍 Парсинг групп/каналов, в которых состоит аккаунт: {phone}")
        client = await self.tg_connect.get_telegram_client(phone[0], account_directory=path_accounts_folder)
        await log_and_display(
            f"🔗 Подключение к аккаунту: {phone}\n 🔄 Парсинг групп/каналов, на которые подписан аккаунт", self.page)
        await self.forming_a_list_of_groups(client)

    async def parse_active_users(self, chat_input, limit_active_user, phone_number) -> None:
        """
        Парсинг активных пользователей в чате.
        """
        try:
            client = await self.tg_connect.get_telegram_client(phone_number,
                                                               account_directory=path_accounts_folder)
            await SubscribeUnsubscribeTelegram(self.page).subscribe_to_group_or_channel(client, chat_input)
            try:
                await asyncio.sleep(int(TIME_ACTIVITY_USER_2 or 5))
            except TypeError:
                await asyncio.sleep(5)
            # Все операции с Telegram API должны быть здесь
            await self.get_active_users(client, chat_input, limit_active_user)
        except Exception as error:
            logger.exception(error)

    async def get_active_users(self, client, chat, limit_active_user) -> None:
        """
        Получаем данные участников группы которые писали сообщения.

        :param client: Клиент Telegram
        :param chat: ссылка на чат
        :param limit_active_user: лимит активных участников
        """
        try:
            entity = await client.get_entity(chat)
            async for message in client.iter_messages(entity, limit=limit_active_user):
                from_id = getattr(message, 'from_id', None)
                if from_id:
                    user = await client.get_entity(from_id)
                    try:
                        await log_and_display(f"{message.from_id}", self.page)
                        # Получаем входную сущность пользователя
                        from_user = InputUser(user_id=await UserInfo().get_user_id(user),
                                              access_hash=await UserInfo().get_access_hash(user))  # Создаем InputUser
                        await log_and_display(f"{from_user}", self.page)
                        # Получаем данные о пользователе
                        log_data = await self.collect_user_log_data(user)
                        await log_and_display(f"{log_data}", self.page)
                        await add_member_to_db(log_data)
                    except ValueError as e:
                        await log_and_display(
                            f"❌ Не удалось найти сущность для пользователя {message.from_id.user_id}: {e}", self.page, )
                else:
                    await log_and_display(f"Сообщение {message.id} не имеет действительного from_id.", self.page, )
        except Exception as error:
            logger.exception(error)

    @staticmethod
    async def filtering_groups(chats):
        """
        Фильтрация чатов для получения только групп.

        :param chats: Список чатов.
        :return: Список групп.
        """
        groups = []
        for chat in chats:
            try:
                if chat.megagroup:
                    groups.append(chat)
            except AttributeError:
                continue  # Игнорируем объекты без атрибута megagroup
        return groups

    @staticmethod
    async def name_of_the_groups(groups):
        """
        Получение названий групп.

        :param groups: Список групп.
        :return: Список названий групп.
        """
        group_names = []  # Создаем новый список для названий групп
        for group in groups:
            group_names.append(group.title)  # Добавляем название группы в список
        return group_names

    async def forming_a_list_of_groups(self, client) -> None:
        """
        Формирует список групп и каналов без дублирования записей.

        Метод собирает информацию о группах и каналах, включая их ID, название, описание, ссылку, количество участников
        и время последнего парсинга. Данные сохраняются в базу данных.

        :param client: Экземпляр клиента Telegram.
        """
        try:
            async for dialog in client.iter_dialogs():
                try:
                    entity = await client.get_entity(dialog.id)
                    # Пропускаем личные чаты
                    from telethon.tl.types import Chat, Channel
                    if isinstance(entity, Chat):
                        logger.debug(f"💬 Пропущен личный чат: {dialog.id}")
                        continue
                    # Проверяем, является ли супергруппой или каналом
                    if not getattr(entity, 'megagroup', False) and not getattr(entity, 'broadcast', False):
                        continue
                    full_channel_info = await client(functions.channels.GetFullChannelRequest(channel=entity))
                    chat = full_channel_info.full_chat
                    if not hasattr(chat, 'participants_count'):
                        logger.warning(f"⚠️ participants_count отсутствует для {dialog.id}")
                        continue
                    participants_count = chat.participants_count
                    username = getattr(entity, 'username', None)
                    link = f"https://t.me/{username}" if username else None
                    title = entity.title or "Без названия"
                    about = getattr(chat, 'about', '')
                    # Логируем информацию
                    await log_and_display(f"{dialog.id}, {title}, {link or 'без ссылки'}, {participants_count}",
                                          self.page, )
                    await save_group_channel_info(dialog, title, about, link, participants_count)
                except TypeError as te:
                    logger.warning(f"❌ TypeError при обработке диалога {dialog.id}: {te}")
                    continue
                except Exception as e:
                    logger.exception(f"⚠️ Ошибка при обработке диалога {dialog.id}: {e}")
                    continue
        except Exception as error:
            logger.exception(f"🔥 Критическая ошибка в forming_a_list_of_groups: {error}")

# 690
