import datetime
import random
import time

from loguru import logger
from rich import print
from rich.progress import track
from telethon.errors import *

from system.account_actions.subscription.subscription import subscribe_to_the_group_and_send_the_link
from system.auxiliary_functions.auxiliary_functions import record_and_interrupt, read_json_file
from system.auxiliary_functions.global_variables import console, time_sending_messages_1, time_sending_messages_2
from system.error.telegram_errors import record_account_actions
from system.menu.app_gui import program_window, done_button
from system.notification.notification import app_notifications
from system.telegram_actions.telegram_actions import telegram_connect_and_output_name

creating_a_table = """SELECT * from writing_group_links"""
writing_data_to_a_table = """DELETE from writing_group_links where writing_group_links = ?"""
event: str = "Рассылаем сообщение по чатам Telegram"


def connecting_tg_account_creating_list_groups(db_handler):
    """Подключение к аккаунту телеграмм и формирование списка групп"""
    app_notifications(notification_text=event)  # Выводим уведомление
    # Открываем базу данных для работы с аккаунтами user_settings/software_database.db
    records: list = db_handler.open_and_read_data("config")  # Открываем базу данных
    print(f"[medium_purple3]Всего accounts: {len(records)}")
    for row in records:
        # Подключение к Telegram и вывод имя аккаунта в консоль / терминал
        client, phone = telegram_connect_and_output_name(row, db_handler)
        records: list = db_handler.open_and_read_data("writing_group_links")  # Открываем базу данных
        print(f"[medium_purple3]Всего групп: {len(records)}")

    return client, phone, records


def sending_files_via_chats(db_handler) -> None:
    """Рассылка файлов по чатам"""
    # Спрашиваем у пользователя, через какое время будем отправлять сообщения
    link_to_the_file: str = console.input(
        "[medium_purple3][+] Введите название файла с папки user_settings/files_to_send: ")
    message_text_time: str = console.input(
        "[medium_purple3][+] Введите время, через какое время будем отправлять файлы: ")
    client, phone, records = connecting_tg_account_creating_list_groups(db_handler)
    for groups in records:  # Поочередно выводим записанные группы
        groups_wr = subscribe_to_the_group_and_send_the_link(client, groups, phone, db_handler)
        description_action = f"Sending messages to a group: {groups_wr}"
        try:
            client.send_file(groups_wr, f"user_settings/files_to_send/{link_to_the_file}")  # Рассылаем файлов по чатам
            # Работу записываем в лог файл, для удобства слежения, за изменениями
            time.sleep(int(message_text_time))
            record_account_actions(phone, description_action, event, f"[medium_purple3]Сообщение в группу {groups_wr} написано!", db_handler)
        except ChannelPrivateError:
            record_account_actions(phone, description_action, event, "Указанный канал является приватным, или вам запретили подписываться.", db_handler)
            db_handler.write_data_to_db(creating_a_table, writing_data_to_a_table, groups_wr)
        except PeerFloodError:
            record_and_interrupt("Предупреждение о Flood от Telegram.", phone, description_action, event, db_handler)
            break  # Прерываем работу и меняем аккаунт
        except FloodWaitError as e:
            record_account_actions(phone, description_action, event, f'Flood! wait for {str(datetime.timedelta(seconds=e.seconds))}', db_handler)
            logger.error(f'Спим {e.seconds} секунд')
            time.sleep(e.seconds)
        except UserBannedInChannelError:
            record_and_interrupt("Вам запрещено отправлять сообщения в супергруппу.", phone, description_action, event, db_handler)
            break  # Прерываем работу и меняем аккаунт
        except ChatWriteForbiddenError:
            record_and_interrupt("Вам запрещено писать в супергруппу / канал.", phone, description_action, event, db_handler)
            break  # Прерываем работу и меняем аккаунт
        except (TypeError, UnboundLocalError):
            continue  # Записываем ошибку в software_database.db и продолжаем работу
        client.disconnect()  # Разрываем соединение Telegram


