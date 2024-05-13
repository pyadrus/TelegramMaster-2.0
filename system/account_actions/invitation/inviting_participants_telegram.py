import datetime

from loguru import logger
from rich import print
from telethon.errors import *

from system.account_actions.subscription.subscription import subscribe_to_group_or_channel
from system.account_actions.unsubscribe.unsubscribe import unsubscribe_from_the_group
from system.auxiliary_functions.auxiliary_functions import clear_console_and_display_banner
from system.auxiliary_functions.auxiliary_functions import record_and_interrupt
from system.auxiliary_functions.auxiliary_functions import record_inviting_results
from system.auxiliary_functions.global_variables import limits, config_read
# from system.auxiliary_functions.global_variables import link_group
from system.notification.notification import app_notifications
from system.telegram_actions.telegram_actions import telegram_connect_and_output_name

link_group = config_read()
event: str = f"Inviting в группу {link_group}"  # Событие, которое записываем в базу данных


def inviting_to_a_group(client, username) -> None:
    """Inviting в группу"""
    logger.info(username)
    try:
        client(functions.channels.InviteToChannelRequest(channel=link_group, users=[f'{username}']))
    except UserBlockedError as e:
        logger.error(e)


def invitation_from_all_accounts_program_body(name_database_table, db_handler) -> None:
    """Inviting по заранее parsing списку и работа с несколькими аккаунтами"""
    clear_console_and_display_banner()  # Чистим консоль, выводим банер
    app_notifications(notification_text=event)  # Выводим уведомление
    # Открываем базу данных для работы с аккаунтами user_settings/software_database.db
    records: list = db_handler.open_and_read_data("config")
    for row in records:
        # Подключение к Telegram и вывод имя аккаунта в консоль / терминал
        client, phone = telegram_connect_and_output_name(row, db_handler)
        # Подписываемся на группу которую будем inviting, если аккаунт новый, то он автоматически подпишется и
        # записываем действия в software_database.db
        print(link_group)
        subscribe_to_group_or_channel(client, link_group, phone, db_handler)
        records: list = db_handler.open_and_read_data(name_database_table)
        print(f"[medium_purple3]Всего username: {len(records)}")  # Количество аккаунтов на данный момент в работе
        try:
            inviting(client, phone, records, db_handler)
        except FloodWaitError as e:
            logger.error(f'Flood! wait for {str(datetime.timedelta(seconds=e.seconds))}')
            continue  # Прерываем работу и меняем аккаунт
    app_notifications(notification_text=f"Работа с группой {link_group} окончена!")  # Выводим уведомление


def invite_from_multiple_accounts_with_limits(name_database_table, db_handler) -> None:
    """Inviting по заранее parsing списку и работа с несколькими аккаунтами и выставленными лимитами"""
    app_notifications(notification_text=event)  # Выводим уведомление
    # Открываем базу данных для работы с аккаунтами user_settings/software_database.db
    records: list = db_handler.open_and_read_data("config")
    for row in records:
        # Подключение к Telegram и вывод имя аккаунта в консоль / терминал
        client, phone = telegram_connect_and_output_name(row, db_handler)
        # Подписываемся на группу которую будем inviting, если аккаунт новый, то он автоматически подпишется и
        # записываем действия в software_database.db
        subscribe_to_group_or_channel(client, link_group, phone, db_handler)
        number_usernames: list = db_handler.open_and_read_data(name_database_table)
        records: list = db_handler.open_the_db_and_read_the_data_lim(name_database_table, number_of_accounts=limits)
        # Количество аккаунтов на данный момент в работе
        print(f"[medium_purple3]Всего username: {len(number_usernames)}. Лимит на аккаунт: {len(records)}")
        inviting(client, phone, records, db_handler)
    app_notifications(notification_text=f"Работа с группой {link_group} окончена!")  # Выводим уведомление


