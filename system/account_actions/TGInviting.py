# -*- coding: utf-8 -*-
import asyncio

from loguru import logger
from telethon.errors import (AuthKeyDuplicatedError, PeerFloodError, FloodWaitError, UserPrivacyRestrictedError,
                             UserChannelsTooMuchError, BotGroupsBlockedError, ChatWriteForbiddenError,
                             UserBannedInChannelError, UserNotMutualContactError, ChatAdminRequiredError,
                             UserKickedError, ChannelPrivateError, UserIdInvalidError, UsernameNotOccupiedError,
                             UsernameInvalidError, InviteRequestSentError, TypeNotFoundError)
from telethon.tl.functions.channels import InviteToChannelRequest

from system.account_actions.TGConnect import TGConnect
from system.account_actions.TGLimits import SettingLimits
from system.account_actions.TGSubUnsub import SubscribeUnsubscribeTelegram
from system.auxiliary_functions.auxiliary_functions import record_and_interrupt, record_inviting_results, find_filess
from system.auxiliary_functions.config import ConfigReader, path_inviting_folder
from system.sqlite_working_tools.sqlite_working_tools import DatabaseHandler


class InvitingToAGroup:
    def __init__(self):
        self.db_handler = DatabaseHandler()
        self.sub_unsub_tg = SubscribeUnsubscribeTelegram()
        self.limits_class = SettingLimits()
        self.tg_connect = TGConnect()
        self.config_reader = ConfigReader()

    async def getting_an_invitation_link_from_the_database(self):
        """"Получение ссылки для инвайтинга"""
        try:
            links_inviting: list = await self.db_handler.open_and_read_data("links_inviting")  # Открываем базу данных
            logger.info(f"Ссылка для инвайтинга:  {links_inviting}")
            return links_inviting
        except Exception as e:
            logger.exception(f"Ошибка: {e}")

    @staticmethod
    async def inviting_to_a_group_according_to_the_received_list(client, link_row, username,
                                                                 time_inviting) -> None:
        """
        Инвайтинг в группу
        :param client: Телеграм клиент
        :param link_row: Ссылка для инвайтинга
        :param username: username
        :param time_inviting: время инвайтинга
        """
        try:
            logger.info(f"Попытка приглашения {username[0]} в группу {link_row[0]}.")
            await client(InviteToChannelRequest(link_row[0], [username[0]]))
            logger.info(f'Удачно! Спим 5 секунд')
            await asyncio.sleep(5)
        except PeerFloodError:
            logger.error(f"Попытка приглашения {username} в группу {link_row[0]}. Настройки "
                         f"конфиденциальности {username} не позволяют вам inviting")
            await record_and_interrupt(time_inviting[0], time_inviting[1])
        except Exception as e:
            logger.exception(f"Ошибка: {e}")

    async def inviting_without_limits(self, account_limits) -> None:
        """
        Инвайтинг без лимитов
        :param account_limits: Таблица с лимитами
        """
        try:
            logger.info(f"Запуск инвайтинга без лимитов")
            for session_name in find_filess(directory_path=path_inviting_folder, extension='session'):
                client = await self.tg_connect.get_telegram_client(session_name,
                                                                   account_directory=path_inviting_folder)
                """Получение ссылки для инвайтинга"""
                for link in await self.getting_an_invitation_link_from_the_database():
                    logger.info(f"{link[0]}")
                    """Подписка на группу для инвайтинга"""
                    await self.sub_unsub_tg.subscribe_to_group_or_channel(client, link[0])
                    """Получение списка usernames"""
                    number_usernames = await self.limits_class.get_usernames_with_limits(table_name="members",
                                                                                         account_limits=account_limits)

                    if len(number_usernames) == 0:
                        logger.info(f"В таблице members нет пользователей для инвайтинга")
                        await self.sub_unsub_tg.unsubscribe_from_the_group(client, link[0])
                        break  # Прерываем работу и меняем аккаунт

                    for username in number_usernames:
                        logger.info(f"Пользователь username:{username[0]}")
                        """Инвайтинг в группу по полученному списку"""
                        time_inviting = self.config_reader.get_time_inviting()
                        try:
                            await self.inviting_to_a_group_according_to_the_received_list(client, link, username,
                                                                                          time_inviting)
                        except PeerFloodError:
                            logger.error(f"Попытка приглашения {username} в группу {link[0]}. Настройки "
                                         f"конфиденциальности {username} не позволяют вам inviting")
                            await record_and_interrupt(time_inviting[0], time_inviting[1])
                            break  # Прерываем работу и меняем аккаунт
                        except AuthKeyDuplicatedError:
                            await record_and_interrupt(time_inviting[0], time_inviting[1])
                            break  # Прерываем работу и меняем аккаунт
                        except FloodWaitError as error:
                            logger.error(f'{error}')
                            await record_and_interrupt(time_inviting[0], time_inviting[1])
                            break  # Прерываем работу и меняем аккаунт
                        except UserPrivacyRestrictedError:
                            logger.error(
                                f"Попытка приглашения {username} в группу {link[0]}. Настройки конфиденциальности "
                                f"{username} не позволяют вам inviting")
                            await record_inviting_results(time_inviting[0], time_inviting[1], username)
                        except UserChannelsTooMuchError:
                            logger.error(
                                f"Попытка приглашения {username} в группу {link[0]}. Превышен лимит у user каналов / "
                                f"супергрупп.")
                            await record_inviting_results(time_inviting[0], time_inviting[1], username)
                            continue
                        except UserBannedInChannelError:
                            await record_and_interrupt(time_inviting[0], time_inviting[1])
                            break  # Прерываем работу и меняем аккаунт
                        except ChatWriteForbiddenError:
                            logger.error(f"Попытка приглашения {username} в группу {link[0]}. Настройки в чате не дают "
                                         f"добавлять людей в чат, возможно стоит бот админ и нужно подписаться на "
                                         f"другие проекты")
                            await record_inviting_results(time_inviting[0], time_inviting[1], username)
                            break  # Прерываем работу и меняем аккаунт
                        except BotGroupsBlockedError:
                            logger.error(f"Попытка приглашения {username} в группу {link[0]}. Вы не можете добавить "
                                         f"бота в группу.")
                            await record_inviting_results(time_inviting[0], time_inviting[1], username)
                        except UserNotMutualContactError:
                            logger.error(f"Попытка приглашения {username} в группу {link[0]}. User не является"
                                         f" взаимным контактом.")
                            await record_inviting_results(time_inviting[0], time_inviting[1], username)
                        except ChatAdminRequiredError:
                            logger.error(f"Попытка приглашения {username} в группу {link[0]}. Требуются права "
                                         f"администратора.")
                            await record_inviting_results(time_inviting[0], time_inviting[1], username)
                        except UserKickedError:
                            logger.error(f"Попытка приглашения {username} в группу {link[0]}. Пользователь был удален "
                                         f"ранее из супергруппы.")
                            await record_inviting_results(time_inviting[0], time_inviting[1], username)
                        except ChannelPrivateError:
                            await record_and_interrupt(time_inviting[0], time_inviting[1])
                            break  # Прерываем работу и меняем аккаунт
                        except (UserIdInvalidError, UsernameNotOccupiedError, ValueError, UsernameInvalidError):
                            await record_inviting_results(time_inviting[0], time_inviting[1], username)
                            logger.error(f"Попытка приглашения {username} в группу {link[0]}. Не корректное имя "
                                         f"{username}")
                            break  # Прерываем работу и меняем аккаунт
                        except (TypeError, UnboundLocalError):
                            logger.error(f"Попытка приглашения {username} в группу {link[0]}")
                            continue  # Записываем ошибку в software_database.db и продолжаем работу
                        except InviteRequestSentError:
                            logger.error(f"Попытка приглашения {username} в группу {link[0]}. Доступ к функциям группы "
                                         f"станет возможен после утверждения заявки администратором на {link[0]}")
                            await record_inviting_results(time_inviting[0], time_inviting[1], username)
                            break  # Прерываем работу и меняем аккаунт
                        except TypeNotFoundError:
                            await record_and_interrupt(time_inviting[0], time_inviting[1])
                            break  # Прерываем работу и меняем аккаунт
                        except KeyboardInterrupt:  # Закрытие окна программы
                            client.disconnect()  # Разрываем соединение telegram
                            logger.info("[!] Скрипт остановлен!")
                        else:
                            logger.info(f"[+] Участник {username} добавлен, если не состоит в чате {link[0]}")
                            await record_inviting_results(time_inviting[0], time_inviting[1], username)

                    await self.sub_unsub_tg.unsubscribe_from_the_group(client, link[0])
            logger.info("[!] Инвайтинг окончен!")
        except Exception as e:
            logger.exception(f"Ошибка: {e}")
