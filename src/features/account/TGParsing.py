# -*- coding: utf-8 -*-
import asyncio
import datetime
import os
import os.path
import shutil
import time

import flet as ft  # Импортируем библиотеку flet
from loguru import logger
from telethon import functions, types
from telethon.errors import (AuthKeyUnregisteredError, ChatAdminRequiredError, ChannelPrivateError, FloodWaitError,
                             UsernameInvalidError)
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import (
    ChannelParticipantsAdmins, UserProfilePhoto, ChannelParticipantsSearch, InputPeerEmpty, UserStatusEmpty, InputUser,
    UserStatusLastMonth, UserStatusLastWeek, UserStatusOffline, UserStatusOnline, UserStatusRecently
)

from src.core.configs import (line_width_button, BUTTON_HEIGHT, time_activity_user_2,
                              path_accounts_folder)
from src.core.sqlite_working_tools import DatabaseHandler, db, GroupsAndChannels, remove_duplicates, MembersAdmin
from src.core.utils import find_filess
from src.features.account.TGConnect import TGConnect
from src.features.account.TGSubUnsub import SubscribeUnsubscribeTelegram
from src.gui.menu import log_and_display
from src.locales.translations_loader import translations


class ParsingGroupMembers:
    """Класс для парсинга групп, на которые подписан аккаунт."""

    def __init__(self):
        self.db_handler = DatabaseHandler()
        self.tg_connect = TGConnect()
        self.tg_subscription_manager = SubscribeUnsubscribeTelegram()

    async def clean_parsing_list_and_remove_duplicates(self, list_view, page: ft.Page):
        """Очищает список парсинга от записей без имени пользователя и удаляет дубликаты по идентификатору."""

        # Очистка списка парсинга от записей без имени пользователя
        await self.db_handler.remove_records_without_username(list_view, page)
        # Удаление дублирующихся записей по идентификатору
        await self.db_handler.remove_duplicate_ids(table_name="members", column_name="id")

    @staticmethod
    def back_button_clicked(page):
        """
        ⬅️ Обрабатывает нажатие кнопки "Назад", возвращая в меню парсинга.
        """
        page.go("/parsing")  # переходим к основному меню парсинга 🏠

    @staticmethod
    async def get_user_online_status(user):
        """
        Определяет статус онлайна пользователя на основе его статуса.
        https://core.telegram.org/type/UserStatus
        :param user: Объект пользователя из Telethon
        :return: Строка или datetime, описывающая статус онлайна
        """
        online_at = "Был(а) недавно"  # Значение по умолчанию
        if user.status:
            if isinstance(user.status, UserStatusOffline):
                online_at = user.status.was_online
            elif isinstance(user.status, UserStatusRecently):
                online_at = "Был(а) недавно"
            elif isinstance(user.status, UserStatusLastWeek):
                online_at = "Был(а) на этой неделе"
            elif isinstance(user.status, UserStatusLastMonth):
                online_at = "Был(а) в этом месяце"
            elif isinstance(user.status, UserStatusOnline):
                online_at = user.status.expires
            elif isinstance(user.status, UserStatusEmpty):
                online_at = "Статус пользователя не определен"
        return online_at

    async def obtaining_administrators(self, session_files, list_view, page: ft.Page):
        """
        Получает информацию об администраторах группы, включая их биографию, статус, фото и премиум-статус.
        """
        try:
            for session_path in session_files:
                session_name = os.path.basename(session_path)
                try:
                    client = await self.tg_connect.get_telegram_client(page, session_name,
                                                                       account_directory=path_accounts_folder,
                                                                       list_view=list_view)
                    for groups in await self.db_handler.open_and_read_data(table_name="writing_group_links",
                                                                           list_view=list_view, page=page):
                        await log_and_display(f"🔍 Парсинг группы: {groups[0]}", list_view, page)
                        try:
                            entity = await client.get_entity(groups[0])  # Получаем сущность группы/канала
                            # Проверяем, является ли сущность супергруппой
                            if hasattr(entity, 'megagroup') and entity.megagroup:
                                # Получаем итератор администраторов
                                async for user in client.iter_participants(entity, filter=ChannelParticipantsAdmins):
                                    # Формируем отображаемое имя администратора
                                    admin_name = (user.first_name or "").strip()
                                    if user.last_name:
                                        admin_name += f" {user.last_name}"
                                    # Получаем полную информацию о пользователе
                                    full_user = await client(GetFullUserRequest(id=user.id))
                                    bio = full_user.full_user.about or ""
                                    photos_id = "C фото" if isinstance(user.photo, UserProfilePhoto) else "Без фото"
                                    online_at = await self.get_user_online_status(user)
                                    user_premium = "Пользователь с premium" if user.premium else "Обычный пользователь"
                                    user_status = "Admin"
                                    log_data = {
                                        "username": user.username or "", "user_id": user.id,
                                        "access_hash": user.access_hash, "first_name": user.first_name or "",
                                        "last_name": user.last_name or "", "phone": user.phone or "",
                                        "online_at": online_at, "photo_status": photos_id,
                                        "premium_status": user_premium, "user_status": user_status,
                                        "bio": bio or "", "group": groups[0]
                                    }
                                    # Задержка для избежания ограничений Telegram API
                                    await asyncio.sleep(0.5)
                                    await log_and_display(f"Полученные данные: {log_data}", list_view, page)
                                    with db.atomic():  # Атомарная транзакция для записи данных
                                        MembersAdmin.create(
                                            username=log_data['username'], user_id=log_data['user_id'],
                                            access_hash=log_data['access_hash'], first_name=log_data['first_name'],
                                            last_name=log_data['last_name'], phone=log_data['phone'],
                                            online_at=log_data['online_at'], photo_status=log_data['photo_status'],
                                            premium_status=log_data['premium_status'],
                                            user_status=log_data['user_status'],
                                            bio=log_data['bio'], group_name=log_data['group'],
                                        )
                                # Удаляем группу из списка после завершения парсинга 🗑️
                                await self.db_handler.delete_row_db(table="writing_group_links",
                                                                    column="writing_group_links", value=groups)
                            else:
                                try:
                                    await log_and_display(f"Это не группа, а канал: {entity.title}", list_view, page)
                                    # Удаляем группу из списка после завершения парсинга 🗑️
                                    await self.db_handler.delete_row_db(table="writing_group_links",
                                                                        column="writing_group_links", value=groups)
                                except AttributeError:
                                    await log_and_display(f"⚠️ Ошибка при получении сущности группы {groups[0]}",
                                                          list_view, page)
                                    # Удаляем группу из списка после завершения парсинга 🗑️
                                    await self.db_handler.delete_row_db(table="writing_group_links",
                                                                        column="writing_group_links", value=groups)
                        except UsernameInvalidError:
                            await log_and_display(f"⚠️ Ошибка при получении сущности группы {groups[0]}", list_view,
                                                  page)
                            # Удаляем группу из списка после завершения парсинга 🗑️
                            await self.db_handler.delete_row_db(table="writing_group_links",
                                                                column="writing_group_links", value=groups)
                        except ValueError:
                            await log_and_display(f"⚠️ Ошибка при получении сущности группы {groups[0]}", list_view,
                                                  page)
                            # Удаляем группу из списка после завершения парсинга 🗑️
                            await self.db_handler.delete_row_db(table="writing_group_links",
                                                                column="writing_group_links", value=groups)
                    await client.disconnect()
                except FloodWaitError as e:
                    await log_and_display(
                        f"⚠️ Ошибка флуда аккаунта {session_name}, ожидание: {e.seconds} секунд. Переключение на другой аккаунт.",
                        list_view, page)
                    await client.disconnect()
        except Exception as e:
            logger.exception(e)

    async def parse_groups(self, page: ft.Page) -> None:
        """
        🔍 Запускает процесс парсинга групп Telegram и отображает статус процесса в GUI.

        :param page: Страница интерфейса Flet для отображения элементов управления.
        """
        start_time = datetime.datetime.now()  # фиксируем время начала выполнения кода ⏱️
        selected_sessions = []  # Список для хранения выбранных session файлов

        admin_switch = ft.CupertinoSwitch(
            label="Парсить только администраторов",
            value=False,
            tooltip="Если включено, парсятся только администраторы групп. Если выключено, парсятся все участники групп."
        )
        account_groups_switch = ft.CupertinoSwitch(
            label="Парсить группы и каналы, в которых состоит аккаунт",
            value=False,
            tooltip="Если включено, парсятся группы и каналы, в которых состоит аккаунт."
        )
        members_switch = ft.CupertinoSwitch(
            label="Парсить только участников",
            value=False,
            tooltip="Если включено, парсятся только участники групп. Если выключено, парсятся все участники групп."
        )

        # Обработчики для взаимоисключающего поведения
        def toggle_admin_switch(_):
            if admin_switch.value:
                account_groups_switch.value = False
                members_switch.value = False
            page.update()

        def toggle_account_groups_switch(_):
            if account_groups_switch.value:
                admin_switch.value = False
                members_switch.value = False
            page.update()

        def toggle_members_switch(_):
            if members_switch.value:
                admin_switch.value = False
                account_groups_switch.value = False
            page.update()

        # Присоединяем обработчики к элементам интерфейса
        admin_switch.on_change = toggle_admin_switch
        account_groups_switch.on_change = toggle_account_groups_switch
        members_switch.on_change = toggle_members_switch

        list_view = ft.ListView(expand=10, spacing=1, padding=2, auto_scroll=True)
        page.controls.append(list_view)  # добавляем ListView на страницу для отображения логов 📝
        page.update()  # обновляем страницу, чтобы сразу показать ListView 🔄

        # Поле для отображения выбранного файла
        selected_files = ft.Text(value="Session файл не выбран", size=12)

        async def add_items(_):
            """🚀 Запускает процесс парсинга групп и отображает статус в интерфейсе."""

            if not selected_sessions:
                await log_and_display("⚠️ Файлы не выбраны. Используются все session файлы из папки.", list_view, page)
                session_files = await find_filess(directory_path=path_accounts_folder, extension='session')
                if not session_files:
                    await log_and_display("❌ В папке нет session файлов для парсинга.", list_view, page)
                    page.update()
                    return
            else:
                session_files = selected_sessions
                await log_and_display(
                    f"🚀 Начало парсинга с выбранных файлов: {', '.join([os.path.basename(s) for s in selected_sessions])}",
                    list_view, page)

            # Индикация начала парсинга
            await log_and_display(f"▶️ Начало парсинга.\n🕒 Время старта: {str(start_time)}", list_view, page)
            page.update()  # Обновите страницу, чтобы сразу показать сообщение 🔄
            try:
                if account_groups_switch.value:
                    # Обрабатываем все файлы сессий по очереди 📂
                    for session_path in session_files:
                        session_name = os.path.basename(session_path)
                        client = await self.tg_connect.get_telegram_client(page, session_name,
                                                                           account_directory=path_accounts_folder,
                                                                           list_view=list_view)
                        await log_and_display(f"🔗 Подключение к аккаунту: {session_name}", list_view, page)
                        await log_and_display(f"🔄 Парсинг групп/каналов, на которые подписан аккаунт", list_view, page)
                        await self.forming_a_list_of_groups(client, list_view, page)
                        remove_duplicates()  # Чистка дубликатов в базе данных 🧹 (таблица groups_and_channels, колонка id)

                if admin_switch.value:
                    # Если выбрано парсить администраторов, выполняем парсинг администраторов 👤
                    await self.obtaining_administrators(session_files, list_view, page)

                if members_switch.value:
                    # Обрабатываем все файлы сессий по очереди 📂
                    for session_path in session_files:
                        session_name = os.path.basename(session_path)
                        client = await self.tg_connect.get_telegram_client(page, session_name,
                                                                           account_directory=path_accounts_folder,
                                                                           list_view=list_view)
                        for groups in await self.db_handler.open_and_read_data(table_name="writing_group_links",
                                                                               list_view=list_view, page=page):
                            await log_and_display(f"🔍 Парсинг группы: {groups[0]}", list_view, page)
                            # подписываемся на группу
                            await self.tg_subscription_manager.subscribe_to_group_or_channel(client, groups[0],
                                                                                             list_view, page)
                            await self.parse_group(client, groups[0], list_view, page)  # выполняем парсинг группы
                            # Удаляем группу из списка после завершения парсинга 🗑️
                            await self.db_handler.delete_row_db(table="writing_group_links",
                                                                column="writing_group_links", value=groups)
                            # Очищаем список и удаляем дубликаты после завершения обработки всех групп
                            await self.clean_parsing_list_and_remove_duplicates(list_view, page)
                            # Завершаем работу клиента после завершения парсинга 🔌
                        await client.disconnect()
                        await log_and_display(f"🔌 Отключение от аккаунта: {session_name}", list_view, page)
            except Exception as error:
                logger.exception(f"❌ Ошибка: {error}")
            finish = datetime.datetime.now()  # фиксируем время окончания парсинга ⏰
            await log_and_display(
                f"🔚 Конец парсинга.\n🕒 Время окончания: {finish}.\n⏳ Время работы: {finish - start_time}",
                list_view, page)

        async def btn_click(e: ft.FilePickerResultEvent) -> None:
            """Обработка выбора файлов"""
            if e.files:
                selected_sessions.clear()  # Очищаем список перед добавлением новых файлов
                for file in e.files:
                    file_name = file.name  # Имя файла
                    file_path = file.path  # Путь к файлу

                    # Проверка расширения файла на ".session"
                    if file_name.endswith(".session"):
                        target_folder = path_accounts_folder
                        target_path = os.path.join(target_folder, file_name)

                        # Проверяем, существует ли файл уже в целевой папке
                        if not os.path.exists(target_path) or file_path != os.path.abspath(target_path):
                            # Создаем директорию, если она не существует
                            os.makedirs(target_folder, exist_ok=True)
                            # Копируем файл только если он отличается
                            shutil.copy(file_path, target_path)
                        selected_sessions.append(target_path)  # Добавляем целевой путь
                    else:
                        selected_files.value = f"Файл {file_name} не является session файлом. Выберите только .session файлы."
                        selected_files.update()
                        return

                selected_files.value = f"Выбраны session файлы: {', '.join([os.path.basename(s) for s in selected_sessions])}"
                selected_files.update()
            else:
                selected_files.value = "Выбор файлов отменен"
                selected_files.update()

            page.update()

        pick_files_dialog = ft.FilePicker(on_result=btn_click)  # Инициализация выбора файлов
        page.overlay.append(pick_files_dialog)  # Добавляем FilePicker на страницу
        # Кнопка для открытия диалога выбора файлов
        button_select_file = ft.ElevatedButton(width=line_width_button, height=BUTTON_HEIGHT,
                                               text="Выбрать session файл(ы)",
                                               on_click=lambda _: pick_files_dialog.pick_files(allow_multiple=True)
                                               # Разрешаем выбор нескольких файлов
                                               )

        # Добавляем кнопки и другие элементы управления на страницу
        page.views.append(
            ft.View(
                "/parsing",
                [
                    list_view,  # отображение логов 📝
                    ft.Column([admin_switch, account_groups_switch, members_switch]),
                    # переключатели в столбце для корректного отображения
                    ft.Column(),  # резерв для приветствия или других элементов интерфейса
                    selected_files,  # Отображение выбранных файлов
                    button_select_file,  # Кнопка для выбора файлов
                    ft.ElevatedButton(width=line_width_button, height=BUTTON_HEIGHT,
                                      text=translations["ru"]["buttons"]["start"],
                                      on_click=add_items),  # Кнопка "🚀 Начать парсинг"
                    ft.ElevatedButton(width=line_width_button, height=BUTTON_HEIGHT,
                                      text=translations["ru"]["buttons"]["back"],
                                      on_click=lambda _: self.back_button_clicked(page))  # Кнопка "⬅️ Назад"
                ],
            )
        )
        page.update()  # обновляем страницу после добавления элементов управления 🔄

    async def parse_group(self, client, groups_wr, list_view, page) -> None:
        """
        Эта функция выполняет парсинг групп, на которые пользователь подписался. Аргумент phone используется декоратором
        @handle_exceptions для отлавливания ошибок и записи их в базу данных user_data/software_database.db.

        :param client: Клиент Telegram
        :param groups_wr: ссылка на группу
        :param list_view: ListView
        :param page: Страница интерфейса Flet для отображения элементов управления.
        """
        try:
            # Записываем parsing данные в файл user_data/software_database.db
            entities: list = await self.get_all_participants(await self.parse_users(client, groups_wr, list_view, page),
                                                             list_view,
                                                             page)
            await log_and_display(f"{entities}", list_view, page)
            await self.db_handler.write_parsed_chat_participants_to_db(entities)
        except Exception as error:
            logger.exception(f"❌ Ошибка: {error}")

    async def parse_active_users(self, chat_input, limit_active_user, page, list_view) -> None:
        """
        Parsing участников, которые пишут в чат (активных участников)

        :param chat_input: Ссылка на чат
        :param limit_active_user: лимит активных участников
        :param page: Страница интерфейса Flet для отображения элементов управления.
        :param list_view: ListView
        """
        try:
            for session_name in await find_filess(directory_path=path_accounts_folder, extension='session'):
                client = await self.tg_connect.get_telegram_client(page, session_name,
                                                                   account_directory=path_accounts_folder,
                                                                   list_view=list_view)
                await self.tg_subscription_manager.subscribe_to_group_or_channel(client, chat_input, list_view, page)

                try:
                    # Преобразуем значение time_activity_user_2 в целое число (если оно None, используем 5 по умолчанию).
                    await asyncio.sleep(
                        int(time_activity_user_2 or 5))  # По умолчанию 5, если None или некорректный тип
                except TypeError:
                    # Если произошла ошибка преобразования (например, time_activity_user_2 имеет неподдерживаемый тип),
                    # то делаем паузу по умолчанию в 5 секунд.
                    await asyncio.sleep(5)  # По умолчанию 5, если None или неправильный тип

                await self.get_active_users(client, chat_input, limit_active_user, list_view, page)
                await client.disconnect()  # Разрываем соединение telegram
            await self.clean_parsing_list_and_remove_duplicates(list_view, page)
        except Exception as error:
            logger.exception(f"❌ Ошибка: {error}")

    async def get_active_users(self, client, chat, limit_active_user, list_view, page) -> None:
        """
        Получаем данные участников группы которые писали сообщения.

        :param client: Клиент Telegram
        :param chat: ссылка на чат
        :param limit_active_user: лимит активных участников
        :param list_view: ListView
        :param page: Страница интерфейса Flet для отображения элементов управления.
        """
        try:
            async for message in client.iter_messages(chat, limit=int(limit_active_user)):
                if message.from_id is not None:
                    try:
                        await log_and_display(f"{message.from_id}", list_view, page)
                        # Получаем входную сущность пользователя
                        user = await client.get_entity(message.from_id.user_id)  # Получаем полную сущность
                        from_user = InputUser(user_id=user.id, access_hash=user.access_hash)  # Создаем InputUser
                        await log_and_display(f"{from_user}", list_view, page)
                        # Получаем данные о пользователе
                        entities = await self.get_active_user_data(user)
                        await log_and_display(f"{entities}", list_view, page)
                        await self.db_handler.write_parsed_chat_participants_to_db_active(entities)
                    except ValueError as e:
                        await log_and_display(
                            f"❌ Не удалось найти сущность для пользователя {message.from_id.user_id}: {e}", list_view,
                            page)
                else:
                    await log_and_display(f"Сообщение {message.id} не имеет действительного from_id.", list_view, page)
        except Exception as error:
            logger.exception(f"❌ Ошибка: {error}")

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

    async def choose_and_parse_group(self, page: ft.Page, list_view) -> None:
        """
        📌 Выбираем группу из подписанных и запускаем парсинг

        :param page: Страница интерфейса Flet для отображения элементов управления.
        :param list_view: ListView
        :return: None
        """
        list_view = ft.ListView(expand=10, spacing=1, padding=2, auto_scroll=True)
        page.controls.append(list_view)
        try:
            for session_name in await find_filess(directory_path=path_accounts_folder, extension='session'):
                client = await self.tg_connect.get_telegram_client(page, session_name,
                                                                   account_directory=path_accounts_folder,
                                                                   list_view=list_view)
                chats = []
                last_date = None
                result = await client(
                    GetDialogsRequest(offset_date=last_date, offset_id=0, offset_peer=InputPeerEmpty(), limit=200,
                                      hash=0))
                chats.extend(result.chats)
                groups = await self.filtering_groups(chats)  # Получаем отфильтрованные группы
                group_titles = await self.name_of_the_groups(groups)  # Получаем названия групп
                await log_and_display(f"{group_titles}", list_view, page)
                # Создаем текст для отображения результата
                result_text = ft.Text(value="📂 Выберите группу для парсинга")

                # Обработчик нажатия кнопки выбора группы
                async def handle_button_click(_) -> None:
                    start = datetime.datetime.now()  # фиксируем время начала выполнения кода
                    await log_and_display(f"▶️ Начало парсинга.\n🕒 Время старта: {str(start)}", list_view, page)
                    await log_and_display(f"📂 Выбрана группа: {dropdown.value}", list_view, page)
                    await self.parse_group(client, dropdown.value, list_view,
                                           page)  # Запускаем парсинг выбранной группы
                    await self.clean_parsing_list_and_remove_duplicates(list_view, page)
                    await client.disconnect()
                    # Переходим на экран парсинга только после завершения всех действий
                    finish = datetime.datetime.now()  # фиксируем время окончания парсинга
                    await log_and_display(
                        f"🔚 Конец парсинга.\n🕒 Время окончания: {finish}.\n⏳ Время работы: {finish - start}", list_view,
                        page)
                    page.go("/parsing")

                # Создаем выпадающий список с названиями групп
                dropdown = ft.Dropdown(width=line_width_button,
                                       options=[ft.DropdownOption(title) for title in group_titles], autofocus=True)
                page.views.append(
                    ft.View(
                        "/parsing",
                        [
                            ft.Column(controls=[
                                dropdown,
                                ft.ElevatedButton(width=line_width_button, height=BUTTON_HEIGHT,
                                                  text="📂 Выбрать группу",
                                                  on_click=handle_button_click),  # Кнопка "Выбрать группу" 📂
                                ft.ElevatedButton(width=line_width_button, height=BUTTON_HEIGHT,
                                                  text=translations["ru"]["buttons"]["back"],
                                                  on_click=lambda _: self.back_button_clicked(page)),
                                # Кнопка "⬅️ Назад"
                                result_text, list_view,
                            ])
                        ],
                    )  # Добавляем созданный вид на страницу
                )
                page.update()
        except Exception as error:
            logger.exception(f"❌ Ошибка: {error}")

    @staticmethod
    async def parse_users(client, target_group, list_view, page: ft.Page):
        """
        🧑‍🤝‍🧑 Парсинг и сбор данных пользователей группы или канала.
        Метод осуществляет поиск участников в указанной группе или канале, собирает их данные и сохраняет в файле.

        :param client: Клиент Telegram.
        :param target_group: Группа или канал, участники которого будут собраны.
        :param list_view: Элемент управления ListView для отображения данных.
        :param page: Страница интерфейса Flet для отображения элементов управления.
        :return: Список участников.
        """
        try:
            await log_and_display("🔍 Ищем участников... 💾 Сохраняем в файл software_database.db...", list_view, page)

            all_participants: list = []
            while_condition = True
            my_filter = ChannelParticipantsSearch("")
            offset = 0
            while while_condition:
                try:
                    participants = await client(
                        GetParticipantsRequest(channel=target_group, offset=offset, filter=my_filter, limit=200,
                                               hash=0))
                    all_participants.extend(participants.users)
                    offset += len(participants.users)
                    if len(participants.users) < 1:
                        while_condition = False
                except TypeError:
                    await log_and_display(f"❌ Ошибка: {target_group} не является группой / каналом.", list_view, page,
                                          level="error")
                    await asyncio.sleep(2)
                    break
                except ChatAdminRequiredError:
                    await log_and_display(f"❌ Ошибка: не хватает прав администратора {target_group}", list_view, page,
                                          level="error")
                    await asyncio.sleep(2)
                    break
                except ChannelPrivateError:
                    await log_and_display(
                        f"❌ Ошибка: канал / закрыт {target_group} или аккаунт забанен на канале или группе. Замените аккаунт",
                        list_view, page, level="error")
                    await asyncio.sleep(2)
                    break
                except AuthKeyUnregisteredError:
                    await log_and_display(f"❌ Ошибка: неверный ключ авторизации аккаунта, выполните проверку аккаунтов",
                                          list_view, page, level="error")
                    await asyncio.sleep(2)
                    break

            return all_participants
        except Exception as error:
            logger.exception(f"❌ Ошибка: {error}")
            raise

    async def get_all_participants(self, all_participants, list_view, page: ft.Page) -> list:
        """
        Сбор данных всех участников.
        Метод проходит по списку участников, получает их данные и сохраняет их в список сущностей.

        :param all_participants: Список объектов участников.
        :param list_view: Элемент управления ListView для отображения данных.
        :param page: Страница интерфейса Flet для отображения элементов управления.
        :return: Список собранных данных участников.
        """
        try:
            entities: list = []  # Создаем пустой список для хранения данных участников
            for user in all_participants:
                await self.get_user_data(user, entities, list_view, page)
            return entities  # Возвращаем словарь пользователей
        except TypeError as error:
            logger.exception(f"❌ Ошибка: {error}")
            return []  # Возвращаем пустой список в случае ошибки
        except Exception as error:
            logger.exception(f"❌ Ошибка: {error}")
            return []  # Возвращаем пустой список в случае ошибки

    async def get_user_data(self, user, entities, list_view: ft.ListView, page: ft.Page) -> None:
        """
        Получение и сохранение данных пользователя.
        Метод получает данные пользователя, добавляет их в список сущностей и отображает на странице.

        :param user: Объект пользователя.
        :param entities: Список сущностей для хранения данных пользователя.
        :param list_view: Элемент управления ListView для отображения данных.
        :param page: Страница интерфейса Flet для отображения элементов управления.
        """
        try:
            # Получение данных пользователя
            username, user_phone, first_name, last_name, photos_id, online_at, user_premium = await self.receiving_data(
                user)
            # Добавление данных в список сущностей
            entities.append(
                [username, user.id, user.access_hash, first_name, last_name, user_phone, online_at, photos_id,
                 user_premium])
            # Отображение данных на странице
            list_view.controls.append(ft.Text(
                f"{username}, {user.id}, {user.access_hash}, {first_name}, {last_name}, {user_phone}, {online_at}, {photos_id}, {user_premium}"))
            page.update()  # Обновление страницы для каждого элемента данных
        except Exception as error:
            logger.exception(f"❌ Ошибка: {error}")

    async def receiving_data(self, user):
        """
        Получение и обработка данных пользователя.
        Метод извлекает и форматирует различные данные профиля пользователя, такие как имя, номер телефона, статус онлайн,
        наличие фотографии и премиум-аккаунт.

        :param user: Объект пользователя.
        :return: Кортеж со значениями: username, user_phone, first_name, last_name, photos_id, online_at, user_premium.
        """
        usernames = user.username if user.username else ""
        user_phone = user.phone if user.phone else "Номер телефона скрыт"
        first_name = user.first_name if user.first_name else ""
        last_name = user.last_name if user.last_name else ""
        photos_id = ("C фото" if isinstance(user.photo, types.UserProfilePhoto) else "Без фото")
        online_at = await self.get_user_online_status(user)
        user_premium = "Пользователь с premium" if user.premium else ""
        return usernames, user_phone, first_name, last_name, photos_id, online_at, user_premium

    async def get_active_user_data(self, user):
        """
        Получаем данные активного пользователя

        :param user: пользователь
        """
        try:
            username, user_phone, first_name, last_name, photos_id, online_at, user_premium = await self.receiving_data(
                user)
            entity = (
                username, user.id, user.access_hash, first_name, last_name, user_phone, online_at, photos_id,
                user_premium)
            return entity
        except Exception as error:
            logger.exception(f"❌ Ошибка: {error}")
            raise

    @staticmethod
    async def forming_a_list_of_groups(client, list_view: ft.ListView, page: ft.Page) -> None:
        """
        Формирует список групп и каналов.

        Метод собирает информацию о группах и каналах, включая их ID, название, описание, ссылку, количество участников
        и время последнего парсинга. Данные сохраняются в базу данных.

        :param client: Экземпляр клиента Telegram.
        :param list_view: ListView для отображения сообщений.
        :param page: Страница интерфейса Flet для отображения элементов управления.
        """
        try:
            async for dialog in client.iter_dialogs():
                try:
                    entity = await client.get_entity(dialog.id)
                    full_channel_info = await client(functions.channels.GetFullChannelRequest(channel=entity))
                    channel_details = await client.get_entity(full_channel_info.full_chat)
                    # Получение количества участников
                    participants_count = getattr(full_channel_info.full_chat, 'participants_count', 0)
                    # Время синтаксического анализа
                    parsing_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    await log_and_display(
                        f"{dialog.id}, {channel_details.title}, https://t.me/{channel_details.username}, {participants_count}",
                        list_view, page)
                    with db.atomic():  # Атомарная транзакция для записи данных
                        GroupsAndChannels.create(
                            id=dialog.id, title=channel_details.title, about=full_channel_info.full_chat.about,
                            link=f"https://t.me/{channel_details.username}", members_count=participants_count,
                            parsing_time=parsing_time
                        )
                except TypeError:
                    continue  # Записываем ошибку в software_database.db и продолжаем работу
        except Exception as error:
            logger.exception(f"❌ Ошибка: {error}")

    async def entering_data_for_parsing_active(self, page: ft.Page) -> None:
        """
        📝 Создает интерфейс для ввода данных для парсинга активных пользователей.
        Отображает поля для ввода ссылки на чат и количества сообщений, а также кнопки для подтверждения и возврата.

        :param page: Страница интерфейса Flet для отображения элементов управления.
        """
        try:

            list_view = ft.ListView(expand=10, spacing=1, padding=2, auto_scroll=True)
            page.controls.append(list_view)  # добавляем ListView на страницу для отображения логов 📝
            page.update()  # обновляем страницу, чтобы сразу показать ListView 🔄

            # Поле для ввода ссылки на чат
            chat_input = ft.TextField(label="🔗 Введите ссылку на чат, с которого будем собирать активных:",
                                      multiline=False, max_lines=1)
            # Поле для ввода количества сообщений
            limit_active_user = ft.TextField(label="💬 Введите количество сообщений, которые будем парсить:",
                                             multiline=False, max_lines=1)

            async def btn_click(_) -> None:
                """✅ Функция-обработчик для кнопки "Готово"""
                start = datetime.datetime.now()  # фиксируем время начала выполнения кода
                await log_and_display(f"▶️ Начало парсинга.\n🕒 Время старта: {str(start)}", list_view, page)
                await log_and_display(
                    f"🔗 Ссылка на чат: {chat_input.value}. 💬 Количество сообщений: {limit_active_user.value}",
                    list_view, page)
                # Вызов функции для парсинга активных пользователей (функция должна быть реализована)
                await self.parse_active_users(chat_input.value, int(limit_active_user.value), page, list_view)
                # Изменение маршрута на новый (если необходимо)
                finish = datetime.datetime.now()  # фиксируем время окончания парсинга ⏰
                await log_and_display(
                    f"🔚 Конец парсинга.\n🕒 Время окончания: {finish}.\n⏳ Время работы: {finish - start}", list_view,
                    page)
                page.go("/parsing")  # Возвращаемся к основному меню парсинга 🏠
                page.update()  # Обновление страницы для отображения изменений 🔄

            # Добавление представления на страницу
            page.views.append(
                ft.View(
                    "/parsing",  # Маршрут для этого представления
                    [
                        list_view,  # отображение логов 📝
                        chat_input,  # Поле ввода ссылки на чат 🔗
                        limit_active_user,  # Поле ввода количества сообщений 💬
                        ft.Column(),  # Колонка для размещения других элементов (при необходимости)
                        ft.ElevatedButton(width=line_width_button, height=BUTTON_HEIGHT,
                                          text=translations["ru"]["buttons"]["done"],
                                          on_click=btn_click),  # Кнопка "✅ Готово"
                        ft.ElevatedButton(width=line_width_button, height=BUTTON_HEIGHT,
                                          text=translations["ru"]["buttons"]["back"],
                                          on_click=lambda _: self.back_button_clicked(page))  # Кнопка "⬅️ Назад"
                    ]
                ))
        except Exception as error:
            logger.exception(f"❌ Ошибка: {error}")
# 690
