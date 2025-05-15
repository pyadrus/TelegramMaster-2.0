# -*- coding: utf-8 -*-
import asyncio
import datetime
import random
import sys

import flet as ft
from loguru import logger
from telethon import events
from telethon.errors import (ChannelPrivateError, PeerFloodError, FloodWaitError, UserBannedInChannelError,
                             ChatWriteForbiddenError, UserNotMutualContactError, UserIdInvalidError,
                             UsernameNotOccupiedError, UsernameInvalidError, ChatAdminRequiredError, SlowModeWaitError)

from src.core.configs import (ConfigReader, path_send_message_folder, path_folder_with_messages,
                              path_send_message_folder_answering_machine_message,
                              path_send_message_folder_answering_machine, line_width_button, BUTTON_HEIGHT,
                              time_sending_messages_1, time_sending_messages_2, time_subscription_1,
                              time_subscription_2)
from src.core.sqlite_working_tools import db_handler
from src.core.utils import find_files, all_find_files, record_inviting_results, find_filess
from src.core.utils import read_json_file
from src.core.utils import record_and_interrupt
from src.features.account.TGConnect import TGConnect
from src.features.account.TGSubUnsub import SubscribeUnsubscribeTelegram
from src.gui.gui import start_time, end_time, list_view, log_and_display
from src.locales.translations_loader import translations


