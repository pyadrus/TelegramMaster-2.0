# -*- coding: utf-8 -*-
import random

import requests
from loguru import logger

from src.features.auth.logging_in import get_country_flag
from src.core.sqlite_working_tools import DatabaseHandler


async def reading_proxy_data_from_the_database(db_handler):
    """
    Считываем данные для proxy c базы данных "software_database.db", таблица "proxy" где:
    proxy_type - тип proxy (например: SOCKS5), addr - адрес (например: 194.67.248.9), port - порт (например: 9795)
    username - логин (например: username), password - пароль (например: password)

    :param db_handler - объект класса DatabaseHandler
    """
    try:
        proxy_random_list = random.choice(await db_handler.open_and_read_data("proxy"))
        logger.info(f"{proxy_random_list}")
        proxy = {'proxy_type': (proxy_random_list[0]), 'addr': proxy_random_list[1], 'port': int(proxy_random_list[2]),
                 'username': proxy_random_list[3], 'password': proxy_random_list[4], 'rdns': proxy_random_list[5]}
        return proxy
    except IndexError:
        proxy = None
        return proxy
    except Exception as error:
        logger.exception(f"❌ Ошибка: {error}")


async def checking_the_proxy_for_work() -> None:
    """
    Проверка proxy на работоспособность с помощью Example.org. Example.org является примером адреса домена верхнего
    уровня, который используется для демонстрации работы сетевых протоколов. На этом сайте нет никакого контента, но он
    используется для различных тестов.
    """
    try:
        for proxy_dic in await DatabaseHandler().open_and_read_data("proxy"):
            logger.info(proxy_dic)
            # Подключение к proxy с проверкой на работоспособность
            await connecting_to_proxy_with_verification(proxy_type=proxy_dic[0],  # Тип proxy (например: SOCKS5)
                                                        addr=proxy_dic[1],  # Адрес (например: 194.67.248.9)
                                                        port=proxy_dic[2],  # Порт (например: 9795)
                                                        username=proxy_dic[3],  # Логин (например: username)
                                                        password=proxy_dic[4],  # Пароль (например: password)
                                                        rdns=proxy_dic[5],
                                                        db_handler=DatabaseHandler())
    except Exception as error:
        logger.exception(f"❌ Ошибка: {error}")


async def connecting_to_proxy_with_verification(proxy_type, addr, port, username, password, rdns, db_handler) -> None:
    """Подключение к proxy с проверкой на работоспособность где: proxy_type - тип proxy (например: SOCKS5),
    addr - адрес (например: 194.67.248.9), port - порт (например: 9795), username - логин (например: username),
    password - пароль (например: password)

    :param proxy_type: тип proxy (например: SOCKS5)
    :param addr: адрес (например: 194.67.248.9)
    :param port: порт (например: 9795)
    :param username: логин (например: username)
    :param password: пароль (например: password)
    :param rdns: rdns (например: rdns)
    :param db_handler: объект класса DatabaseHandler
    """
    # Пробуем подключиться по прокси
    try:
        # Указываем параметры прокси
        proxy = {'http': f'{proxy_type}://{username}:{password}@{addr}:{port}'}
        emoji, country = get_country_flag(addr)
        logger.info(
            f"Проверяемый прокси: {proxy_type}://{username}:{password}@{addr}:{port}. Страна proxy {country} {emoji}")
        requests.get('http://example.org', proxies=proxy)
        logger.info(f'⚠️ Proxy: {proxy_type}://{username}:{password}@{addr}:{port} рабочий!')
    # RequestException исключение возникает при ошибках, которые могут быть вызваны при запросе к веб-серверу.
    # Это может быть из-за недоступности сервера, ошибочного URL или других проблем с соединением.
    except requests.exceptions.RequestException:
        logger.info('❌ Proxy не рабочий!')
        await db_handler.deleting_an_invalid_proxy(proxy_type, addr, port, username, password, rdns)
    except Exception as error:
        logger.exception(f"❌ Ошибка: {error}")
