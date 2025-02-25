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
                              path_send_message_folder_answering_machine, line_width_button, BUTTON_HEIGHT)
from src.core.localization import done_button, back_button, sending_messages_files_via_chats_ru
from src.core.sqlite_working_tools import db_handler
from src.core.utils import (find_files, all_find_files, record_inviting_results,
                            find_filess)
from src.core.utils import read_json_file
from src.core.utils import record_and_interrupt
from src.features.account.TGConnect import TGConnect
from src.features.account.TGSubUnsub import SubscribeUnsubscribeTelegram
from src.gui.menu import log_and_display_info


class SendTelegramMessages:
    """
    Отправка (текстовых) сообщений в личку Telegram пользователям из базы данных.
    """

    def __init__(self):
        self.tg_connect = TGConnect()
        self.config_reader = ConfigReader()
        self.sub_unsub_tg = SubscribeUnsubscribeTelegram()
        self.time_sending_messages_1, self.time_sending_messages_2 = self.config_reader.get_time_sending_messages()
        self.time_subscription_1, self.time_subscription_2 = self.config_reader.get_time_subscription()
        self.account_extension = "session"  # Расширение файла аккаунта
        self.file_extension = "json"

    async def random_dream(self):
        """
        Рандомный сон
        """
        try:
            time_in_seconds = random.randrange(self.time_sending_messages_1, self.time_sending_messages_2)
            logger.info(f'Спим {time_in_seconds} секунд...')
            await asyncio.sleep(time_in_seconds)  # Спим 1 секунду
        except Exception as error:
            logger.exception(f"❌ Ошибка: {error}")

    @staticmethod
    async def select_and_read_random_file(entities, folder):
        """
        Выбираем рандомный файл для чтения

        :param entities: список файлов для чтения
        :param folder: папка для сохранения файлов
        """
        try:
            if entities:  # Проверяем, что список не пустой, если он не пустой
                # Выбираем рандомный файл для чтения
                random_file = random.choice(entities)  # Выбираем случайный файл для чтения из списка файлов
                logger.info(f"Выбран файл для чтения: {random_file[0]}.json")
                data = read_json_file(filename=f"user_data/{folder}/{random_file[0]}.json")
            return data  # Возвращаем данные из файла
        except Exception as error:
            logger.exception(f"❌ Ошибка: {error}")

    async def send_message_from_all_accounts(self, account_limits, page: ft.Page) -> None:
        """
        Отправка (текстовых) сообщений в личку Telegram пользователям из базы данных.

        :param account_limits: Лимит на аккаунты
        :param page: Страница интерфейса Flet для отображения элементов управления.
        """
        try:
            time_inviting = self.config_reader.get_time_inviting()
            for session_name in find_filess(directory_path=path_send_message_folder, extension=self.account_extension):
                client = await self.tg_connect.get_telegram_client(page, session_name,
                                                                   account_directory=path_send_message_folder)
                try:
                    for username in await db_handler.open_db_func_lim(table_name="members",
                                                                      account_limit=account_limits):
                        # username - имя аккаунта пользователя в базе данных user_data/software_database.db
                        logger.info(f"[!] Отправляем сообщение: {username[0]}")
                        try:
                            entities = find_files(directory_path=path_folder_with_messages,
                                                  extension=self.file_extension)
                            logger.info(entities)
                            data = await self.select_and_read_random_file(entities, folder="message")
                            await client.send_message(await client.get_input_entity(username[0]),
                                                      data.format(username[0]))
                            # Записываем данные в log файл, чистим список кого добавляли или писали сообщение
                            logger.info(f"Отправляем сообщение в личку {username[0]}. Сообщение отправлено пользователю {username[0]}.")
                            await record_inviting_results(time_inviting[0], time_inviting[1], username)
                        except FloodWaitError as e:
                            await record_and_interrupt(time_inviting[0], time_inviting[1])
                            break  # Прерываем работу и меняем аккаунт
                        except PeerFloodError:
                            await record_and_interrupt(time_inviting[0], time_inviting[1])
                            break  # Прерываем работу и меняем аккаунт
                        except UserNotMutualContactError:
                            logger.error(
                                f"❌ Отправляем сообщение в личку {username[0]}. {username[0]} не является взаимным контактом.")
                        except (UserIdInvalidError, UsernameNotOccupiedError, ValueError, UsernameInvalidError):
                            logger.error(
                                f"❌ Отправляем сообщение в личку {username[0]}. Не корректное имя {username[0]}.")
                        except ChatWriteForbiddenError:
                            await record_and_interrupt(time_inviting[0], time_inviting[1])
                            break  # Прерываем работу и меняем аккаунт
                        except (TypeError, UnboundLocalError):
                            continue  # Записываем ошибку в software_database.db и продолжаем работу
                except KeyError:  # В случае отсутствия ключа в базе данных (нет аккаунтов в базе данных).
                    sys.exit(1)

        except Exception as error:
            logger.exception(f"❌ Ошибка: {error}")

    async def send_files_to_personal_chats(self, page: ft.Page) -> None:
        """
        Отправка файлов в личку

        :param page: Страница интерфейса Flet для отображения элементов управления.
        """

        output = ft.Text("Отправка сообщений в личку", size=18, weight=ft.FontWeight.BOLD)

        # Обработчик кнопки "Готово"
        async def button_clicked(_):
            time_from = tb_time_from.value or self.time_sending_messages_1  # Получаем значение первого поля
            time_to = tb_time_to.value or self.time_sending_messages_2  # Получаем значение второго поля

            # Получаем значение третьего поля и разделяем его на список по пробелам
            account_limits_input = account_limits_inputs.value  # Удаляем лишние пробелы
            if account_limits_input:  # Если поле не пустое
                account_limits = account_limits_input  # Разделяем строку по пробелам
                logger.info(account_limits)
            else:
                account_limits=ConfigReader().get_limits()
            if time_from < time_to:
                try:
                    # Просим пользователя ввести расширение сообщения
                    for session_name in find_filess(directory_path=path_send_message_folder,
                                                    extension=self.account_extension):
                        client = await self.tg_connect.get_telegram_client(page, session_name,
                                                                           account_directory=path_send_message_folder)
                        try:
                            # Открываем parsing список user_data/software_database.db для inviting в группу
                            number_usernames: list = await db_handler.open_db_func_lim(table_name="members",
                                                                                       account_limit=int(account_limits))
                            # Количество аккаунтов на данный момент в работе
                            logger.info(f"Всего username: {len(number_usernames)}")
                            for rows in number_usernames:
                                username = rows[0]  # Получаем имя аккаунта из базы данных user_data/software_database.db
                                logger.info(f"[!] Отправляем сообщение: {username}")
                                try:
                                    user_to_add = await client.get_input_entity(username)
                                    text = "Тест сообщение"
                                    for files in all_find_files(directory_path="user_data/files_to_send"):
                                        await client.send_file(entity=user_to_add, caption=text,
                                                               file=f"user_data/files_to_send/{files}")
                                        logger.info(f"Отправляем сообщение в личку {username}. Файл {files} отправлен пользователю {username}.")
                                    await record_inviting_results(time_from, time_to, rows)

                                except FloodWaitError as e:
                                    await record_and_interrupt(time_from, time_to)
                                    break  # Прерываем работу и меняем аккаунт
                                except PeerFloodError:
                                    await record_and_interrupt(time_from, time_to)
                                    break  # Прерываем работу и меняем аккаунт
                                except UserNotMutualContactError:
                                    logger.error(f"❌ Отправляем сообщение в личку {username}. {username} не является взаимным контактом.")
                                except (UserIdInvalidError, UsernameNotOccupiedError, ValueError, UsernameInvalidError):
                                    logger.error(f"❌ Отправляем сообщение в личку {username}. Не корректное имя {username}.")
                                except ChatWriteForbiddenError:
                                    await record_and_interrupt(time_from, time_to)
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
        # Группа полей ввода для времени сна
        tb_time_from = ft.TextField(label="Время сна от", width=297, hint_text="Введите время", border_radius=5, )
        tb_time_to = ft.TextField(label="Время сна до", width=297, hint_text="Введите время", border_radius=5, )
        sleep_time_group = ft.Row(controls=[tb_time_from, tb_time_to], spacing=20, )
        # Поле для формирования списка чатов
        account_limits_inputs = ft.TextField(label="Введите лимит на сообщения", multiline=True, max_lines=12)
        # Кнопка "Готово"
        button_done = ft.ElevatedButton(text=done_button, width=line_width_button, height=BUTTON_HEIGHT,
                                        on_click=button_clicked, )
        # Кнопка "Назад"
        button_back = ft.ElevatedButton(text=back_button, width=line_width_button, height=BUTTON_HEIGHT,
                                        on_click=lambda _: page.go("/sending_messages_via_chats_menu"))
        t = ft.Text()
        # Разделение интерфейса на верхнюю и нижнюю части
        page.views.append(
            ft.View(
                "/sending_messages_via_chats_menu",
                controls=[output, sleep_time_group, t, account_limits_inputs,
                          ft.Column(  # Верхняя часть: контрольные элементы
                              controls=[button_done, button_back, ],
                          ), ], ))

    # Рассылка сообщений по чатам

    async def performing_the_operation(self, page: ft.Page, checs, chat_list_fields) -> None:
        """Пишет в группы"""
        # Создаем ListView для отображения логов
        page.views.clear()
        page.update()
        lv = ft.ListView(expand=10, spacing=1, padding=2, auto_scroll=True)
        page.controls.append(lv)  # добавляем ListView на страницу для отображения логов 📝
        # Кнопка "Назад"
        button_back = ft.ElevatedButton(text=back_button, width=line_width_button, height=BUTTON_HEIGHT,
                                        on_click=lambda _: page.go("/sending_messages_via_chats_menu"))

        # Создание View с элементами
        page.views.append(
            ft.View(
                "/sending_messages_via_chats_menu",
                controls=[
                    lv,  # отображение логов 📝
                    ft.Column(
                        controls=[button_back]
                    )
                ]
            )
        )

        if checs == True:
            try:
                for session_name in find_filess(directory_path=path_send_message_folder_answering_machine,
                                                extension=self.account_extension):
                    client = await self.tg_connect.get_telegram_client(page, session_name,
                                                                       account_directory=path_send_message_folder_answering_machine)

                    @client.on(events.NewMessage(incoming=True))  # Обработчик личных сообщений
                    async def handle_private_messages(event):
                        """Обрабатывает входящие личные сообщения"""
                        if event.is_private:  # Проверяем, является ли сообщение личным
                            logger.info(f'Входящее сообщение: {event.message.message}')
                            entities = find_files(
                                directory_path=path_send_message_folder_answering_machine_message,
                                extension=self.file_extension)
                            logger.info(entities)
                            data = await self.select_and_read_random_file(entities, folder="answering_machine")
                            logger.info(data)
                            await event.respond(f'{data}')  # Отвечаем на входящее сообщение

                    # Получаем список чатов, которым нужно отправить сообщение
                    await log_and_display_info(f"Всего групп: {len(chat_list_fields)}", lv, page)
                    page.update()
                    for group_link in chat_list_fields:
                        try:
                            await self.sub_unsub_tg.subscribe_to_group_or_channel(client, group_link)
                            # Находит все файлы в папке с сообщениями и папке с файлами для отправки.
                            messages, files = await self.all_find_and_all_files()
                            # Отправляем сообщения и файлы в группу
                            await self.send_content_to_group(client, group_link, messages, files, lv, page)
                        except UserBannedInChannelError:
                            logger.error(
                                'Вам запрещено отправлять сообщения в супергруппах/каналах (вызвано запросом SendMessageRequest)')
                        except ValueError:
                            logger.error(f"❌ Ошибка рассылки, проверьте ссылку  на группу: {group_link}")
                            break
                        await self.random_dream()  # Прерываем работу и меняем аккаунт
                    await client.run_until_disconnected()  # Запускаем программу и ждем отключения клиента
            except Exception as error:
                logger.exception(f"❌ Ошибка: {error}")
        else:
            try:
                start = await self.start_time(lv, page)
                for session_name in find_filess(directory_path=path_send_message_folder,
                                                extension=self.account_extension):
                    client = await self.tg_connect.get_telegram_client(page, session_name,
                                                                       account_directory=path_send_message_folder)
                    # Открываем базу данных с группами, в которые будут рассылаться сообщения
                    await log_and_display_info(f"Всего групп: {len(chat_list_fields)}", lv, page)
                    for group_link in chat_list_fields:  # Поочередно выводим записанные группы
                        try:
                            await self.sub_unsub_tg.subscribe_to_group_or_channel(client, group_link)
                            # Находит все файлы в папке с сообщениями и папке с файлами для отправки.
                            messages, files = await self.all_find_and_all_files()
                            # Отправляем сообщения и файлы в группу
                            await self.send_content_to_group(client, group_link, messages, files, lv, page)
                        except ChannelPrivateError:
                            logger.warning(f"Группа {group_link} приватная или подписка запрещена.")
                        except PeerFloodError:
                            await record_and_interrupt(self.time_subscription_1, self.time_subscription_2)
                            break  # Прерываем работу и меняем аккаунт
                        except FloodWaitError as e:
                            logger.warning(f"FloodWait! Ожидание {str(datetime.timedelta(seconds=e.seconds))}")
                            await asyncio.sleep(e.seconds)
                        except UserBannedInChannelError:
                            await record_and_interrupt(self.time_subscription_1, self.time_subscription_2)
                            break  # Прерываем работу и меняем аккаунт
                        except ChatAdminRequiredError:
                            logger.warning(f"Нужны права администратора для отправки сообщений в {group_link}")
                            break
                        except ChatWriteForbiddenError:
                            await record_and_interrupt(self.time_subscription_1, self.time_subscription_2)
                            break  # Прерываем работу и меняем аккаунт
                        except SlowModeWaitError as e:
                            logger.warning(
                                f"Рассылка сообщений в группу: {group_link}. SlowModeWait! wait for {str(datetime.timedelta(seconds=e.seconds))}")
                            await asyncio.sleep(e.seconds)
                        except ValueError:
                            logger.warning(f"❌ Ошибка рассылки, проверьте ссылку  на группу: {group_link}")
                            break
                        except (TypeError, UnboundLocalError):
                            continue  # Записываем ошибку в software_database.db и продолжаем работу
                        except Exception as error:
                            logger.exception(f"❌ Ошибка: {error}")
                    await client.disconnect()  # Разрываем соединение Telegram
                await log_and_display_info("🔚 Конец отправки сообщений + файлов по чатам", lv, page)
                await self.end_time(start, lv, page)
            except Exception as error:
                logger.exception(f"❌ Ошибка: {error}")

    async def sending_messages_files_via_chats(self, page: ft.Page) -> None:
        """
        Рассылка сообщений + файлов по чатам
        """
        output = ft.Text(sending_messages_files_via_chats_ru, size=18, weight=ft.FontWeight.BOLD)

        # Обработчик кнопки "Готово"
        async def button_clicked(e):
            time_from = tb_time_from.value or self.time_sending_messages_1  # Получаем значение первого поля
            time_to = tb_time_to.value or self.time_sending_messages_2  # Получаем значение второго поля
            # Получаем значение третьего поля и разделяем его на список по пробелам
            chat_list_input = chat_list_field.value.strip()  # Удаляем лишние пробелы
            if chat_list_input:  # Если поле не пустое
                chat_list_fields = chat_list_input.split()  # Разделяем строку по пробелам
            else:
                # Если поле пустое, используем данные из базы данных
                db_chat_list = await db_handler.open_and_read_data("writing_group_links")
                chat_list_fields = [group[0] for group in db_chat_list]  # Извлекаем только ссылки из кортежей
            checs = c.value  # Получаем значение чекбокса
            if time_from < time_to:
                await self.performing_the_operation(page, checs, chat_list_fields)
            else:
                t.value = f"Время сна: Некорректный диапазон, введите корректные значения"
                t.update()
            page.update()

        # GUI элементы
        # Чекбокс для работы с автоответчиком
        c = ft.Checkbox(label="Работа с автоответчиком")
        # Группа полей ввода для времени сна
        tb_time_from = ft.TextField(label="Время сна от", width=297, hint_text="Введите время", border_radius=5, )
        tb_time_to = ft.TextField(label="Время сна до", width=297, hint_text="Введите время", border_radius=5, )
        sleep_time_group = ft.Row(controls=[tb_time_from, tb_time_to], spacing=20, )
        # Поле для формирования списка чатов
        chat_list_field = ft.TextField(label="Формирование списка чатов", multiline=True, max_lines=12)
        # Кнопка "Готово"
        button_done = ft.ElevatedButton(text=done_button, width=line_width_button, height=BUTTON_HEIGHT,
                                        on_click=button_clicked, )
        # Кнопка "Назад"
        button_back = ft.ElevatedButton(text=back_button, width=line_width_button, height=BUTTON_HEIGHT,
                                        on_click=lambda _: page.go("/sending_messages_via_chats_menu"))
        t = ft.Text()
        # Разделение интерфейса на верхнюю и нижнюю части
        page.views.append(
            ft.View(
                "/sending_messages_via_chats_menu",
                controls=[output, c, sleep_time_group, t, chat_list_field,
                          ft.Column(  # Верхняя часть: контрольные элементы
                              controls=[button_done, button_back, ],
                          ), ], ))

    async def start_time(self, lv, page):
        start = datetime.datetime.now()  # фиксируем и выводим время старта работы кода
        await log_and_display_info('Время старта: ' + str(start), lv, page)
        await log_and_display_info("▶️ Начало отправки сообщений + файлов по чатам", lv, page)
        return start

    async def end_time(self, start, lv, page):
        finish = datetime.datetime.now()  # фиксируем и выводим время окончания работы кода
        await log_and_display_info('Время окончания: ' + str(finish), lv, page)
        await log_and_display_info('Время работы: ' + str(finish - start), lv, page)

    async def send_content_to_group(self, client, group_link, messages, files, lv, page):
        """
        Отправляет сообщения и файлы в группу.
        :param client: Телеграм клиент
        :param group_link: Ссылка на группу
        :param messages: Список сообщений
        :param files: Список файлов
        :param lv: Лог-вью
        :param page: Страница
        """
        await log_and_display_info(f"Отправляем сообщение в группу: {group_link}", lv, page)
        if not messages:
            for file in files:
                await client.send_file(group_link, f"user_data/files_to_send/{file}")
                await log_and_display_info(f"Файл {file} отправлен в {group_link}.", lv, page)
                await self.random_dream()
        else:
            message = await self.select_and_read_random_file(messages, folder="message")
            if not files:
                await client.send_message(entity=group_link, message=message)
            else:
                for file in files:
                    await client.send_file(group_link, f"user_data/files_to_send/{file}", caption=message)
                    await log_and_display_info(f"Сообщение и файл отправлены в {group_link}", lv, page)
                    await self.random_dream()

    async def all_find_and_all_files(self):
        """
        Находит все файлы в папке с сообщениями и папке с файлами для отправки.
        """
        messages = find_files(directory_path=path_folder_with_messages, extension=self.file_extension)
        files = all_find_files(directory_path="user_data/files_to_send")
        return messages, files

# 392
