import random

import requests
from rich import print

from system.sqlite_working_tools.sqlite_working_tools import deleting_an_invalid_proxy
from system.sqlite_working_tools.sqlite_working_tools import open_the_db_and_read_the_data


def reading_proxy_data_from_the_database():
    """Считываем данные для proxy c базы данных "software_database.db", таблица "proxy" где:
    proxy_type - тип proxy (например: SOCKS5), addr - адрес (например: 194.67.248.9), port - порт (например: 9795)
    username - логин (например: username), password - пароль (например: password)"""
    try:
        records: list = open_the_db_and_read_the_data(name_database_table="proxy")
        proxy_random_list = random.choice(records)
        print(f"[magenta]{proxy_random_list}")
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


def checking_the_proxy_for_work():
    """Проверка proxy на работоспособность с помощью Example.org. Example.org является примером адреса домена верхнего
    уровня, который используется для демонстрации работы сетевых протоколов. На этом сайте нет никакого контента, но он
    используется для различных тестов."""
    records: list = open_the_db_and_read_the_data(name_database_table="proxy")
    for proxy_dic in records:
        print(proxy_dic)
        # Распаковка словаря с proxy по переменным
        proxy_type, addr, port, username, password, rdns = unpacking_a_dictionary_with_proxy_by_variables(proxy_dic)
        # Подключение к proxy с проверкой на работоспособность
        connecting_to_proxy_with_verification(proxy_type, addr, port, username, password, rdns)


def connecting_to_proxy_with_verification(proxy_type, addr, port, username, password, rdns) -> None:
    """Подключение к proxy с проверкой на работоспособность где: proxy_type - тип proxy (например: SOCKS5),
    addr - адрес (например: 194.67.248.9), port - порт (например: 9795), username - логин (например: username),
    password - пароль (например: password)"""
    # Пробуем подключиться по прокси
    try:
        # Указываем параметры прокси
        proxy = {'http': f'{proxy_type}://{username}:{password}@{addr}:{port}'}
        requests.get('http://example.org', proxies=proxy)
        print('[magenta][!] Proxy рабочий!')
    # RequestException исключение возникает при ошибках, которые могут быть вызваны при запросе к веб-серверу.
    # Это может быть из-за недоступности сервера, ошибочного URL или других проблем с соединением.
    except requests.exceptions.RequestException:
        print('[magenta][-] Proxy не рабочий!')
        deleting_an_invalid_proxy(proxy_type, addr, port, username, password, rdns)


if __name__ == "__main__":
    reading_proxy_data_from_the_database()
    checking_the_proxy_for_work()