def sending_messages_files_via_chats() -> None:
    """Рассылка сообщений + файлов по чатам"""
    root, text = program_window()

    def output_values_from_the_input_field(db_handler) -> None:
        """Выводим значения с поля ввода (то что ввел пользователь)"""
        message_text = text.get("1.0", 'end-1c')
        closing_the_input_field()
        print("[medium_purple3][+] Введите текс сообщения которое будем отправлять в чаты: ")
        link_to_the_file: str = console.input(
            "[medium_purple3][+] Введите название файла с папки user_settings/files_to_send: ")
        # Спрашиваем у пользователя, через какое время будем отправлять сообщения
        message_text_time: str = console.input(
            "[medium_purple3][+] Введите время, через какое время будем отправлять сообщения: ")
        client, phone, records = connecting_tg_account_creating_list_groups(db_handler)
        for groups in records:  # Поочередно выводим записанные группы
            groups_wr = subscribe_to_the_group_and_send_the_link(client, groups, phone, db_handler)
            try:
                client.send_message(entity=groups_wr, message=message_text)  # Рассылаем сообщение по чатам
                # Рассылаем файлов по чатам
                client.send_file(groups_wr, f"user_settings/files_to_send/{link_to_the_file}")
                # Работу записываем в лог файл, для удобства слежения, за изменениями
                time.sleep(int(message_text_time))
                record_account_actions(phone, f"Sending messages to a group: {groups_wr}",
                                       f"Рассылаем сообщение + файлы по чатам Telegram",
                                       f"[medium_purple3]Сообщение в группу {groups_wr} написано!", db_handler)
            except ChannelPrivateError:
                record_account_actions(phone, f"Sending messages to a group: {groups_wr}",
                                       f"Рассылаем сообщение + файлы по чатам Telegram",
                                       "Указанный канал является приватным, или вам запретили подписываться.", db_handler)
                db_handler.write_data_to_db(creating_a_table, writing_data_to_a_table, groups_wr)
            except PeerFloodError:
                record_and_interrupt("Предупреждение о Flood от Telegram.", phone,
                                     f"Sending messages to a group: {groups_wr}",
                                     f"Рассылаем сообщение + файлы по чатам Telegram", db_handler)
                break  # Прерываем работу и меняем аккаунт
            except FloodWaitError as e:
                record_account_actions(phone, f"Sending messages to a group: {groups_wr}",
                                       f"Рассылаем сообщение + файлы по чатам Telegram",
                                       f'Flood! wait for {str(datetime.timedelta(seconds=e.seconds))}', db_handler)
                logger.error(f'Спим {e.seconds} секунд')
                time.sleep(e.seconds)
            except UserBannedInChannelError:
                record_and_interrupt("Вам запрещено отправлять сообщения в супергруппу.", phone,
                                     f"Sending messages to a group: {groups_wr}",
                                     f"Рассылаем сообщение + файлы по чатам Telegram", db_handler)
                break  # Прерываем работу и меняем аккаунт
            except ChatWriteForbiddenError:
                record_and_interrupt("Вам запрещено писать в супергруппу / канал.", phone,
                                     f"Sending messages to a group: {groups_wr}",
                                     f"Рассылаем сообщение + файлы по чатам Telegram", db_handler)
                break  # Прерываем работу и меняем аккаунт
            except (TypeError, UnboundLocalError):
                continue  # Записываем ошибку в software_database.db и продолжаем работу
        client.disconnect()  # Разрываем соединение Telegram

    def closing_the_input_field() -> None:
        """Закрываем программу"""
        root.destroy()

    done_button(root, output_values_from_the_input_field)  # Кнопка "Готово"
    root.mainloop()  # Запускаем программу


def select_and_read_random_file(entities):
    if entities:  # Проверяем, что список не пустой, если он не пустой
        # Выбираем рандомный файл для чтения
        random_file = random.choice(entities)  # Выбираем случайный файл для чтения из списка файлов
        logger.info(f"Выбран файл для чтения: {random_file[0]}.json")
        data = read_json_file(filename=f"user_settings/message/{random_file[0]}.json")
    return data  # Возвращаем данные из файла


def sending_messages_via_chats_times(entities, db_handler) -> None:
    """Массовая рассылка в чаты"""
    client, phone, records = connecting_tg_account_creating_list_groups(db_handler)
    for groups in records:  # Поочередно выводим записанные группы
        logger.info(f"Группа: {groups}")
        groups_wr = subscribe_to_the_group_and_send_the_link(client, groups, phone, db_handler)
        data = select_and_read_random_file(entities)  # Выбираем случайное сообщение из файла
        try:
            client.send_message(entity=groups_wr, message=data)  # Рассылаем сообщение по чатам
            selected_shift_time = random.randrange(time_sending_messages_1, time_sending_messages_2)
            time_in_seconds = selected_shift_time * 60
            for _ in track(range(time_in_seconds), description=f"[red]Спим {time_in_seconds} минуты / минут..."):
                time.sleep(1)  # Спим 1 секунду
            record_account_actions(phone, f"Sending messages to a group: {groups_wr}", event,
                                   f"[medium_purple3]Сообщение в группу {groups_wr} написано!", db_handler)
        except ChannelPrivateError:
            record_account_actions(phone, f"Sending messages to a group: {groups_wr}", event,
                                   "Указанный канал является приватным, или вам запретили подписываться.", db_handler)
            db_handler.write_data_to_db(creating_a_table, writing_data_to_a_table, groups_wr)
        except PeerFloodError:
            record_and_interrupt("Предупреждение о Flood от Telegram.", phone,
                                 f"Sending messages to a group: {groups_wr}", event, db_handler)
            break  # Прерываем работу и меняем аккаунт
        except FloodWaitError as e:
            record_account_actions(phone, f"Sending messages to a group: {groups_wr}", event,
                                   f'Flood! wait for {str(datetime.timedelta(seconds=e.seconds))}', db_handler)
            logger.error(f'Спим {e.seconds} секунд')
            time.sleep(e.seconds)
        except UserBannedInChannelError:
            record_and_interrupt("Вам запрещено отправлять сообщения в супергруппу.", phone,
                                 f"Sending messages to a group: {groups_wr}", event, db_handler)
            break  # Прерываем работу и меняем аккаунт
        except (TypeError, UnboundLocalError):
            continue  # Записываем ошибку в software_database.db и продолжаем работу
        except ChatWriteForbiddenError:
            record_and_interrupt("Вам запрещено писать в супергруппу / канал.", phone,
                                 f"Sending messages to a group: {groups_wr}", event, db_handler)
            break  # Прерываем работу и меняем аккаунт


if __name__ == "__main__":
    sending_messages_files_via_chats()  # Отправляем сообщения через чаты
