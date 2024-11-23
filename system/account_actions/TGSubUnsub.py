# -*- coding: utf-8 -*-
import asyncio
import datetime
import random

from loguru import logger
from telethon.errors import (ChannelsTooMuchError, ChannelPrivateError, UsernameInvalidError, PeerFloodError,
                             FloodWaitError, InviteRequestSentError, UserDeactivatedBanError, SessionRevokedError)
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.channels import LeaveChannelRequest

from system.account_actions.TGConnect import TGConnect
from system.auxiliary_functions.auxiliary_functions import record_and_interrupt, find_filess
from system.auxiliary_functions.config import ConfigReader, path_subscription_folder, path_unsubscribe_folder
from system.sqlite_working_tools.sqlite_working_tools import DatabaseHandler


class SubscribeUnsubscribeTelegram:

    def __init__(self):
        self.db_handler = DatabaseHandler()
        self.tg_connect = TGConnect()
        self.configs_reader = ConfigReader()
        self.time_subscription_1, self.time_subscription_2 = self.configs_reader.get_time_subscription()

    async def subscribe_telegram(self) -> None:
        """
        Подписка на группы / каналы Telegram
        """
        try:
            logger.info(f"Запуск подписки на группы / каналы Telegram")
            for session_name in find_filess(directory_path=path_subscription_folder, extension='session'):
                client = await self.tg_connect.get_telegram_client(session_name,
                                                                   account_directory=path_subscription_folder)
                """Получение ссылки для инвайтинга"""
                links_inviting: list = await self.db_handler.open_and_read_data(
                    "writing_group_links")  # Открываем базу данных
                logger.info(f"Ссылка для инвайтинга:  {links_inviting}")
                for link in links_inviting:
                    logger.info(f"{link[0]}")
                    """Подписка на группу для инвайтинга"""
                    await self.subscribe_to_group_or_channel(client, link[0])

            logger.info(f"Окончание подписки на группы / каналы Telegram")
        except Exception as error:
            logger.exception(f"❌ Ошибка: {error}")  # Логируем возникшее исключение вместе с сообщением об ошибке.

    async def unsubscribe_all(self) -> None:
        """
        Отписываемся от групп, каналов, личных сообщений
        """
        try:
            for session_name in find_filess(directory_path=path_unsubscribe_folder, extension='session'):
                client = await self.tg_connect.get_telegram_client(session_name,
                                                                   account_directory=path_unsubscribe_folder)
                dialogs = client.iter_dialogs()
                logger.info(f"Диалоги: {dialogs}")
                async for dialog in dialogs:
                    logger.info(f"{dialog.name}, {dialog.id}")
                    await client.delete_dialog(dialog)
                await client.disconnect()
        except Exception as error:
            logger.exception(f"❌ Ошибка: {error}")  # Логируем возникшее исключение вместе с сообщением об ошибке.

    @staticmethod
    async def unsubscribe_from_the_group(client, group_link) -> None:
        """
        Отписываемся от группы.

        Аргументы:
        :param group_link: Группа или канал
        :param client: Телеграм клиент
        """
        try:
            entity = await client.get_entity(group_link)
            if entity:
                await client(LeaveChannelRequest(entity))
        except ChannelPrivateError:  # Аккаунт Telegram не может отписаться так как не имеет доступа
            logger.error(
                f'Группа или канал: {group_link}, является закрытым или аккаунт не имеет доступ  к {group_link}')
        except Exception as error:
            logger.exception(f"❌ Ошибка: {error}")  # Логируем возникшее исключение вместе с сообщением об ошибке.
        finally:
            await client.disconnect()  # Разрываем соединение с Telegram

    async def subscribe_to_group_or_channel(self, client, groups_wr) -> None:
        """
        Подписываемся на группу или канал

        Аргументы:
        :param groups_wr: str - группа или канал
        :param client:    TelegramClient - объект клиента
        """
        # цикл for нужен для того, что бы сработала команда brake команда break в Python используется только для выхода из
        # цикла, а не выхода из программы в целом.
        logger.info(f"Группа для подписки {groups_wr}")
        try:
            await client(JoinChannelRequest(groups_wr))
            logger.info(f"Аккаунт подписался на группу / канал: {groups_wr}")
        except SessionRevokedError:
            logger.error(
                f"❌ Попытка подписки на группу / канал {groups_wr}. Авторизация была признана недействительной из-за того, что пользователь завершил все сеансы.")
        except UserDeactivatedBanError:
            logger.error(f"❌ Попытка подписки на группу / канал {groups_wr}. Аккаунт заблокирован.")
        except ChannelsTooMuchError:
            """Если аккаунт подписан на множество групп и каналов, то отписываемся от них"""
            async for dialog in client.iter_dialogs():
                logger.info(f"{dialog.name}, {dialog.id}")
                try:
                    await client.delete_dialog(dialog)
                    await client.disconnect()
                except ConnectionError:
                    break
            logger.info("❌  Список почистили, и в файл записали.")
        except ChannelPrivateError:
            logger.error(f"❌ Попытка подписки на группу / канал {groups_wr}. Указанный канал / группа {groups_wr} "
                         f"является приватным, или вам запретили подписываться.")
        except (UsernameInvalidError, ValueError, TypeError):
            logger.error(
                f"❌ Попытка подписки на группу / канал {groups_wr}. Не верное имя или cсылка {groups_wr} не "
                f"является группой / каналом: {groups_wr}")
            await self.db_handler.write_data_to_db("""SELECT * from writing_group_links""",
                                                   """DELETE from writing_group_links where writing_group_links = ?""",
                                                   groups_wr)
        except PeerFloodError:
            logger.error(f"❌ Попытка подписки на группу / канал {groups_wr}. Предупреждение о Flood от Telegram.")
            await asyncio.sleep(random.randrange(50, 60))
        except FloodWaitError as e:
            logger.error(f"❌ Попытка подписки на группу / канал {groups_wr}. Flood! wait for "
                         f"{str(datetime.timedelta(seconds=e.seconds))}")
            await record_and_interrupt(self.time_subscription_1, self.time_subscription_2)
            # Прерываем работу и меняем аккаунт
            raise
        except InviteRequestSentError:
            logger.error(f"❌ Попытка подписки на группу / канал {groups_wr}. Действия будут доступны после одобрения "
                         f"администратором на вступление в группу")
        except Exception as error:
            logger.exception(f"❌ Ошибка: {error}")  # Логируем возникшее исключение вместе с сообщением об ошибке.