def inviting(client, phone, records, db_handler) -> None:
    """Inviting"""
    for rows in records:
        username = rows[0]  # Имя аккаунта пользователя в базе данных user_settings/software_database.db
        try:
            inviting_to_a_group(client, username)  # Inviting user в группу
        except AuthKeyDuplicatedError:
            record_and_interrupt("Аккаунт запущен еще на одном устройстве!", phone,
                                 f"username : {username}", event, db_handler)
            break  # Прерываем работу и меняем аккаунт
        except FloodWaitError as e:
            record_and_interrupt(f'Flood! wait for {str(datetime.timedelta(seconds=e.seconds))}',
                                 phone, f"username : {username}", event, db_handler)
            break  # Прерываем работу и меняем аккаунт
        except PeerFloodError:
            record_and_interrupt("Предупреждение о Flood от telegram.", phone,
                                 f"username : {username}", event, db_handler)
            break  # Прерываем работу и меняем аккаунт
        except UserPrivacyRestrictedError:
            record_inviting_results(username, phone, f"username : {username}", event,
                                    f"Настройки конфиденциальности {username} не позволяют вам inviting", db_handler)
        except UserChannelsTooMuchError:
            record_inviting_results(username, phone, f"username : {username}", event,
                                    "Превышен лимит у user каналов / супергрупп.", db_handler)
        except UserBannedInChannelError:
            record_and_interrupt("Вам запрещено отправлять сообщения в супергруппу.", phone,
                                 f"username : {username}", event, db_handler)
            break  # Прерываем работу и меняем аккаунт
        except ChatWriteForbiddenError:
            record_and_interrupt("Настройки в чате не дают добавлять людей в чат, возможно стоит бот админ и нужно подписаться на другие проекты ", phone, f"username : {username}", event, db_handler)
            break  # Прерываем работу и меняем аккаунт
        except BotGroupsBlockedError:
            record_inviting_results(username, phone, f"username : {username}", event,
                                    "Вы не можете добавить бота в группу.", db_handler)
        except UserNotMutualContactError:
            record_inviting_results(username, phone, f"username : {username}", event,
                                    "User не является взаимным контактом.", db_handler)
        except ChatAdminRequiredError:
            record_inviting_results(username, phone, f"username : {username}", event,
                                    "Требуются права администратора.", db_handler)
        except UserKickedError:
            record_inviting_results(username, phone, f"username : {username}", event,
                                    "Пользователь был удален ранее из супергруппы.", db_handler)
        except ChannelPrivateError:
            record_and_interrupt("Чат является приватным, или закрыт доступ добавления участников.",
                                 phone, f"username : {username}", event, db_handler)
            break  # Прерываем работу и меняем аккаунт
        except (UserIdInvalidError, UsernameNotOccupiedError, ValueError, UsernameInvalidError):
            record_inviting_results(username, phone, f"username : {username}", event, f"Не корректное имя {username}", db_handler)
        except (TypeError, UnboundLocalError):
            continue  # Записываем ошибку в software_database.db и продолжаем работу
        except InviteRequestSentError:
            record_inviting_results(username, phone, f"username : {username}", event,
                                    "Действия будут доступны после одобрения администратором на вступление в группу", db_handler)
            break  # Прерываем работу и меняем аккаунт
        except TypeNotFoundError:
            record_and_interrupt(f"Аккаунт {phone} не может добавить в группу {link_group}", phone,
                                 f"username : {username}", event, db_handler)
            break  # Прерываем работу и меняем аккаунт
        except KeyboardInterrupt:  # Закрытие окна программы
            client.disconnect()  # Разрываем соединение telegram
            print("[!] Скрипт остановлен!")
        else:
            # Записываем данные в базу данных, чистим список кого добавляли или писали сообщение
            print(f"[magenta][+] Участник {username} добавлен, если не состоит в чате")
            record_inviting_results(username, phone, f"username : {username}", event,
                                    f"Участник {username} добавлен, если не состоит в чате", db_handler)
    unsubscribe_from_the_group(client, link_group)  # Отписываемся от группы, на которую подписались в самом начале
    client.disconnect()  # Разрываем соединение telegram
