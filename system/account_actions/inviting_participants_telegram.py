# -*- coding: utf-8 -*-
import time

from loguru import logger
from telethon.errors import AuthKeyDuplicatedError, PeerFloodError, FloodWaitError, UserPrivacyRestrictedError, \
    UserChannelsTooMuchError, BotGroupsBlockedError, ChatWriteForbiddenError, UserBannedInChannelError, \
    UserNotMutualContactError, ChatAdminRequiredError, UserKickedError, ChannelPrivateError, UserIdInvalidError, \
    UsernameNotOccupiedError, UsernameInvalidError, InviteRequestSentError, TypeNotFoundError
from telethon.tl.functions.channels import InviteToChannelRequest

from system.account_actions.TGConnect import TGConnect
from system.account_actions.TGLimits import SettingLimits
from system.account_actions.TGSubUnsub import SubscribeUnsubscribeTelegram
from system.auxiliary_functions.auxiliary_functions import record_and_interrupt, record_inviting_results
from system.auxiliary_functions.global_variables import ConfigReader
from system.sqlite_working_tools.sqlite_working_tools import DatabaseHandler


async def inviting_with_limits() -> None:
    """Инвайтинг с лимитами на аккаунт"""
    logger.info(f"Запуск инвайтинга с лимитами")

    inviting_to_a_group = InvitingToAGroup()
    inviting_with_limits_class = SettingLimits()
    tg_connect = TGConnect()

    accounts = await inviting_to_a_group.reading_the_list_of_accounts_from_the_database()
    for account in accounts:
        logger.info(f"{account[0]}")

        """Получение ссылки для инвайтинга"""
        links_inviting = await inviting_to_a_group.getting_an_invitation_link_from_the_database()
        for link in links_inviting:
            logger.info(f"{link[0]}")
            proxy = await tg_connect.reading_proxies_from_the_database()
            client = await tg_connect.connecting_to_telegram(account[0], proxy,
                                                             "user_settings/accounts/inviting")
            await client.connect()

            """Подписка на группу для инвайтинга"""
            sub_unsub_tg = SubscribeUnsubscribeTelegram()
            await sub_unsub_tg.subscribe_to_group_or_channel(client, link[0])

            """Получение списка usernames"""
            number_usernames = await inviting_with_limits_class.get_usernames_with_limits(table_name="members")

            logger.info(f"{number_usernames}")
            for username in number_usernames:
                logger.info(f"Пользователь username:{username[0]}")

                """Инвайтинг в группу по полученному списку"""
                config_reader = ConfigReader()
                time_inviting = config_reader.get_time_inviting()
                time_inviting_1 = time_inviting[0]
                time_inviting_2 = time_inviting[1]
                try:
                    await inviting_to_a_group.inviting_to_a_group_according_to_the_received_list(client, link,
                                                                                                 username)

                except PeerFloodError:
                    logger.error(f"Попытка приглашения {username} в группу {link[0]}. Настройки "
                                 f"конфиденциальности {username} не позволяют вам inviting")
                    record_and_interrupt(time_inviting_1, time_inviting_2)
                    break  # Прерываем работу и меняем аккаунт
                except AuthKeyDuplicatedError:
                    record_and_interrupt(time_inviting_1, time_inviting_2)
                    break  # Прерываем работу и меняем аккаунт
                except FloodWaitError as error:
                    logger.error(f'{error}')
                    record_and_interrupt(time_inviting_1, time_inviting_2)
                    break  # Прерываем работу и меняем аккаунт
                except UserPrivacyRestrictedError:
                    logger.error(
                        f"Попытка приглашения {username} в группу {link[0]}. Настройки конфиденциальности "
                        f"{username} не позволяют вам inviting")
                    await record_inviting_results(time_inviting_1, time_inviting_2, username)
                except UserChannelsTooMuchError:
                    logger.error(
                        f"Попытка приглашения {username} в группу {link[0]}. Превышен лимит у user каналов / "
                        f"супергрупп.")
                    await record_inviting_results(time_inviting_1, time_inviting_2, username)
                    continue
                except UserBannedInChannelError:
                    record_and_interrupt(time_inviting_1, time_inviting_2)
                    break  # Прерываем работу и меняем аккаунт
                except ChatWriteForbiddenError:
                    logger.error(f"Попытка приглашения {username} в группу {link[0]}. Настройки в чате не дают "
                                 f"добавлять людей в чат, возможно стоит бот админ и нужно подписаться на "
                                 f"другие проекты")
                    await record_inviting_results(time_inviting_1, time_inviting_2, username)
                    break  # Прерываем работу и меняем аккаунт
                except BotGroupsBlockedError:
                    logger.error(f"Попытка приглашения {username} в группу {link[0]}. Вы не можете добавить "
                                 f"бота в группу.")
                    await record_inviting_results(time_inviting_1, time_inviting_2, username)
                except UserNotMutualContactError:
                    logger.error(f"Попытка приглашения {username} в группу {link[0]}. User не является"
                                 f" взаимным контактом.")
                    await record_inviting_results(time_inviting_1, time_inviting_2, username)
                except ChatAdminRequiredError:
                    logger.error(f"Попытка приглашения {username} в группу {link[0]}. Требуются права "
                                 f"администратора.")
                    await record_inviting_results(time_inviting_1, time_inviting_2, username)
                except UserKickedError:
                    logger.error(f"Попытка приглашения {username} в группу {link[0]}. Пользователь был удален "
                                 f"ранее из супергруппы.")
                    await record_inviting_results(time_inviting_1, time_inviting_2, username)
                except ChannelPrivateError:
                    record_and_interrupt(time_inviting_1, time_inviting_2)
                    break  # Прерываем работу и меняем аккаунт
                except (UserIdInvalidError, UsernameNotOccupiedError, ValueError, UsernameInvalidError):
                    await record_inviting_results(time_inviting_1, time_inviting_2, username)
                    logger.error(f"Попытка приглашения {username} в группу {link[0]}. Не корректное имя "
                                 f"{username}")
                    break  # Прерываем работу и меняем аккаунт
                except (TypeError, UnboundLocalError):
                    logger.error(f"Попытка приглашения {username} в группу {link[0]}")
                    continue  # Записываем ошибку в software_database.db и продолжаем работу
                except InviteRequestSentError:
                    logger.error(f"Попытка приглашения {username} в группу {link[0]}. Доступ к функциям группы "
                                 f"станет возможен после утверждения заявки администратором на {link[0]}")
                    await record_inviting_results(time_inviting_1, time_inviting_2, username)
                    break  # Прерываем работу и меняем аккаунт
                except TypeNotFoundError:
                    record_and_interrupt(time_inviting_1, time_inviting_2)
                    break  # Прерываем работу и меняем аккаунт
                except KeyboardInterrupt:  # Закрытие окна программы
                    client.disconnect()  # Разрываем соединение telegram
                    logger.info("[!] Скрипт остановлен!")
                else:
                    logger.info(f"[+] Участник {username} добавлен, если не состоит в чате {link[0]}")
                    await record_inviting_results(time_inviting_1, time_inviting_2, username)

            await inviting_to_a_group.unsubscribing_from_group_for_inviting(client, link)

    logger.info(f"Окончание  инвайтинга с лимитами")


