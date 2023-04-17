# -*- coding: utf-8 -*-
from rich import print
from telethon.errors import *
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.tl.types import InputPeerUser
from telethon.tl.functions.channels import LeaveChannelRequest
from system.actions.subscription.subscription import subscribe_to_group_or_channel
from system.auxiliary_functions.auxiliary_functions import we_interrupt_the_code_and_write_the_data_to_the_database, \
    record_inviting_results
from system.auxiliary_functions.global_variables import limits
from system.auxiliary_functions.global_variables import target_group_entity
from system.notification.notification import app_notifications
from system.sqlite_working_tools.sqlite_working_tools import open_the_db_and_read_the_data
from system.sqlite_working_tools.sqlite_working_tools import open_the_db_and_read_the_data_lim
from system.telegram_actions.telegram_actions import connect_to_telegram_account_and_output_name
from system.telegram_actions.telegram_actions import we_get_username_user_id_access_hash

event: str = f"Inviting в группу {target_group_entity}"  # Событие, которое записываем в базу данных


def inviting_to_a_group(client, username, user_id, access_hash) -> None:
    """Inviting в группу"""
    user_to_add = client.get_input_entity(username)
    if username == "":
        user_to_add = InputPeerUser(user_id, access_hash)
    client(InviteToChannelRequest(target_group_entity, [user_to_add]))


def invitation_from_all_accounts_program_body(name_database_table) -> None:
    """Inviting по заранее parsing списку и работа с несколькими аккаунтами"""
    # Выводим уведомление, если операционная система windows 7, то выводим уведомление в консоль
    app_notifications(notification_text=event)
    # Открываем базу данных для работы с аккаунтами setting_user/software_database.db
    records: list = open_the_db_and_read_the_data(name_database_table="config")
    for row in records:
        # Подключение к Telegram и вывод имя аккаунта в консоль / терминал
        client, phone = connect_to_telegram_account_and_output_name(row)
        # Подписываемся на группу которую будем inviting, если аккаунт новый, то он автоматически подпишется и
        # записываем действия в software_database.db
        print(target_group_entity)
        subscribe_to_group_or_channel(client, target_group_entity, phone)
        # records: list = open_the_db_and_read_the_data_lim(name_database_table, number_of_accounts=20)
        records: list = open_the_db_and_read_the_data(name_database_table)
        # Количество аккаунтов на данный момент в работе
        print(f"[bold red]Всего username: {len(records)}")
        inviting(client, phone, records)
    # Выводим уведомление, если операционная система windows 7, то выводим уведомление в консоль
    app_notifications(notification_text=f"Работа с группой {target_group_entity} окончена!")


def unsubscribe_from_the_group(client, target_group_entity):
    """Отписываемся от группы"""
    entity = client.get_entity(target_group_entity)
    if entity:
        client(LeaveChannelRequest(entity))
    client.disconnect()


def invite_from_multiple_accounts_with_limits(name_database_table) -> None:
    """Inviting по заранее parsing списку и работа с несколькими аккаунтами и выставленными лимитами"""
    # Выводим уведомление, если операционная система windows 7, то выводим уведомление в консоль
    app_notifications(notification_text=event)
    # Открываем базу данных для работы с аккаунтами setting_user/software_database.db
    records: list = open_the_db_and_read_the_data(name_database_table="config")
    for row in records:
        # Подключение к Telegram и вывод имя аккаунта в консоль / терминал
        client, phone = connect_to_telegram_account_and_output_name(row)
        # Подписываемся на группу которую будем inviting, если аккаунт новый, то он автоматически подпишется и
        # записываем действия в software_database.db
        subscribe_to_group_or_channel(client, target_group_entity, phone)
        number_usernames: list = open_the_db_and_read_the_data(name_database_table)
        records: list = open_the_db_and_read_the_data_lim(name_database_table, number_of_accounts=limits)
        # Количество аккаунтов на данный момент в работе
        print(f"[bold red]Всего username: {len(number_usernames)}. Лимит на аккаунт: {len(records)}")
        inviting(client, phone, records)
    # Выводим уведомление, если операционная система windows 7, то выводим уведомление в консоль
    app_notifications(notification_text=f"Работа с группой {target_group_entity} окончена!")


