# -*- coding: utf-8 -*-
import random
from loguru import logger
import requests


async def reading_proxy_data_from_the_database(db_handler):
    """Считываем данные для proxy c базы данных "software_database.db", таблица "proxy" где:
    proxy_type - тип proxy (например: SOCKS5), addr - адрес (например: 194.67.248.9), port - порт (например: 9795)
    username - логин (например: username), password - пароль (например: password)"""
    try:
        records: list = await db_handler.open_and_read_data("proxy")
        proxy_random_list = random.choice(records)
        logger.info(f"{proxy_random_list}")
        proxy = {'proxy_type': (proxy_random_list[0]), 'addr': proxy_random_list[1], 'port': int(proxy_random_list[2]),
                 'username': proxy_random_list[3], 'password': proxy_random_list[4], 'rdns': proxy_random_list[5]}
        return proxy
    except IndexError:
        proxy = None
        return proxy


def unpacking_a_dictionary_with_proxy_by_variables(proxy):
    """Распаковка словаря с proxy по переменным где: proxy_type - тип proxy (например: SOCKS5),
    addr - адрес (например: 194.67.248.9), port - порт (например: 9795) username - логин (например: username),
    password - пароль (например: password)"""
    proxy_type = proxy[0]  # Тип proxy (например: SOCKS5)
    addr = proxy[1]  # Адрес (например: 194.67.248.9)
    port = proxy[2]  # Порт (например: 9795)
    username = proxy[3]  # Логин (например: username)
    password = proxy[4]  # Пароль (например: password)
    rdns = proxy[5]
    return proxy_type, addr, port, username, password, rdns


async def checking_the_proxy_for_work(db_handler) -> None:
    """Проверка proxy на работоспособность с помощью Example.org. Example.org является примером адреса домена верхнего
    уровня, который используется для демонстрации работы сетевых протоколов. На этом сайте нет никакого контента, но он
    используется для различных тестов."""
    records: list = await db_handler.open_and_read_data("proxy")
    for proxy_dic in records:
        logger.info(proxy_dic)
        # Распаковка словаря с proxy по переменным
        proxy_type, addr, port, username, password, rdns = unpacking_a_dictionary_with_proxy_by_variables(proxy_dic)
        # Подключение к proxy с проверкой на работоспособность
        connecting_to_proxy_with_verification(proxy_type, addr, port, username, password, rdns, db_handler)


def connecting_to_proxy_with_verification(proxy_type, addr, port, username, password, rdns, db_handler) -> None:
    """Подключение к proxy с проверкой на работоспособность где: proxy_type - тип proxy (например: SOCKS5),
    addr - адрес (например: 194.67.248.9), port - порт (например: 9795), username - логин (например: username),
    password - пароль (например: password)"""
    # Пробуем подключиться по прокси
    try:
        # Указываем параметры прокси
        proxy = {'http': f'{proxy_type}://{username}:{password}@{addr}:{port}'}
        requests.get('http://example.org', proxies=proxy)
        logger.info('[!] Proxy рабочий!')
    # RequestException исключение возникает при ошибках, которые могут быть вызваны при запросе к веб-серверу.
    # Это может быть из-за недоступности сервера, ошибочного URL или других проблем с соединением.
    except requests.exceptions.RequestException:
        logger.info('[-] Proxy не рабочий!')
        db_handler.deleting_an_invalid_proxy(proxy_type, addr, port, username, password, rdns)