async def inviting_without_limits() -> None:
    """Инвайтинг без лимитов"""
    logger.info(f"Запуск инвайтинга без лимитов")
    inviting_to_a_group = InvitingToAGroup()
    inviting_with_limits_class = SettingLimits()
    tg_connect = TGConnect()

    """Инвайтинг"""
    accounts = await inviting_to_a_group.reading_the_list_of_accounts_from_the_database()
    for account in accounts:
        logger.info(f"{account[0]}")

        """Получение ссылки для инвайтинга"""
        links_inviting = await inviting_to_a_group.getting_an_invitation_link_from_the_database()
        for link in links_inviting:
            logger.info(f"{link[0]}")
            proxy = await tg_connect.reading_proxies_from_the_database()
            client = await tg_connect.connecting_to_telegram(account[0], proxy,
                                                             "user_settings/accounts/inviting")
            await client.connect()

            """Подписка на группу для инвайтинга"""
            sub_unsub_tg = SubscribeUnsubscribeTelegram()
            await sub_unsub_tg.subscribe_to_group_or_channel(client, link[0])

            """Получение списка usernames"""
            number_usernames = await inviting_with_limits_class.get_usernames_without_limits(table_name="members")
            for username in number_usernames:
                logger.info(f"Пользователь username:{username[0]}")

                """Инвайтинг в группу по полученному списку"""
                config_reader = ConfigReader()
                time_inviting = config_reader.get_time_inviting()
                time_inviting_1 = time_inviting[0]
                time_inviting_2 = time_inviting[1]
                try:
                    await inviting_to_a_group.inviting_to_a_group_according_to_the_received_list(client, link,
                                                                                                 username)
                except PeerFloodError:
                    logger.error(f"Попытка приглашения {username} в группу {link[0]}. Настройки "
                                 f"конфиденциальности {username} не позволяют вам inviting")
                    record_and_interrupt(time_inviting_1, time_inviting_2)
                    break  # Прерываем работу и меняем аккаунт
                except AuthKeyDuplicatedError:
                    record_and_interrupt(time_inviting_1, time_inviting_2)
                    break  # Прерываем работу и меняем аккаунт
                except FloodWaitError as error:
                    logger.error(f'{error}')
                    record_and_interrupt(time_inviting_1, time_inviting_2)
                    break  # Прерываем работу и меняем аккаунт
                except UserPrivacyRestrictedError:
                    logger.error(
                        f"Попытка приглашения {username} в группу {link[0]}. Настройки конфиденциальности "
                        f"{username} не позволяют вам inviting")
                    await record_inviting_results(time_inviting_1, time_inviting_2, username)
                except UserChannelsTooMuchError:
                    logger.error(
                        f"Попытка приглашения {username} в группу {link[0]}. Превышен лимит у user каналов / "
                        f"супергрупп.")
                    await record_inviting_results(time_inviting_1, time_inviting_2, username)
                    continue
                except UserBannedInChannelError:
                    record_and_interrupt(time_inviting_1, time_inviting_2)
                    break  # Прерываем работу и меняем аккаунт
                except ChatWriteForbiddenError:
                    logger.error(f"Попытка приглашения {username} в группу {link[0]}. Настройки в чате не дают "
                                 f"добавлять людей в чат, возможно стоит бот админ и нужно подписаться на "
                                 f"другие проекты")
                    await record_inviting_results(time_inviting_1, time_inviting_2, username)
                    break  # Прерываем работу и меняем аккаунт
                except BotGroupsBlockedError:
                    logger.error(f"Попытка приглашения {username} в группу {link[0]}. Вы не можете добавить "
                                 f"бота в группу.")
                    await record_inviting_results(time_inviting_1, time_inviting_2, username)
                except UserNotMutualContactError:
                    logger.error(f"Попытка приглашения {username} в группу {link[0]}. User не является"
                                 f" взаимным контактом.")
                    await record_inviting_results(time_inviting_1, time_inviting_2, username)
                except ChatAdminRequiredError:
                    logger.error(f"Попытка приглашения {username} в группу {link[0]}. Требуются права "
                                 f"администратора.")
                    await record_inviting_results(time_inviting_1, time_inviting_2, username)
                except UserKickedError:
                    logger.error(f"Попытка приглашения {username} в группу {link[0]}. Пользователь был удален "
                                 f"ранее из супергруппы.")
                    await record_inviting_results(time_inviting_1, time_inviting_2, username)
                except ChannelPrivateError:
                    record_and_interrupt(time_inviting_1, time_inviting_2)
                    break  # Прерываем работу и меняем аккаунт
                except (UserIdInvalidError, UsernameNotOccupiedError, ValueError, UsernameInvalidError):
                    await record_inviting_results(time_inviting_1, time_inviting_2, username)
                    logger.error(f"Попытка приглашения {username} в группу {link[0]}. Не корректное имя "
                                 f"{username}")
                    break  # Прерываем работу и меняем аккаунт
                except (TypeError, UnboundLocalError):
                    logger.error(f"Попытка приглашения {username} в группу {link[0]}")
                    continue  # Записываем ошибку в software_database.db и продолжаем работу
                except InviteRequestSentError:
                    logger.error(f"Попытка приглашения {username} в группу {link[0]}. Доступ к функциям группы "
                                 f"станет возможен после утверждения заявки администратором на {link[0]}")
                    await record_inviting_results(time_inviting_1, time_inviting_2, username)
                    break  # Прерываем работу и меняем аккаунт
                except TypeNotFoundError:
                    record_and_interrupt(time_inviting_1, time_inviting_2)
                    break  # Прерываем работу и меняем аккаунт
                except KeyboardInterrupt:  # Закрытие окна программы
                    client.disconnect()  # Разрываем соединение telegram
                    logger.info("[!] Скрипт остановлен!")
                else:
                    logger.info(f"[+] Участник {username} добавлен, если не состоит в чате {link[0]}")
                    await record_inviting_results(time_inviting_1, time_inviting_2, username)

            await inviting_to_a_group.unsubscribing_from_group_for_inviting(client, link)
    logger.info("[!] Инвайтинг окончен!")