class SendTelegramMessages:
    """
    Отправка (текстовых) сообщений в личку Telegram пользователям из базы данных.
    """

    def __init__(self):
        self.tg_connect = TGConnect()
        self.config_reader = ConfigReader()
        self.sub_unsub_tg = SubscribeUnsubscribeTelegram()
        self.account_extension = "session"  # Расширение файла аккаунта
        self.file_extension = "json"

    async def send_files_to_personal_chats(self, page: ft.Page) -> None:
        """
        Отправка файлов в личку

        :param page: Страница интерфейса Flet для отображения элементов управления.
        """

        output = ft.Text("Отправка сообщений в личку", size=18, weight=ft.FontWeight.BOLD)

        # Обработчик кнопки "Готово"
        async def button_clicked(_):
            time_from = tb_time_from.value or time_sending_messages_1  # Получаем значение первого поля
            time_to = tb_time_to.value or time_sending_messages_2  # Получаем значение второго поля

            # Получаем значение третьего поля и разделяем его на список по пробелам
            account_limits_input = account_limits_inputs.value  # Удаляем лишние пробелы
            if account_limits_input:  # Если поле не пустое
                account_limits = account_limits_input  # Разделяем строку по пробелам
                await log_and_display(f"{account_limits}", page)
            else:
                account_limits = ConfigReader().get_limits()
            if time_from < time_to:
                try:
                    # Просим пользователя ввести расширение сообщения
                    for session_name in await find_filess(directory_path=path_send_message_folder,
                                                          extension=self.account_extension):
                        client = await self.tg_connect.get_telegram_client(page, session_name,
                                                                           account_directory=path_send_message_folder)
                        try:
                            # Открываем parsing список user_data/software_database.db для inviting в группу
                            number_usernames: list = await db_handler.select_records_with_limit(table_name="members",
                                                                                                limit=int(
                                                                                                    account_limits))
                            # Количество аккаунтов на данный момент в работе
                            await log_and_display(f"Всего username: {len(number_usernames)}", page)
                            for rows in number_usernames:
                                username = rows[
                                    0]  # Получаем имя аккаунта из базы данных user_data/software_database.db
                                await log_and_display(f"[!] Отправляем сообщение: {username}", page)
                                try:
                                    user_to_add = await client.get_input_entity(username)
                                    messages, files = await self.all_find_and_all_files(page)
                                    await self.send_content(client, user_to_add, messages, files, page)
                                    await log_and_display(
                                        f"Отправляем сообщение в личку {username}. Файл {files} отправлен пользователю {username}.",
                                        page)
                                    await record_inviting_results(time_from, time_to, rows, page)
                                except FloodWaitError as e:
                                    await log_and_display(
                                        f"{translations["ru"]["notifications_errors"]["flood_wait"]}{e}", page,
                                        level="error")
                                    await record_and_interrupt(time_from, time_to, page)
                                    break  # Прерываем работу и меняем аккаунт
                                except PeerFloodError:
                                    await record_and_interrupt(time_from, time_to, page)
                                    break  # Прерываем работу и меняем аккаунт
                                except UserNotMutualContactError:
                                    await log_and_display(
                                        translations["ru"]["notifications_errors"]["user_not_mutual_contact"], page)
                                except (UserIdInvalidError, UsernameNotOccupiedError, ValueError, UsernameInvalidError):
                                    await log_and_display(
                                        translations["ru"]["notifications_errors"]["invalid_username"], page)
                                except ChatWriteForbiddenError:
                                    await log_and_display(translations["ru"]["notifications_errors"]["chat_write_forbidden"], page)
                                    await record_and_interrupt(time_from, time_to, page)
                                    break  # Прерываем работу и меняем аккаунт
                                except (TypeError, UnboundLocalError):
                                    continue  # Записываем ошибку в software_database.db и продолжаем работу
                        except KeyError:
                            sys.exit(1)
                except Exception as error:
                    logger.exception(f"❌ Ошибка: {error}")
            else:
                t.value = f"Время сна: Некорректный диапазон, введите корректные значения"
                t.update()
            page.update()

        # GUI элементы

        tb_time_from, tb_time_to = await self.sleep_selection_input()
        sleep_time_group = ft.Row(controls=[tb_time_from, tb_time_to], spacing=20, )
        # Поле для формирования списка чатов
        account_limits_inputs = ft.TextField(label="Введите лимит на сообщения", multiline=True, max_lines=12)
        # Кнопка "Готово"
        button_done = ft.ElevatedButton(text=translations["ru"]["buttons"]["done"], width=line_width_button,
                                        height=BUTTON_HEIGHT,
                                        on_click=button_clicked, )
        # Кнопка "Назад"
        button_back = ft.ElevatedButton(text=translations["ru"]["buttons"]["back"], width=line_width_button,
                                        height=BUTTON_HEIGHT,
                                        on_click=lambda _: page.go("/sending_messages_via_chats_menu"))
        t = ft.Text()
        # Разделение интерфейса на верхнюю и нижнюю части
        page.views.append(
            ft.View("/sending_messages_via_chats_menu",
                    controls=[output, sleep_time_group, t, account_limits_inputs,
                              ft.Column(  # Верхняя часть: контрольные элементы
                                  controls=[button_done, button_back, ],
                              ), ], ))

    @staticmethod
    async def sleep_selection_input():
        # Группа полей ввода для времени сна
        tb_time_from = ft.TextField(label="Время сна от", width=297, hint_text="Введите время", border_radius=5, )
        tb_time_to = ft.TextField(label="Время сна до", width=297, hint_text="Введите время", border_radius=5, )
        return tb_time_from, tb_time_to

    async def performing_the_operation(self, page: ft.Page, checs, chat_list_fields) -> None:
        """Рассылка сообщений по чатам
        :param checs: значение чекбокса"""
        # Создаем ListView для отображения логов
        page.views.clear()
        page.update()
        page.controls.append(list_view)  # добавляем ListView на страницу для отображения логов 📝
        # Кнопка "Назад"
        button_back = ft.ElevatedButton(text=translations["ru"]["buttons"]["back"], width=line_width_button,
                                        height=BUTTON_HEIGHT,
                                        on_click=lambda _: page.go("/sending_messages_via_chats_menu"))
        # Создание View с элементами
        page.views.append(
            ft.View(
                "/sending_messages_via_chats_menu",
                controls=[
                    list_view,  # отображение логов 📝
                    ft.Column(
                        controls=[button_back]
                    )]))

        if checs == True:
            try:
                for session_name in await find_filess(directory_path=path_send_message_folder_answering_machine,
                                                      extension=self.account_extension):
                    client = await self.tg_connect.get_telegram_client(page, session_name,
                                                                       account_directory=path_send_message_folder_answering_machine)

                    @client.on(events.NewMessage(incoming=True))  # Обработчик личных сообщений
                    async def handle_private_messages(event):
                        """Обрабатывает входящие личные сообщения"""
                        if event.is_private:  # Проверяем, является ли сообщение личным
                            await log_and_display(f"Входящее сообщение: {event.message.message}", page)
                            entities = find_files(
                                directory_path=path_send_message_folder_answering_machine_message,
                                extension=self.file_extension, page=page)
                            await log_and_display(f"{entities}", page)
                            data = await self.select_and_read_random_file(entities, folder="answering_machine",
                                                                          page=page)
                            await log_and_display(f"{data}", page)
                            await event.respond(f'{data}')  # Отвечаем на входящее сообщение

                    # Получаем список чатов, которым нужно отправить сообщение
                    await log_and_display(f"Всего групп: {len(chat_list_fields)}", page)
                    page.update()
                    for group_link in chat_list_fields:
                        try:
                            await self.sub_unsub_tg.subscribe_to_group_or_channel(client, group_link, page)
                            # Находит все файлы в папке с сообщениями и папке с файлами для отправки.
                            messages, files = await self.all_find_and_all_files(page)
                            # Отправляем сообщения и файлы в группу
                            await self.send_content(client, group_link, messages, files, page)
                        except UserBannedInChannelError:
                            await log_and_display(
                                f"Вам запрещено отправлять сообщения в супергруппах/каналах (вызвано запросом SendMessageRequest)",
                                page)
                        except ValueError:
                            await log_and_display(f"❌ Ошибка рассылки, проверьте ссылку  на группу: {group_link}",
                                                  page)
                            break
                        await self.random_dream(page)  # Прерываем работу и меняем аккаунт
                    await client.run_until_disconnected()  # Запускаем программу и ждем отключения клиента
            except Exception as error:
                logger.exception(f"❌ Ошибка: {error}")
        else:
            try:
                start = await start_time(page)
                for session_name in await find_filess(directory_path=path_send_message_folder,
                                                      extension=self.account_extension):
                    client = await self.tg_connect.get_telegram_client(page, session_name,
                                                                       account_directory=path_send_message_folder)
                    # Открываем базу данных с группами, в которые будут рассылаться сообщения
                    await log_and_display(f"Всего групп: {len(chat_list_fields)}", page)
                    for group_link in chat_list_fields:  # Поочередно выводим записанные группы
                        try:
                            await self.sub_unsub_tg.subscribe_to_group_or_channel(client, group_link, page)
                            # Находит все файлы в папке с сообщениями и папке с файлами для отправки.
                            messages, files = await self.all_find_and_all_files(page)
                            # Отправляем сообщения и файлы в группу
                            await self.send_content(client, group_link, messages, files, page)
                        except ChannelPrivateError:
                            await log_and_display(f"Группа {group_link} приватная или подписка запрещена.", page)
                        except PeerFloodError:
                            await record_and_interrupt(time_subscription_1, time_subscription_2, page)
                            break  # Прерываем работу и меняем аккаунт
                        except FloodWaitError as e:
                            await log_and_display(f"{translations["ru"]["notifications_errors"]["flood_wait"]}{e}",
                                                  page, level="error")
                            await asyncio.sleep(e.seconds)
                        except UserBannedInChannelError:
                            await record_and_interrupt(time_subscription_1, time_subscription_2, page)
                            break  # Прерываем работу и меняем аккаунт
                        except ChatAdminRequiredError:
                            await log_and_display(translations["ru"]["notifications_errors"]["admin_rights_required"], page)
                            break
                        except ChatWriteForbiddenError:
                            await log_and_display(translations["ru"]["notifications_errors"]["chat_write_forbidden"], page)
                            await record_and_interrupt(time_subscription_1, time_subscription_2, page)
                            break  # Прерываем работу и меняем аккаунт
                        except SlowModeWaitError as e:
                            await log_and_display(
                                f"Рассылка сообщений в группу: {group_link}. SlowModeWait! wait for {str(datetime.timedelta(seconds=e.seconds))}",
                                page)
                            await asyncio.sleep(e.seconds)
                        except ValueError:
                            await log_and_display(f"❌ Ошибка рассылки, проверьте ссылку  на группу: {group_link}",
                                                  page)
                            break
                        except (TypeError, UnboundLocalError):
                            continue  # Записываем ошибку в software_database.db и продолжаем работу
                        except Exception as error:
                            logger.exception(f"❌ Ошибка: {error}")
                    await client.disconnect()  # Разрываем соединение Telegram
                await log_and_display("🔚 Конец отправки сообщений + файлов по чатам", page)
                await end_time(start, page)
            except Exception as error:
                logger.exception(f"❌ Ошибка: {error}")

    async def sending_messages_files_via_chats(self, page: ft.Page) -> None:
        """
        Рассылка сообщений + файлов по чатам
        """

        # Обработчик кнопки "Готово"
        async def button_clicked(_):
            # Получаем значение третьего поля и разделяем его на список по пробелам
            chat_list_input = chat_list_field.value.strip()  # Удаляем лишние пробелы
            if chat_list_input:  # Если поле не пустое
                chat_list_fields = chat_list_input.split()  # Разделяем строку по пробелам
            else:
                # Если поле пустое, используем данные из базы данных
                db_chat_list = await db_handler.open_and_read_data(table_name="writing_group_links",
                                                                   page=page)
                chat_list_fields = [group[0] for group in db_chat_list]  # Извлекаем только ссылки из кортежей
            if tb_time_from.value or time_sending_messages_1 < tb_time_to.value or time_sending_messages_2:
                await self.performing_the_operation(page, c.value, chat_list_fields)
            else:
                t.value = f"Время сна: Некорректный диапазон, введите корректные значения"
                t.update()
            page.update()

        # Чекбокс для работы с автоответчиком
        c = ft.Checkbox(label="Работа с автоответчиком")
        tb_time_from, tb_time_to = await self.sleep_selection_input()
        # Поле для формирования списка чатов
        chat_list_field = ft.TextField(label="Формирование списка чатов", multiline=True, max_lines=12)

        t = ft.Text()
        # Разделение интерфейса на верхнюю и нижнюю части
        page.views.append(
            ft.View(
                "/sending_messages_via_chats_menu",
                controls=[
                    ft.Text(translations["ru"]["message_sending_menu"]["sending_messages_files_via_chats"], size=18,
                            weight=ft.FontWeight.BOLD), c, ft.Row(controls=[tb_time_from, tb_time_to], spacing=20, ), t,
                    chat_list_field,
                    ft.Column(  # Верхняя часть: контрольные элементы
                        controls=[ft.ElevatedButton(text=translations["ru"]["buttons"]["done"], width=line_width_button,
                                                    height=BUTTON_HEIGHT,
                                                    on_click=button_clicked, ),
                                  ft.ElevatedButton(text=translations["ru"]["buttons"]["back"], width=line_width_button,
                                                    height=BUTTON_HEIGHT,
                                                    on_click=lambda _: page.go("/sending_messages_via_chats_menu")), ],
                    ), ], ))

    async def send_content(self, client, target, messages, files, page: ft.Page):
        """
        Отправляет сообщения и файлы в личку.
        :param client: Телеграм клиент
        :param target: Ссылка на группу (или личку)
        :param messages: Список сообщений
        :param files: Список файлов
        :param page: Страница
        """
        await log_and_display(f"Отправляем сообщение: {target}", page)
        if not messages:
            for file in files:
                await client.send_file(target, f"user_data/files_to_send/{file}")
                await log_and_display(f"Файл {file} отправлен в {target}.", page)
        else:
            message = await self.select_and_read_random_file(messages, folder="message", page=page)
            if not files:
                await client.send_message(entity=target, message=message)
            else:
                for file in files:
                    await client.send_file(target, f"user_data/files_to_send/{file}", caption=message)
                    await log_and_display(f"Сообщение и файл отправлены: {target}", page)
        await self.random_dream(page)

    async def all_find_and_all_files(self, page: ft.Page):
        """
        Находит все файлы в папке с сообщениями и папке с файлами для отправки.
        """
        messages = find_files(directory_path=path_folder_with_messages, extension=self.file_extension,
                              page=page)
        files = all_find_files(directory_path="user_data/files_to_send")
        return messages, files

    async def random_dream(self, page):
        """
        Рандомный сон
        """
        try:
            time_in_seconds = random.randrange(time_sending_messages_1, time_sending_messages_2)
            await log_and_display(f"Спим {time_in_seconds} секунд...", page)
            await asyncio.sleep(time_in_seconds)  # Спим 1 секунду
        except Exception as error:
            logger.exception(f"❌ Ошибка: {error}")

    @staticmethod
    async def select_and_read_random_file(entities, folder, page: ft.Page):
        """
        Выбираем рандомный файл для чтения

        :param entities: список файлов для чтения
        :param folder: папка для сохранения файлов
        :param page: Страница интерфейса
        """
        try:
            if entities:  # Проверяем, что список не пустой, если он не пустой
                # Выбираем рандомный файл для чтения
                random_file = random.choice(entities)  # Выбираем случайный файл для чтения из списка файлов
                await log_and_display(f"Выбран файл для чтения: {random_file[0]}.json", page)
                data = read_json_file(filename=f"user_data/{folder}/{random_file[0]}.json")
            return data  # Возвращаем данные из файла
        except Exception as error:
            logger.exception(f"❌ Ошибка: {error}")
            return None
