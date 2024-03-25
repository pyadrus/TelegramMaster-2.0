import datetime

from loguru import logger
from rich import print
from telethon.errors import *

from system.account_actions.subscription.subscription import subscribe_to_group_or_channel
from system.account_actions.unsubscribe.unsubscribe import unsubscribe_from_the_group
from system.auxiliary_functions.auxiliary_functions import clearing_console_showing_banner
from system.auxiliary_functions.auxiliary_functions import record_and_interrupt
from system.auxiliary_functions.auxiliary_functions import record_inviting_results
from system.auxiliary_functions.global_variables import limits
from system.auxiliary_functions.global_variables import link_group
from system.notification.notification import app_notifications
from system.telegram_actions.telegram_actions import telegram_connect_and_output_name

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
    clearing_console_showing_banner()  # Чистим консоль, выводим банер
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
            print(f'Flood! wait for {str(datetime.timedelta(seconds=e.seconds))}')
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
            actions: str = "Аккаунт запущен еще на одном устройстве!"
            record_and_interrupt(actions, phone, f"username : {username}", event, db_handler)
            break  # Прерываем работу и меняем аккаунт
        except FloodWaitError as e:
            actions: str = f'Flood! wait for {str(datetime.timedelta(seconds=e.seconds))}'
            record_and_interrupt(actions, phone, f"username : {username}", event, db_handler)
            break  # Прерываем работу и меняем аккаунт
        except PeerFloodError:
            actions: str = "Предупреждение о Flood от telegram."
            record_and_interrupt(actions, phone, f"username : {username}", event, db_handler)
            break  # Прерываем работу и меняем аккаунт
        except UserPrivacyRestrictedError:
            actions: str = f"Настройки конфиденциальности {username} не позволяют вам inviting"
            record_inviting_results(username, phone, f"username : {username}", event, actions, db_handler)
        except UserChannelsTooMuchError:
            actions: str = "Превышен лимит у user каналов / супергрупп."
            record_inviting_results(username, phone, f"username : {username}", event, actions, db_handler)
        except UserBannedInChannelError:
            actions: str = "Вам запрещено отправлять сообщения в супергруппу."
            record_and_interrupt(actions, phone, f"username : {username}", event, db_handler)
            break  # Прерываем работу и меняем аккаунт
        except ChatWriteForbiddenError:
            actions: str = "Настройки в чате не дают добавлять людей в чат, возможно стоит бот админ и " \
                           "нужно подписаться на другие проекты "
            record_and_interrupt(actions, phone, f"username : {username}", event, db_handler)
            break  # Прерываем работу и меняем аккаунт
        except BotGroupsBlockedError:
            actions: str = "Вы не можете добавить бота в группу."
            record_inviting_results(username, phone, f"username : {username}", event, actions, db_handler)
        except UserNotMutualContactError:
            actions: str = "User не является взаимным контактом."
            record_inviting_results(username, phone, f"username : {username}", event, actions, db_handler)
        except ChatAdminRequiredError:
            actions: str = "Требуются права администратора."
            record_inviting_results(username, phone, f"username : {username}", event, actions, db_handler)
        except UserKickedError:
            actions: str = "Пользователь был удален ранее из супергруппы."
            record_inviting_results(username, phone, f"username : {username}", event, actions, db_handler)
        except ChannelPrivateError:
            actions: str = "Чат является приватным, или закрыт доступ добавления участников."
            record_and_interrupt(actions, phone, f"username : {username}", event, db_handler)
            break  # Прерываем работу и меняем аккаунт
        except (UserIdInvalidError, UsernameNotOccupiedError, ValueError, UsernameInvalidError):
            actions: str = f"Не корректное имя {username}"
            record_inviting_results(username, phone, f"username : {username}", event, actions, db_handler)
        except (TypeError, UnboundLocalError):
            continue  # Записываем ошибку в software_database.db и продолжаем работу
        except InviteRequestSentError:
            actions: str = "Действия будут доступны после одобрения администратором на вступление в группу"
            record_inviting_results(username, phone, f"username : {username}", event, actions, db_handler)
            break  # Прерываем работу и меняем аккаунт
        except TypeNotFoundError:
            actions: str = f"Аккаунт {phone} не может добавить в группу {link_group}"
            record_and_interrupt(actions, phone, f"username : {username}", event, db_handler)
            break  # Прерываем работу и меняем аккаунт
        except KeyboardInterrupt:  # Закрытие окна программы
            client.disconnect()  # Разрываем соединение telegram
            print("[!] Скрипт остановлен!")
        else:
            # Записываем данные в базу данных, чистим список кого добавляли или писали сообщение
            actions: str = f"Участник {username} добавлен, если не состоит в чате"
            print(f"[magenta][+] {actions}")
            record_inviting_results(username, phone, f"username : {username}", event, actions, db_handler)
    unsubscribe_from_the_group(client, link_group)  # Отписываемся от группы, на которую подписались в самом начале
    client.disconnect()  # Разрываем соединение telegram
