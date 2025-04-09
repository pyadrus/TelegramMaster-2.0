import datetime
import json
from urllib.request import urlopen  # Изменено с urllib2 на urllib.request

import phonenumbers
import requests
from loguru import logger
from phonenumbers import carrier, geocoder
from telethon import TelegramClient
from telethon.errors import FilePartsInvalidError

from src.core.configs import program_version, date_of_program_change, program_name


def getting_phone_number_data_by_phone_number(phone_numbers):
    """
    Определение страны и оператора по номеру телефона

    :param phone_numbers: Номер телефона
    :return: None
    """

    # Пример номера телефона для анализа
    number = phonenumbers.parse(f"+{phone_numbers}", None)

    # Получение информации о стране и операторе на русском языке
    country_name = geocoder.description_for_number(number, "ru")
    operator_name = carrier.name_for_number(number, "ru")

    # Вывод информации
    logger.info(f"Номер: {phone_numbers}, Оператор: {operator_name}, Страна: {country_name}")


def get_country_flag(ip_address):
    """
    Определение страны по ip адресу на основе сервиса https://ipwhois.io/ru/documentation.
    Возвращает флаг и название страны.
    :param ip_address: ip адрес
    :return: флаг и название страны
    """
    try:
        ipwhois = json.load(urlopen(f'https://ipwho.is/{ip_address}'))
        return ipwhois['flag']['emoji'], ipwhois['country']
    except KeyError:
        return "🏳️", "🌍"


def get_external_ip():
    """Получение внешнего ip адреса"""
    try:
        response = requests.get('https://httpbin.org/ip')
        response.raise_for_status()
        return response.json().get("origin")
    except requests.RequestException as error:
        return None


async def loging():
    """
    Логирование TelegramMaster 2.0
    """

    local_ip = get_external_ip()
    emoji, country = get_country_flag(local_ip)

    client = TelegramClient('src/features/auth/log',
                            api_id=7655060,
                            api_hash="cc1290cd733c1f1d407598e5a31be4a8")
    await client.connect()
    # Красивое сообщение
    message = (
        f"🚀 **Launch Information**\n\n"

        f"Program name: `{program_name}`\n"
        f"🌍 IP Address: `{local_ip}`\n"
        f"📍 Location: {country} {emoji}\n"
        f"🕒 Date: `{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`\n"
        f"🔧 Program Version: `{program_version}`\n"
        f"📅 Date of Change: `{date_of_program_change}`"
    )
    try:
        await client.send_file(535185511, 'user_data/log/log_ERROR.log', caption=message)
        client.disconnect()
    except FilePartsInvalidError as error:
        logger.error(error)
        client.disconnect()


if __name__ == "__main__":
    loging()
    get_external_ip()
