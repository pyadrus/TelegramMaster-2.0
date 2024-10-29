from loguru import logger
from telethon import TelegramClient
import socket

from system.auxiliary_functions.config import program_version, date_of_program_change


def get_local_ip():
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    return local_ip


async def loging():
    """Логирование TelegramMaster 2.0"""

    local_ip = get_local_ip()
    logger.info(f"Запуск с {local_ip}")

    client = TelegramClient('system/logging_in/log_sender', api_id=7655060, api_hash="cc1290cd733c1f1d407598e5a31be4a8")
    await client.connect()

    await client.send_file(535185511, 'user_settings/log/log.log',
                           caption=f"Запуск с {local_ip},\n "
                                   f"Program version: {program_version}.\n"
                                   f"Date of change: {date_of_program_change}")
    client.disconnect()


if __name__ == "__main__":
    loging()
