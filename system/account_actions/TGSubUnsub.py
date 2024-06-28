# -*- coding: utf-8 -*-
import datetime
import random
import time

from loguru import logger
from telethon.errors import ChannelsTooMuchError, ChannelPrivateError, UsernameInvalidError, PeerFloodError, \
    FloodWaitError, InviteRequestSentError
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.channels import LeaveChannelRequest
from telethon.tl.functions.contacts import ResolveUsernameRequest

from system.account_actions.TGConnect import TGConnect
from system.auxiliary_functions.auxiliary_functions import record_and_interrupt, find_files
from system.auxiliary_functions.global_variables import ConfigReader
from system.sqlite_working_tools.sqlite_working_tools import DatabaseHandler


class SubscribeUnsubscribeTelegram:

    def __init__(self):
        self.db_handler = DatabaseHandler()
        self.tg_connect = TGConnect()
        self.config_reader = ConfigReader()
        self.configs_reader = ConfigReader()
        self.time_subscription_1, self.time_subscription_2 = self.configs_reader.get_time_subscription()
        # self.inviting_to_a_group = InvitingToAGroup()

    async def connect_to_telegram(self, file):
        """Подключение к Telegram, используя файл session."""
        logger.info(f"{file[0]}")
        proxy = await self.tg_connect.reading_proxies_from_the_database()
        client = await self.tg_connect.connecting_to_telegram(file[0], proxy, "user_settings/accounts/unsubscribe")
        await client.connect()
        return client

    async def subscribe_telegram(self) -> None:
        """Подписка на группы / каналы Telegram"""
        logger.info(f"Запуск подписки на группы / каналы Telegram")
        entities = find_files(directory_path="user_settings/accounts/unsubscribe", extension='session')
        for file in entities:
            client = await self.connect_to_telegram(file)  # Подключение к Telegram

            """Получение ссылки для инвайтинга"""
            links_inviting: list = await self.db_handler.open_and_read_data("links_inviting")  # Открываем базу данных
            logger.info(f"Ссылка для инвайтинга:  {links_inviting}")
            # return links_inviting
            for link in links_inviting:
                logger.info(f"{link[0]}")

                """Подписка на группу для инвайтинга"""
                await self.subscribe_to_group_or_channel(client, link[0])

        logger.info(f"Окончание подписки на группы / каналы Telegram")

    async def unsubscribe_all(self) -> None:
        """Отписываемся от групп, каналов, личных сообщений"""
        entities = find_files(directory_path="user_settings/accounts/unsubscribe", extension='session')
        for file in entities:
            client = await self.connect_to_telegram(file)  # Подключение к Telegram
            dialogs = client.iter_dialogs()
            async for dialog in dialogs:
                logger.info(f"{dialog.name}, {dialog.id}")
                await client.delete_dialog(dialog)
            await client.disconnect()

    async def unsubscribe_from_the_group(self, client, group_link) -> None:
        """
        Отписываемся от группы.
        :param group_link: группа или канал
        :param client: Телеграм клиент
        """
        try:
            entity = await client.get_entity(group_link)
            if entity:
                await client(LeaveChannelRequest(entity))
        except ChannelPrivateError:  # Аккаунт Telegram не может отписаться так как не имеет доступа
            logger.error(
                f'Группа или канал: {group_link}, является закрытым или аккаунт не имеет доступ  к {group_link}')
        finally:
            await client.disconnect()  # Разрываем соединение с Telegram

    async def subscribe_to_group_or_channel(self, client, groups_wr) -> None:
        """
        Подписываемся на группу или канал
        :param groups_wr: str - группа или канал
        :param client: TelegramClient - объект клиента
        """
        # цикл for нужен для того, что бы сработала команда brake команда break в Python используется только для выхода из
        # цикла, а не выхода из программы в целом.
        groups_wra = [groups_wr]
        for groups_wrs in groups_wra:
            logger.info(groups_wrs)
            try:
                await client(JoinChannelRequest(groups_wrs))
                logger.info(f"Аккаунт подписался на группу / канал: {groups_wrs}")
            except ChannelsTooMuchError:
                """Если аккаунт подписан на множество групп и каналов, то отписываемся от них"""
                for dialog in client.iter_dialogs():
                    logger.info(f"{dialog.name}, {dialog.id}")
                    try:
                        client.delete_dialog(dialog)
                        client.disconnect()
                    except ConnectionError:
                        break
                logger.info("[+] Список почистили, и в файл записали.")
            except ChannelPrivateError:
                logger.error(f"Попытка подписки на группу / канал {groups_wrs}. Указанный канал / группа {groups_wrs} "
                             f"является приватным, или вам запретили подписываться.")
            except (UsernameInvalidError, ValueError, TypeError):
                logger.error(
                    f"Попытка подписки на группу / канал {groups_wrs}. Не верное имя или cсылка {groups_wrs} не "
                    f"является группой / каналом: {groups_wrs}")
                await self.db_handler.write_data_to_db("""SELECT * from writing_group_links""",
                                                  """DELETE from writing_group_links where writing_group_links = ?""",
                                                       groups_wrs)
            except PeerFloodError:
                logger.error(f"Попытка подписки на группу / канал {groups_wrs}. Предупреждение о Flood от Telegram.")
                time.sleep(random.randrange(50, 60))
            except FloodWaitError as e:
                logger.error(f"Попытка подписки на группу / канал {groups_wrs}. Flood! wait for "
                             f"{str(datetime.timedelta(seconds=e.seconds))}")
                record_and_interrupt(self.time_subscription_1, self.time_subscription_2)
                break  # Прерываем работу и меняем аккаунт
            except InviteRequestSentError:
                logger.error(
                    f"Попытка подписки на группу / канал {groups_wrs}. Действия будут доступны после одобрения "
                    f"администратором на вступление в группу")
            except ResolveUsernameRequest:
                logger.error(
                    f'Попытка подписки на группу / канал  {groups_wrs}. Действия будут доступны после одобрения')
