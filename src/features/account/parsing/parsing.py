# -*- coding: utf-8 -*-
import asyncio
import os
import os.path
import sqlite3
import time

import flet as ft  # Импортируем библиотеку flet
from loguru import logger
from telethon import functions
from telethon.errors import (AuthKeyUnregisteredError, ChannelPrivateError, ChatAdminRequiredError, FloodWaitError,
                             UsernameInvalidError)
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import (ChannelParticipantsAdmins, ChannelParticipantsSearch, InputPeerEmpty, InputUser)

from src.core.configs import (line_width_button, path_accounts_folder, time_activity_user_2, BUTTON_HEIGHT)
from src.core.sqlite_working_tools import (GroupsAndChannels, MembersAdmin, MembersGroups, db, remove_duplicates)
from src.features.account.TGConnect import TGConnect
from src.features.account.TGSubUnsub import SubscribeUnsubscribeTelegram
from src.features.account.parsing.gui_elements import GUIProgram
from src.features.account.parsing.switch_controller import ToggleController
from src.features.account.parsing.user_info import UserInfo
from src.gui.gui import end_time, list_view, log_and_display, start_time
from src.locales.translations_loader import translations


async def collect_user_log_data(user):
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


async def parse_group(client, groups_wr, page) -> None:
    """
    Эта функция выполняет парсинг групп, на которые пользователь подписался. Аргумент phone используется декоратором
    @handle_exceptions для отлавливания ошибок и записи их в базу данных user_data/software_database.db.

    :param client: Клиент Telegram
    :param groups_wr: ссылка на группу
    :param page: Страница интерфейса Flet для отображения элементов управления.
    """
    await client.connect()
    await log_and_display("🔍 Ищем участников... 💾 Сохраняем в файл software_database.db...", page)
    try:
        all_participants: list = []
        while_condition = True
        my_filter = ChannelParticipantsSearch("")
        offset = 0
        while while_condition:
            try:
                logger.warning(f"🔍 Получаем участников группы: {groups_wr}")
                participants = await client(
                    GetParticipantsRequest(channel=groups_wr, offset=offset, filter=my_filter,
                                           limit=200, hash=0, ))

                all_participants.extend(participants.users)
                offset += len(participants.users)
                if len(participants.users) < 1:
                    while_condition = False
            except TypeError:
                await log_and_display(f"❌ Ошибка: {groups_wr} не является группой / каналом.", page,
                                      level="error", )
                await asyncio.sleep(2)
                break
            except ChatAdminRequiredError:
                await log_and_display(translations["ru"]["errors"]["admin_rights_required"], page)
                await asyncio.sleep(2)
                break
            except ChannelPrivateError:
                await log_and_display(translations["ru"]["errors"]["channel_private"], page)
                await asyncio.sleep(2)
                break
            except AuthKeyUnregisteredError:
                await log_and_display(translations["ru"]["errors"]["auth_key_unregistered"], page)
                await asyncio.sleep(2)
                break

        for user in all_participants:
            await log_and_display(f"Полученные данные: {user}", page)
            logger.info(f"Полученные данные: {user}")
            # user_premium = "Пользователь с premium" if user.premium else "Обычный пользователь"
            log_data = await collect_user_log_data(user)
            with db.atomic():  # Атомарная транзакция для записи данных
                MembersGroups.get_or_create(
                    user_id=log_data["user_id"],
                    defaults={
                        "username": log_data["username"],
                        "access_hash": log_data["access_hash"],
                        "first_name": log_data["first_name"],
                        "last_name": log_data["last_name"],
                        "user_phone": log_data["user_phone"],
                        "online_at": log_data["online_at"],
                        "photos_id": log_data["photos_id"],
                        "user_premium": log_data["user_premium"],
                    },
                )
    except TypeError as error:
        logger.exception(f"❌ Ошибка: {error}")
        return []  # Возвращаем пустой список в случае ошибки
    except Exception as error:
        logger.exception(error)
        logger.exception(error)


