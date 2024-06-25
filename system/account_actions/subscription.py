# -*- coding: utf-8 -*-
import datetime
import random
import time

from loguru import logger
from telethon.errors import ChannelsTooMuchError, ChannelPrivateError, UsernameInvalidError, PeerFloodError, \
    FloodWaitError, InviteRequestSentError
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.contacts import ResolveUsernameRequest

from system.auxiliary_functions.auxiliary_functions import record_and_interrupt
from system.auxiliary_functions.global_variables import ConfigReader
from system.sqlite_working_tools.sqlite_working_tools import DatabaseHandler

configs_reader = ConfigReader()
time_subscription_1, time_subscription_2 = configs_reader.get_time_subscription()


async def subscribe_to_group_or_channel(client, groups_wr) -> None:
    """
    Подписываемся на группу или канал
    :param groups_wr: str - группа или канал
    :param client: TelegramClient - объект клиента
    """
    # цикл for нужен для того, что бы сработала команда brake команда break в Python используется только для выхода из
    # цикла, а не выхода из программы в целом.
    db_handler = DatabaseHandler()
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
            logger.error(f"Попытка подписки на группу / канал {groups_wrs}. Не верное имя или cсылка {groups_wrs} не "
                         f"является группой / каналом: {groups_wrs}")
            await db_handler.write_data_to_db("""SELECT * from writing_group_links""",
                                              """DELETE from writing_group_links where writing_group_links = ?""",
                                              groups_wrs)
        except PeerFloodError:
            logger.error(f"Попытка подписки на группу / канал {groups_wrs}. Предупреждение о Flood от Telegram.")
            time.sleep(random.randrange(50, 60))
        except FloodWaitError as e:
            logger.error(f"Попытка подписки на группу / канал {groups_wrs}. Flood! wait for "
                         f"{str(datetime.timedelta(seconds=e.seconds))}")
            record_and_interrupt(time_subscription_1, time_subscription_2)
            break  # Прерываем работу и меняем аккаунт
        except InviteRequestSentError:
            logger.error(f"Попытка подписки на группу / канал {groups_wrs}. Действия будут доступны после одобрения "
                         f"администратором на вступление в группу")
        except ResolveUsernameRequest:
            logger.error(f'Попытка подписки на группу / канал  {groups_wrs}. Действия будут доступны после одобрения')
