# import datetime

from loguru import logger
# from telethon.errors import *

from system.account_actions.subscription.subscription import subscribe_to_group_or_channel
    # subscribe_to_the_group_and_send_the_link
# from system.account_actions.unsubscribe.unsubscribe import unsubscribe_from_the_group
# from system.auxiliary_functions.auxiliary_functions import record_and_interrupt
# from system.auxiliary_functions.auxiliary_functions import record_inviting_results
from system.auxiliary_functions.global_variables import ConfigReader
from system.sqlite_working_tools.sqlite_working_tools import DatabaseHandler

from system.telegram_actions.telegram_actions import telegram_connect_and_output_name


class InvitingToAGroup:
    """Инвайтинг в группу"""

    def __init__(self):
        self.db_handler = DatabaseHandler()  # Открываем базу с аккаунтами и с выставленными лимитами
        self.configs_reader = ConfigReader()
        self.limits = self.configs_reader.get_limits()
        self.time_inviting_1, time_inviting_2 = self.configs_reader.get_time_inviting()
        self.time_inviting_2 = self.configs_reader.get_time_inviting()

    async def invite_from_multiple_accounts_with_limits(self) -> None:
        """Inviting по заранее parsing списку и работа с несколькими аккаунтами и выставленными лимитами"""
        try:
            records: list = await self.db_handler.open_and_read_data("config")  # Открываем базу данных для работы с аккаунтами user_settings/software_database.db
            logger.info(f"Всего аккаунтов:  {len(records)}")
            for row in records:
                logger.info(f"Имя аккаунта: {row[0]}")
                await self.connecting_to_telegram_account(row, self.db_handler)
        except Exception as e:
            logger.error(f"Error: {e}")

    async def connecting_to_telegram_account(self, row, db_handler):
        # Подключение к Telegram и вывод имя аккаунта в консоль / терминал
        client = await telegram_connect_and_output_name(row, db_handler)

        records: list = await self.db_handler.open_and_read_data("writing_group_links")  # Открываем базу данных
        await subscribe_to_group_or_channel(client, records)

        # number_usernames: list = await self.db_handler.open_and_read_data(name_database_table) records: list =
        # await self.db_handler.open_the_db_and_read_the_data_lim(name_database_table,
        # number_of_accounts=self.limits) Количество аккаунтов на данный момент в работе logger.info(f"Всего
        # username: {len(number_usernames)}. Лимит на аккаунт: {len(records)}") await self.inviting(client, records)

    # async def connecting_to_telegram_account_1(self, row, name_database_table, db_handler):
    # Подключение к Telegram и вывод имя аккаунта в консоль / терминал
    # client = await telegram_connect_and_output_name(row, db_handler)

    # records: list = await self.db_handler.open_and_read_data("writing_group_links")  # Открываем базу данных
    # await subscribe_to_group_or_channel(client, records)

    # groups_wr = await subscribe_to_the_group_and_send_the_link(client, records)
    # logger.info(groups_wr)
    # records: list = await self.db_handler.open_and_read_data(name_database_table)
    # logger.info(f"Всего username: {len(records)}")  # Количество аккаунтов на данный момент в работе
    # await self.inviting(client, records)

    # async def inviting_to_a_group(self, client, username) -> None:
    #     """Inviting в группу"""
    #     logger.info(username)
    #     try:
    #         records: list = await self.db_handler.open_and_read_data("writing_group_links")  # Открываем базу данных
    #         groups_wr = await subscribe_to_the_group_and_send_the_link(client, records)
    #         await client(functions.channels.InviteToChannelRequest(channel=groups_wr, users=username))
    #     except UserBlockedError as e:
    #         logger.error(e)

    # async def inviting(self, client, records) -> None:
    #     """Inviting"""
    #     recordss: list = await self.db_handler.open_and_read_data("writing_group_links")  # Открываем базу данных
    #     groups_wr = await subscribe_to_the_group_and_send_the_link(client, recordss)
    #     logger.info(groups_wr)
    #
    #     for rows in records:
    #
    #         username = rows[0]  # Имя аккаунта пользователя в базе данных user_settings/software_database.db
    #         try:
    #             await self.inviting_to_a_group(client, username)  # Inviting user в группу
    #         except AuthKeyDuplicatedError:
    #             record_and_interrupt(self.time_inviting_1, self.time_inviting_2)
    #             break  # Прерываем работу и меняем аккаунт
    #         except FloodWaitError as error:
    #             record_and_interrupt(self.time_inviting_1, self.time_inviting_2)
    #             break  # Прерываем работу и меняем аккаунт
    #         except PeerFloodError:
    #             record_and_interrupt(self.time_inviting_1, self.time_inviting_2)
    #             break  # Прерываем работу и меняем аккаунт
    #         except UserPrivacyRestrictedError:
    #             logger.error(f"""Попытка приглашения {username} в группу {groups_wr}. Настройки конфиденциальности
    #                              {username} не позволяют вам inviting""")
    #             await record_inviting_results(self.time_inviting_1, self.time_inviting_2, username)
    #         except UserChannelsTooMuchError:
    #             logger.error(f"""Попытка приглашения {username} в группу {groups_wr}. Превышен лимит у user каналов /
    #                              супергрупп.""")
    #             await record_inviting_results(self.time_inviting_1, self.time_inviting_2, username)
    #         except UserBannedInChannelError:
    #             record_and_interrupt(self.time_inviting_1, self.time_inviting_2)
    #             break  # Прерываем работу и меняем аккаунт
    #         except ChatWriteForbiddenError:
    #             logger.error(
    #                 f"Попытка приглашения {username} в группу {groups_wr}. Настройки в чате не дают добавлять людей в чат, возможно стоит бот админ и нужно подписаться на другие проекты")
    #             await record_inviting_results(self.time_inviting_1, self.time_inviting_2, username)
    #             break  # Прерываем работу и меняем аккаунт
    #         except BotGroupsBlockedError:
    #             logger.error(
    #                 f"Попытка приглашения {username} в группу {groups_wr}. Вы не можете добавить бота в группу.")
    #             await record_inviting_results(self.time_inviting_1, self.time_inviting_2, username)
    #         except UserNotMutualContactError:
    #             logger.error(
    #                 f"Попытка приглашения {username} в группу {groups_wr}. User не является взаимным контактом.")
    #             await record_inviting_results(self.time_inviting_1, self.time_inviting_2, username)
    #         except ChatAdminRequiredError:
    #             logger.error(f"Попытка приглашения {username} в группу {groups_wr}. Требуются права администратора.")
    #             await record_inviting_results(self.time_inviting_1, self.time_inviting_2, username)
    #         except UserKickedError:
    #             logger.error(
    #                 f"Попытка приглашения {username} в группу {groups_wr}. Пользователь был удален ранее из супергруппы.")
    #             await record_inviting_results(self.time_inviting_1, self.time_inviting_2, username)
    #         except ChannelPrivateError:
    #             record_and_interrupt(self.time_inviting_1, self.time_inviting_2)
    #             break  # Прерываем работу и меняем аккаунт
    #         except (UserIdInvalidError, UsernameNotOccupiedError, ValueError, UsernameInvalidError):
    #             logger.error(f"Попытка приглашения {username} в группу {groups_wr}. Не корректное имя {username}")
    #             await record_inviting_results(self.time_inviting_1, self.time_inviting_2, username)
    #         except (TypeError, UnboundLocalError):
    #             continue  # Записываем ошибку в software_database.db и продолжаем работу
    #         except InviteRequestSentError:
    #             logger.error(
    #                 f"Попытка приглашения {username} в группу {groups_wr}. Доступ к функциям группы станет возможен после утверждения заявки администратором на {groups_wr}")
    #             await record_inviting_results(self.time_inviting_1, self.time_inviting_2, username)
    #             break  # Прерываем работу и меняем аккаунт
    #         except TypeNotFoundError:
    #             record_and_interrupt(self.time_inviting_1, self.time_inviting_2)
    #             break  # Прерываем работу и меняем аккаунт
    #         except KeyboardInterrupt:  # Закрытие окна программы
    #             client.disconnect()  # Разрываем соединение telegram
    #             logger.info("[!] Скрипт остановлен!")
    #         else:
    #             Записываем данные в базу данных, чистим список кого добавляли или писали сообщение
    # logger.info(f"[+] Участник {username} добавлен, если не состоит в чате {groups_wr}")
    # await record_inviting_results(self.time_inviting_1, self.time_inviting_2, username)
    # await unsubscribe_from_the_group(client, groups_wr)  # Отписка из группы
    # client.disconnect()  # Разрываем соединение telegram