class ParsingGroupMembers:
    """Класс для парсинга групп, на которые подписан аккаунт."""

    def __init__(self):
        self.tg_connect = TGConnect()
        self.tg_subscription_manager = SubscribeUnsubscribeTelegram()

    async def account_selection_menu(self, page):

        async def btn_click_file_picker(e: ft.FilePickerResultEvent):
            if not e.files:
                file_text.value = "❌ Файл не выбран"
                file_text.color = ft.Colors.RED
                page.update()
                return

            file = e.files[0]
            if not file.name.endswith(".session"):
                file_text.value = f"❌ Неверный файл: {file.name}"
                file_text.color = ft.Colors.RED
                page.update()
                return

            # Просто сохраняем путь к session-файлу
            phone = os.path.splitext(os.path.basename(file.name))[0]  # например, "77076324730"
            # Сохраняем название session-файла
            page.session.set("selected_sessions", [phone])

            # Показываем успешный выбор
            file_text.value = f"✅ Аккаунт выбран: {phone}"
            file_text.color = ft.Colors.GREEN

            # 🔓 Разблокируем интерфейс
            admin_switch.disabled = False
            members_switch.disabled = False
            account_groups_switch.disabled = False

            chat_input.disabled = False
            chat_input_active.disabled = False
            limit_active_user.disabled = False

            dropdown.disabled = False
            # btn_active_parse.disabled = False
            # btn_group_parse.disabled = False
            parse_button.disabled = False

            page.update()

        # Создание элементов управления
        file_text = ft.Text(value="📂 Выберите .session файл", size=14)
        file_picker = ft.FilePicker(on_result=btn_click_file_picker)
        page.overlay.append(file_picker)
        pick_button = ft.ElevatedButton(text="📁 Выбрать session файл", width=line_width_button, height=BUTTON_HEIGHT,
                                        on_click=lambda _: file_picker.pick_files(allow_multiple=False))

        # Кнопки-переключатели
        admin_switch = ft.CupertinoSwitch(label="Администраторов", value=False, disabled=True)
        members_switch = ft.CupertinoSwitch(label="Участников", value=False, disabled=True)
        account_groups_switch = ft.CupertinoSwitch(label="Группы аккаунта", value=False, disabled=True)
        account_group_selection_switch = ft.CupertinoSwitch(label="Выбрать группу", value=False, disabled=True)
        # Todo добавить работу
        active_switch = ft.CupertinoSwitch(label="Активные", value=False, disabled=True)
        # Todo добавить работу
        contacts_switch = ft.CupertinoSwitch(label="Контакты", value=False, disabled=True)

        ToggleController(admin_switch, account_groups_switch, members_switch,
                         account_group_selection_switch).element_handler(page)

        async def add_items(_):
            """🚀 Запускает процесс парсинга групп и отображает статус в интерфейсе."""
            try:
                data = chat_input.value.split()
                logger.info(f"Полученные данные: {data}")  # Отладка

                # Удаляем дубликаты ссылок введенных пользователем
                # await write_to_single_column_table_peewee(data)

                start = await start_time(page)
                page.update()  # Обновите страницу, чтобы сразу показать сообщение 🔄
                try:
                    if account_groups_switch.value:  # Парсинг групп, на которые подписан аккаунт
                        await self.parsing_account_groups(page)
                    if admin_switch.value:  # Если выбрано парсить администраторов, выполняем парсинг администраторов 👤
                        for groups in data:
                            await self.obtaining_administrators(groups, page)
                    if members_switch.value:  # Парсинг участников
                        phone = page.session.get("selected_sessions") or []
                        logger.warning(f"Парсинг участников с аккаунта {phone[0]}")
                        for groups in data:
                            await log_and_display(f"🔍 Парсинг группы: {groups}", page)
                            # подписываемся на группу
                            client = await self.tg_connect.get_telegram_client(page, phone[0],
                                                                               account_directory=path_accounts_folder)
                            group = await client.get_entity(groups)
                            await self.tg_subscription_manager.subscribe_to_group_or_channel(client, groups, page)
                            offset = 0
                            limit = 100
                            all_participants = []

                            while True:
                                try:
                                    participants = await client(GetParticipantsRequest(
                                        channel=group,
                                        filter=ChannelParticipantsSearch(''),  # Пустая строка = все участники
                                        offset=offset,
                                        limit=limit,
                                        hash=0
                                    ))
                                except Exception as e:
                                    print(f"Ошибка при получении участников: {e}")
                                    break

                                if not participants.users:
                                    break

                                all_participants.extend(participants.users)
                                offset += len(participants.users)

                                print(f"Спарсили {len(all_participants)} участников...")

                            # Выводим данные участников
                            for user in all_participants:
                                print(f"{user.id} | @{user.username} | {user.first_name} {user.last_name}")

                            # Завершаем работу клиента после завершения парсинга 🔌
                            try:
                                await client.disconnect()
                            except sqlite3.DatabaseError:
                                await log_and_display(
                                    f"❌ Ошибка при отключении аккаунта {phone[0]}, возможно поврежденный аккаунт. Выполните проверку аккаунтов",
                                    page, )
                                await log_and_display(f"🔌 Отключение от аккаунта: {phone[0]}", page)

                    if active_switch.value:  # Парсинг активных пользователей
                        await self.start_active_parsing(page, chat_input_active, limit_active_user)
                    if account_group_selection_switch.value:  # Парсинг выбранной группы
                        await self.load_groups(page, dropdown, result_text)  # ⬅️ Подгружаем группы
                        await self.start_group_parsing(page, dropdown, result_text)

                    await end_time(start, page)
                except Exception as error:
                    logger.exception(error)
            except Exception as error:
                logger.exception(error)

        chat_input = ft.TextField(label="🔗 Введите ссылку на чат...", disabled=True)
        chat_input_active = ft.TextField(label="🔗 Ссылка для активных", expand=True, disabled=True)
        limit_active_user = ft.TextField(label="💬 Кол-во сообщений", expand=True, disabled=True)

        # Выпадающий список для выбора группы
        dropdown = ft.Dropdown(width=line_width_button, options=[], autofocus=True, disabled=True)
        result_text = ft.Text(value="📂 Группы не загружены")

        parse_button = ft.ElevatedButton(text="🔍 Парсить", width=line_width_button, height=BUTTON_HEIGHT,
                                         on_click=add_items, disabled=True)

        # После успешного выбора файла:
        admin_switch.disabled = False
        members_switch.disabled = False
        account_groups_switch.disabled = False
        account_group_selection_switch.disabled = False
        chat_input.disabled = False
        chat_input_active.disabled = False
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
        page.update()

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
                    ft.Divider(),
                    ft.Row([chat_input_active, limit_active_user]),
                    ft.Divider(),
                    result_text,
                    dropdown,
                    parse_button,  # ⬅️ Кнопка для парсинга
                ])
            ]
        )
        page.views.append(view)
        page.update()

    async def start_group_parsing(self, page, dropdown, result_text):
        phone = await self.load_groups(page, dropdown, result_text)
        logger.warning(f"🔍 Аккаунт: {phone}")
        client = await self.tg_connect.get_telegram_client(page, phone, path_accounts_folder)
        if not dropdown.value:
            await log_and_display("⚠️ Группа не выбрана", page)
            return
        await log_and_display(f"▶️ Парсинг группы: {dropdown.value}", page)
        logger.warning(f"🔍 Парсим группу: {dropdown.value}")
        await parse_group(client, dropdown.value, page)
        await client.disconnect()
        await log_and_display("🔚 Парсинг завершен", page)

    async def start_active_parsing(self, page, chat_input_active, limit_active_user):
        selected = page.session.get("selected_sessions") or []
        if not selected:
            await log_and_display("⚠️ Сначала выберите аккаунт", page)
            return

        phone = os.path.splitext(os.path.basename(selected[0]))[0]
        chat = chat_input_active.value
        try:
            limit = int(limit_active_user.value)
        except ValueError:
            await log_and_display("⚠️ Некорректное число сообщений", page)
            return

        await log_and_display(f"🔍 Сканируем чат: {chat} на {limit} сообщений", page)
        await self.parse_active_users(chat, limit, page, phone)

    async def load_groups(self, page, dropdown, result_text):
        try:
            selected = page.session.get("selected_sessions") or []
            if not selected:
                await log_and_display("⚠️ Сначала выберите аккаунт", page)
                return

            session_path = selected[0]
            phone = os.path.splitext(os.path.basename(session_path))[0]
            logger.warning(f"🔍 Работаем с аккаунтом {phone}")
            client = await self.tg_connect.get_telegram_client(page, phone, path_accounts_folder)
            result = await client(
                GetDialogsRequest(offset_date=None, offset_id=0, offset_peer=InputPeerEmpty(), limit=200, hash=0))
            groups = await self.filtering_groups(result.chats)
            titles = await self.name_of_the_groups(groups)
            dropdown.options = [ft.dropdown.Option(t) for t in titles]
            result_text.value = f"🔽 Найдено групп: {len(titles)}"
            page.update()
            return phone
        except Exception as e:
            logger.exception(e)
            return None

    async def obtaining_administrators(self, groups, page: ft.Page):
        """
        Получает информацию об администраторах группы, включая их биографию, статус, фото и премиум-статус.
        """
        try:
            phone = page.session.get("selected_sessions") or []
            logger.debug(f"Аккаунт: {phone}")
            try:
                client = await self.tg_connect.get_telegram_client(page, phone[0], account_directory=path_accounts_folder)
                # for groups in await self.db_handler.open_and_read_data(table_name="writing_group_links", page=page):
                await log_and_display(f"🔍 Парсинг группы: {groups}", page)
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

                            full_user = await client(GetFullUserRequest(id=await UserInfo().get_user_id(user)))
                            bio = full_user.full_user.about or ""

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
                                "bio": bio,
                                "group": groups[0],
                            }
                            # Задержка для избежания ограничений Telegram API
                            await asyncio.sleep(0.5)
                            await log_and_display(f"Полученные данные: {log_data}", page)
                            with db.atomic():  # Атомарная транзакция для записи данных
                                MembersAdmin.create(
                                    username=log_data["username"],
                                    user_id=log_data["user_id"],
                                    access_hash=log_data["access_hash"],
                                    first_name=log_data["first_name"],
                                    last_name=log_data["last_name"],
                                    phone=log_data["phone"],
                                    online_at=log_data["online_at"],
                                    photo_status=log_data["photo_status"],
                                    premium_status=log_data["premium_status"],
                                    user_status=log_data["user_status"],
                                    bio=log_data["bio"],
                                    group_name=log_data["group"],
                                )
                    else:
                        try:
                            await log_and_display(f"Это не группа, а канал: {entity.title}", page)
                            # Удаляем группу из списка после завершения парсинга 🗑️
                        except AttributeError:
                            await log_and_display(f"⚠️ Ошибка при получении сущности группы {groups[0]}",
                                                  page, )
                except UsernameInvalidError:
                    await log_and_display(translations["ru"]["errors"]["group_entity_error"], page)
                except ValueError:
                    await log_and_display(translations["ru"]["errors"]["group_entity_error"], page)
                await client.disconnect()
            except FloodWaitError as e:
                await log_and_display(f"{translations["ru"]["errors"]["flood_wait"]}{e}", page, level="error", )
                await client.disconnect()
        except Exception as error:
            logger.exception(error)

    async def parsing_account_groups(self, page):
        # Обрабатываем все файлы сессий по очереди 📂
        phone = page.session.get("selected_sessions") or []
        logger.debug(f"🔍 Парсинг групп/каналов, в которых состоит аккаунт: {phone}")
        client = await self.tg_connect.get_telegram_client(page, phone, account_directory=path_accounts_folder)
        await log_and_display(
            f"🔗 Подключение к аккаунту: {phone}\n 🔄 Парсинг групп/каналов, на которые подписан аккаунт", page)
        await self.forming_a_list_of_groups(client, page)
        remove_duplicates()  # Чистка дубликатов в базе данных 🧹 (таблица groups_and_channels, колонка id)

    async def parse_active_users(self, chat_input, limit_active_user, page, phone_number) -> None:
        """
        Parsing участников, которые пишут в чат (активных участников)

        :param chat_input: Ссылка на чат
        :param limit_active_user: лимит активных участников
        :param page: Страница интерфейса Flet для отображения элементов управления.
        :param phone_number: Номер телефона пользователя
        """
        try:
            client = await self.tg_connect.get_telegram_client(page, phone_number,
                                                               account_directory=path_accounts_folder)
            await self.tg_subscription_manager.subscribe_to_group_or_channel(client, chat_input, page)
            try:
                # Преобразуем значение time_activity_user_2 в целое число (если оно None, используем 5 по умолчанию).
                await asyncio.sleep(int(time_activity_user_2 or 5))  # По умолчанию 5, если None или некорректный тип
            except TypeError:
                # Если произошла ошибка преобразования (например, time_activity_user_2 имеет неподдерживаемый тип),
                # то делаем паузу по умолчанию в 5 секунд.
                await asyncio.sleep(5)  # По умолчанию 5, если None или неправильный тип
            await self.get_active_users(client, chat_input, limit_active_user, page)
            await client.disconnect()  # Разрываем соединение telegram
        except Exception as error:
            logger.exception(error)

    async def get_active_users(self, client, chat, limit_active_user, page) -> None:
        """
        Получаем данные участников группы которые писали сообщения.

        :param client: Клиент Telegram
        :param chat: ссылка на чат
        :param limit_active_user: лимит активных участников
        :param page: Страница интерфейса Flet для отображения элементов управления.
        """
        try:
            async for message in client.iter_messages(chat, limit=int(limit_active_user)):
                if message.from_id is not None:
                    try:
                        await log_and_display(f"{message.from_id}", page)
                        # Получаем входную сущность пользователя
                        user = await client.get_entity(message.from_id.user_id)  # Получаем полную сущность
                        from_user = InputUser(user_id=await UserInfo().get_user_id(user),
                                              access_hash=await UserInfo().get_access_hash(user))  # Создаем InputUser
                        await log_and_display(f"{from_user}", page)
                        # Получаем данные о пользователе
                        log_data = await collect_user_log_data(user)
                        await log_and_display(f"{log_data}", page)
                        with db.atomic():  # Атомарная транзакция для записи данных
                            MembersGroups.get_or_create(
                                user_id=log_data["user_id"],
                                defaults={
                                    "username": log_data["username"],
                                    "access_hash": log_data["access_hash"],
                                    "first_name": log_data["first_name"],
                                    "last_name": log_data["last_name"],
                                    "user_phone": log_data["user_phone"],
                                    "online_at": log_data["online_at"],
                                    "photos_id": log_data["photos_id"],
                                    "user_premium": log_data["user_premium"],
                                },
                            )
                    except ValueError as e:
                        await log_and_display(
                            f"❌ Не удалось найти сущность для пользователя {message.from_id.user_id}: {e}", page, )
                else:
                    await log_and_display(f"Сообщение {message.id} не имеет действительного from_id.", page, )
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

    @staticmethod
    async def forming_a_list_of_groups(client, page: ft.Page) -> None:
        """
        Формирует список групп и каналов.

        Метод собирает информацию о группах и каналах, включая их ID, название, описание, ссылку, количество участников
        и время последнего парсинга. Данные сохраняются в базу данных.

        :param client: Экземпляр клиента Telegram.
        :param page: Страница интерфейса Flet для отображения элементов управления.
        """
        try:
            async for dialog in client.iter_dialogs():
                try:
                    entity = await client.get_entity(dialog.id)
                    full_channel_info = await client(functions.channels.GetFullChannelRequest(channel=entity))
                    channel_details = await client.get_entity(full_channel_info.full_chat)
                    # Получение количества участников
                    participants_count = getattr(full_channel_info.full_chat, "participants_count", 0)
                    # Время синтаксического анализа
                    await log_and_display(
                        f"{dialog.id}, {channel_details.title}, https://t.me/{channel_details.username}, {participants_count}",
                        page, )
                    with db.atomic():  # Атомарная транзакция для записи данных
                        GroupsAndChannels.create(
                            id=dialog.id,
                            title=channel_details.title,
                            about=full_channel_info.full_chat.about,
                            link=f"https://t.me/{channel_details.username}",
                            members_count=participants_count,
                            parsing_time=time.strftime(
                                "%Y-%m-%d %H:%M:%S", time.localtime()
                            ),
                        )
                except TypeError:
                    continue  # Записываем ошибку в software_database.db и продолжаем работу
        except Exception as error:
            logger.exception(error)

    # @staticmethod
    # async def parse_users(client, target_group, page: ft.Page):
    #     """
    #     🧑‍🤝‍🧑 Парсинг и сбор данных пользователей группы или канала.
    #     Метод осуществляет поиск участников в указанной группе или канале, собирает их данные и сохраняет в файле.
    #
    #     :param client: Клиент Telegram.
    #     :param target_group: Группа или канал, участники которого будут собраны.
    #     :param page: Страница интерфейса Flet для отображения элементов управления.
    #     :return: Список участников.
    #     """
    #     try:
    #         await log_and_display("🔍 Ищем участников... 💾 Сохраняем в файл software_database.db...", page)
    #
    #         all_participants: list = []
    #         while_condition = True
    #         my_filter = ChannelParticipantsSearch("")
    #         offset = 0
    #         while while_condition:
    #             try:
    #                 participants = await client(
    #                     GetParticipantsRequest(channel=target_group, offset=offset, filter=my_filter, limit=200,
    #                                            hash=0))
    #                 all_participants.extend(participants.users)
    #                 offset += len(participants.users)
    #                 if len(participants.users) < 1:
    #                     while_condition = False
    #             except TypeError:
    #                 await log_and_display(f"❌ Ошибка: {target_group} не является группой / каналом.", page,
    #                                       level="error")
    #                 await asyncio.sleep(2)
    #                 break
    #             except ChatAdminRequiredError:
    #                 await log_and_display(translations["ru"]["errors"]["admin_rights_required"], page)
    #                 await asyncio.sleep(2)
    #                 break
    #             except ChannelPrivateError:
    #                 await log_and_display(translations["ru"]["errors"]["channel_private"], page)
    #                 await asyncio.sleep(2)
    #                 break
    #             except AuthKeyUnregisteredError:
    #                 await log_and_display(translations["ru"]["errors"]["auth_key_unregistered"], page)
    #                 await asyncio.sleep(2)
    #                 break
    #
    #         return all_participants
    #     except Exception as error:
    #         logger.exception(error)
    #         raise

    # async def get_all_participants(self, all_participants, page: ft.Page) -> list:
    #     """
    #     Сбор данных всех участников.
    #     Метод проходит по списку участников, получает их данные и сохраняет их в список сущностей.
    #
    #     :param all_participants: Список объектов участников.
    #     :param page: Страница интерфейса Flet для отображения элементов управления.
    #     :return: Список собранных данных участников.
    #     """
    #     try:
    #         entities: list = []  # Создаем пустой список для хранения данных участников
    #         for user in all_participants:
    #             await self.get_user_data(user, entities, page)
    #         return entities  # Возвращаем словарь пользователей
    #     except TypeError as error:
    #         logger.exception(f"❌ Ошибка: {error}")
    #         return []  # Возвращаем пустой список в случае ошибки
    #     except Exception as error:
    #         logger.exception(error)
    #         return []  # Возвращаем пустой список в случае ошибки

    # async def get_active_user_data(self, user):
    #     """
    #     Получаем данные активного пользователя
    #
    #     :param user: пользователь
    #     """
    #     try:
    #         entity = (
    #             await self.get_last_name(user), await self.get_user_phone(user),
    #             await self.get_user_online_status(user), await self.get_photo_status(user),
    #             await self.get_user_premium_status(user))
    #         return entity
    #     except Exception as error:
    #         logger.exception(error)
    #         raise

# 690
