import datetime

from loguru import logger
from telethon.errors import *

from system.account_actions.subscription.subscription import subscribe_to_group_or_channel
from system.account_actions.unsubscribe.unsubscribe import unsubscribe_from_the_group
from system.auxiliary_functions.auxiliary_functions import record_and_interrupt
from system.auxiliary_functions.auxiliary_functions import record_inviting_results
from system.auxiliary_functions.global_variables import ConfigReader

from system.telegram_actions.telegram_actions import telegram_connect_and_output_name

configs_reader = ConfigReader()
link_group = configs_reader.get_link_group()
limits = configs_reader.get_limits()


async def inviting_to_a_group(client, username) -> None:
    """Inviting в группу"""
    logger.info(username)
    try:
        await client(functions.channels.InviteToChannelRequest(channel=link_group, users=username))
    except UserBlockedError as e:
        logger.error(e)


async def invitation_from_all_accounts_program_body(name_database_table, db_handler) -> None:
    """Inviting по заранее parsing списку и работа с несколькими аккаунтами"""
    # Открываем базу данных для работы с аккаунтами user_settings/software_database.db
    records: list = await db_handler.open_and_read_data("config")
    for row in records:
        # Подключение к Telegram и вывод имя аккаунта в консоль / терминал
        client = await telegram_connect_and_output_name(row, db_handler)
        # Подписываемся на группу которую будем inviting, если аккаунт новый, то он автоматически подпишется и
        # записываем действия в software_database.db
        logger.info(link_group)
        await subscribe_to_group_or_channel(client, link_group)
        records: list = await db_handler.open_and_read_data(name_database_table)
        logger.info(f"Всего username: {len(records)}")  # Количество аккаунтов на данный момент в работе
        try:
            await inviting(client, records)
        except FloodWaitError as e:
            logger.error(f'Flood! wait for {str(datetime.timedelta(seconds=e.seconds))}')
            continue  # Прерываем работу и меняем аккаунт


async def invite_from_multiple_accounts_with_limits(name_database_table, db_handler) -> None:
    """Inviting по заранее parsing списку и работа с несколькими аккаунтами и выставленными лимитами"""
    # Открываем базу данных для работы с аккаунтами user_settings/software_database.db
    records: list = await db_handler.open_and_read_data("config")
    for row in records:
        # Подключение к Telegram и вывод имя аккаунта в консоль / терминал
        client, phone = telegram_connect_and_output_name(row, db_handler)
        # Подписываемся на группу которую будем inviting, если аккаунт новый, то он автоматически подпишется и
        # записываем действия в software_database.db
        await subscribe_to_group_or_channel(client, link_group)
        number_usernames: list = db_handler.open_and_read_data(name_database_table)
        records: list = db_handler.open_the_db_and_read_the_data_lim(name_database_table, number_of_accounts=limits)
        # Количество аккаунтов на данный момент в работе
        logger.info(f"Всего username: {len(number_usernames)}. Лимит на аккаунт: {len(records)}")
        await inviting(client, records)


configs_reader = ConfigReader()
time_inviting_1, time_inviting_2 = configs_reader.get_time_inviting()


async def inviting(client, records) -> None:
    """Inviting"""
    for rows in records:
        username = rows[0]  # Имя аккаунта пользователя в базе данных user_settings/software_database.db
        try:
            await inviting_to_a_group(client, username)  # Inviting user в группу
        except AuthKeyDuplicatedError:
            record_and_interrupt(time_inviting_1, time_inviting_2)
            break  # Прерываем работу и меняем аккаунт
        except FloodWaitError as error:
            record_and_interrupt(time_inviting_1, time_inviting_2)
            break  # Прерываем работу и меняем аккаунт
        except PeerFloodError:
            record_and_interrupt(time_inviting_1, time_inviting_2)
            break  # Прерываем работу и меняем аккаунт
        except UserPrivacyRestrictedError:
            logger.error(f"""Попытка приглашения {username} в группу {link_group}. Настройки конфиденциальности 
                             {username} не позволяют вам inviting""")
            await record_inviting_results(time_inviting_1, time_inviting_2, username)
        except UserChannelsTooMuchError:
            logger.error(f"""Попытка приглашения {username} в группу {link_group}. Превышен лимит у user каналов / 
                             супергрупп.""")
            await record_inviting_results(time_inviting_1, time_inviting_2, username)
        except UserBannedInChannelError:
            record_and_interrupt(time_inviting_1, time_inviting_2)
            break  # Прерываем работу и меняем аккаунт
        except ChatWriteForbiddenError:
            logger.error(f"""Попытка приглашения {username} в группу {link_group}. Настройки в чате не дают добавлять 
                             людей в чат, возможно стоит бот админ и нужно подписаться на другие проекты""")
            await record_inviting_results(time_inviting_1, time_inviting_2, username)
            break  # Прерываем работу и меняем аккаунт
        except BotGroupsBlockedError:
            logger.error(f"Попытка приглашения {username} в группу {link_group}. Вы не можете добавить бота в группу.")
            await record_inviting_results(time_inviting_1, time_inviting_2, username)
        except UserNotMutualContactError:
            logger.error(f"Попытка приглашения {username} в группу {link_group}. User не является взаимным контактом.")
            await record_inviting_results(time_inviting_1, time_inviting_2, username)
        except ChatAdminRequiredError:
            logger.error(f"Попытка приглашения {username} в группу {link_group}. Требуются права администратора.")
            await record_inviting_results(time_inviting_1, time_inviting_2, username)
        except UserKickedError:
            logger.error(f"""Попытка приглашения {username} в группу {link_group}. Пользователь был удален ранее из 
                             супергруппы.""")
            await record_inviting_results(time_inviting_1, time_inviting_2, username)
        except ChannelPrivateError:
            record_and_interrupt(time_inviting_1, time_inviting_2)
            break  # Прерываем работу и меняем аккаунт
        except (UserIdInvalidError, UsernameNotOccupiedError, ValueError, UsernameInvalidError):
            logger.error(f"Попытка приглашения {username} в группу {link_group}. Не корректное имя {username}")
            await record_inviting_results(time_inviting_1, time_inviting_2, username)
        except (TypeError, UnboundLocalError):
            continue  # Записываем ошибку в software_database.db и продолжаем работу
        except InviteRequestSentError:
            logger.error(f"""Попытка приглашения {username} в группу {link_group}. Доступ к функциям группы станет 
                             возможен после утверждения заявки администратором на {link_group}""")
            await record_inviting_results(time_inviting_1, time_inviting_2, username)
            break  # Прерываем работу и меняем аккаунт
        except TypeNotFoundError:
            record_and_interrupt(time_inviting_1, time_inviting_2)
            break  # Прерываем работу и меняем аккаунт
        except KeyboardInterrupt:  # Закрытие окна программы
            client.disconnect()  # Разрываем соединение telegram
            logger.info("[!] Скрипт остановлен!")
        else:
            # Записываем данные в базу данных, чистим список кого добавляли или писали сообщение
            logger.info(f"[+] Участник {username} добавлен, если не состоит в чате {link_group}")
            await record_inviting_results(time_inviting_1, time_inviting_2, username)
    await unsubscribe_from_the_group(client, link_group)  # Отписка из группы
    client.disconnect()  # Разрываем соединение telegram