def inviting(client, phone, records) -> None:
    """Inviting"""
    for rows in records:
        username, user_id, access_hash, user = we_get_username_user_id_access_hash(rows)
        description_action = f"username : {username}, id: {user_id}, hash: {access_hash}"
        try:
            inviting_to_a_group(client, username, user_id, access_hash)  # Inviting user в группу
        except AuthKeyDuplicatedError:
            actions: str = "Аккаунт запущен еще на одном устройстве!"
            we_interrupt_the_code_and_write_the_data_to_the_database(actions, phone, description_action, event)
            break  # Прерываем работу и меняем аккаунт
        except FloodWaitError as e:
            actions: str = f'Flood! wait for {e.seconds} seconds'
            we_interrupt_the_code_and_write_the_data_to_the_database(actions, phone, description_action, event)
            break  # Прерываем работу и меняем аккаунт
        except PeerFloodError:
            actions: str = "Предупреждение о Flood от telegram."
            we_interrupt_the_code_and_write_the_data_to_the_database(actions, phone, description_action, event)
            break  # Прерываем работу и меняем аккаунт
        except UserPrivacyRestrictedError:
            actions: str = f"Настройки конфиденциальности {username}, id: {user_id} не позволяют вам inviting"
            record_inviting_results(user, phone, description_action, event, actions)
        except UserChannelsTooMuchError:
            actions: str = "Превышен лимит у user каналов / супергрупп."
            record_inviting_results(user, phone, description_action, event, actions)
        except UserBannedInChannelError:
            actions: str = "Вам запрещено отправлять сообщения в супергруппу."
            we_interrupt_the_code_and_write_the_data_to_the_database(actions, phone, description_action, event)
            break  # Прерываем работу и меняем аккаунт
        except ChatWriteForbiddenError:
            actions: str = "Настройки в чате не дают добавлять людей в чат, возможно стоит бот админ и " \
                           "нужно подписаться на другие проекты "
            we_interrupt_the_code_and_write_the_data_to_the_database(actions, phone, description_action, event)
            break  # Прерываем работу и меняем аккаунт
        except BotGroupsBlockedError:
            actions: str = "Вы не можете добавить бота в группу."
            record_inviting_results(user, phone, description_action, event, actions)
        except UserNotMutualContactError:
            actions: str = "User не является взаимным контактом."
            record_inviting_results(user, phone, description_action, event, actions)
        except ChatAdminRequiredError:
            actions: str = "Требуются права администратора."
            record_inviting_results(user, phone, description_action, event, actions)
        except UserKickedError:
            actions: str = "Пользователь был удален ранее из супергруппы."
            record_inviting_results(user, phone, description_action, event, actions)
        except ChannelPrivateError:
            actions: str = "Чат является приватным, или закрыт доступ добавления участников."
            we_interrupt_the_code_and_write_the_data_to_the_database(actions, phone, description_action, event)
            break  # Прерываем работу и меняем аккаунт
        except (UserIdInvalidError, UsernameNotOccupiedError, ValueError, UsernameInvalidError):
            actions: str = f"Не корректное имя {username}, id: {user_id}"
            record_inviting_results(user, phone, description_action, event, actions)
        except (TypeError, UnboundLocalError):
            continue  # Записываем ошибку в software_database.db и продолжаем работу
        except InviteRequestSentError:
            actions: str = "Действия будут доступны после одобрения администратором на вступление в группу"
            we_interrupt_the_code_and_write_the_data_to_the_database(actions, phone, description_action)
            break  # Прерываем работу и меняем аккаунт
        except TypeNotFoundError:
            actions: str = f"Аккаунт {phone} не может добавить в группу {target_group_entity}"
            we_interrupt_the_code_and_write_the_data_to_the_database(actions, phone, description_action, event)
            break  # Прерываем работу и меняем аккаунт
        except KeyboardInterrupt:
            """Закрытие окна программы"""
            client.disconnect()
            print("[!] Скрипт остановлен!")
        else:
            # Записываем данные в базу данных, чистим список кого добавляли или писали сообщение
            actions: str = f"Участник {username}, id: {user_id} добавлен, если не состоит в чате"
            print(f"[green][+] {actions}")
            record_inviting_results(user, phone, description_action, event, actions)
    # Отписываемся от группы, на которую подписались в самом начале
    unsubscribe_from_the_group(client, target_group_entity)
    client.disconnect()  # Разрываем соединение telegram
