import datetime
import random
import time

from loguru import logger
from telethon.errors import *
from telethon.tl.functions.channels import JoinChannelRequest

from system.auxiliary_functions.auxiliary_functions import record_and_interrupt
from system.auxiliary_functions.global_variables import ConfigReader
from system.sqlite_working_tools.sqlite_working_tools import DatabaseHandler
from system.telegram_actions.telegram_actions import telegram_connect_and_output_name

configs_reader = ConfigReader()
time_subscription_1, time_subscription_2 = configs_reader.get_time_subscription()


async def subscription_all(db_handler) -> None:
    """Подписываемся на каналы и группы, работаем по базе данных"""
    # Открываем базу данных для работы с аккаунтами user_settings/software_database.db
    records: list = db_handler.open_and_read_data("config")
    logger.info(f"Всего accounts: {len(records)}")
    for row in records:
        # Подключение к Telegram и вывод имя аккаунта в консоль / терминал
        client, phone = telegram_connect_and_output_name(row, db_handler)
        # Открываем базу данных
        records: list = db_handler.open_and_read_data("writing_group_links")
        logger.info(f"Всего групп: {len(records)}")
        for groups in records:  # Поочередно выводим записанные группы
            try:
                groups_wr = await subscribe_to_the_group_and_send_the_link(client, groups)
                logger.info(f"[+] Присоединился к группе или чату {groups_wr}")
                logger.info(f"[+] Подождите {time_subscription_1}-{time_subscription_2} Секунд...")
                time.sleep(random.randrange(int(time_subscription_1), int(time_subscription_2)))
            except FloodWaitError as e:
                logger.error(f"Flood! wait for {str(datetime.timedelta(seconds=e.seconds))}")
                time.sleep(e.seconds)
        client.disconnect()  # Разрываем соединение Telegram


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
        try:
            await client(JoinChannelRequest(groups_wrs))
            logger.info(f"Аккаунт подписался на группу: {groups_wrs}")
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
            logger.error(f"""Попытка подписки на группу / канал {groups_wr}. Указанный канал / группа {groups_wr} 
                             является приватным, или вам запретили подписываться.""")
        except (UsernameInvalidError, ValueError, TypeError):
            logger.error(f"""Попытка подписки на группу / канал {groups_wr}. Не верное имя или cсылка {groups_wrs} не 
                             является группой / каналом: {groups_wrs}""")
            await db_handler.write_data_to_db("""SELECT * from writing_group_links""",
                                              """DELETE from writing_group_links where writing_group_links = ?""",
                                              groups_wrs)
        except PeerFloodError:
            logger.error(f"""Попытка подписки на группу / канал {groups_wr}. Предупреждение о Flood от Telegram.""")
            time.sleep(random.randrange(50, 60))
        except FloodWaitError as e:
            logger.error(f"""Попытка подписки на группу / канал {groups_wr}. Flood! wait for 
                             {str(datetime.timedelta(seconds=e.seconds))}""")
            record_and_interrupt(time_subscription_1, time_subscription_2)
            break  # Прерываем работу и меняем аккаунт
        except InviteRequestSentError:
            logger.error(f"""Попытка подписки на группу / канал {groups_wr}. Действия будут доступны после одобрения 
                             администратором на вступление в группу""")


async def subscribe_to_the_group_and_send_the_link(client, groups):
    """Подписываемся на группу и передаем ссылку"""
    group = {"writing_group_links": groups[0]}
    # Вытягиваем данные из кортежа, для подстановки
    groups_wr = group["writing_group_links"]
    await subscribe_to_group_or_channel(client, groups_wr)
    return groups_wr