class InvitingToAGroup:
    def __init__(self):
        self.db_handler = DatabaseHandler()
        self.sub_unsub_tg = SubscribeUnsubscribeTelegram()

    async def reading_the_list_of_accounts_from_the_database(self) -> list:
        """Inviting по заранее parsing списку и работа с несколькими аккаунтами"""
        accounts: list = await self.db_handler.open_and_read_data("config")
        logger.info(f"Всего accounts: {len(accounts)}")
        return accounts

    async def getting_an_invitation_link_from_the_database(self):
        """"Получение ссылки для инвайтинга"""
        links_inviting: list = await self.db_handler.open_and_read_data("links_inviting")  # Открываем базу данных
        logger.info(f"Ссылка для инвайтинга:  {links_inviting}")
        return links_inviting

    async def inviting_to_a_group_according_to_the_received_list(self, client, link_row, username) -> None:
        logger.error(f"Попытка приглашения {username[0]} в группу {link_row[0]}.")
        await client(InviteToChannelRequest(link_row[0], [username[0]]))
        logger.info(f'Удачно! Спим 5 секунд')
        time.sleep(5)

    async def unsubscribing_from_group_for_inviting(self, client, link_row):
        """Отписка от группы"""
        await self.sub_unsub_tg.unsubscribe_from_the_group(client, link_row[0])  # Отписка из группы
        await client.disconnect()  # Разрываем соединение telegram telegram telegram


if __name__ == "__main__":
    inviting_without_limits()
    inviting_with_limits()
