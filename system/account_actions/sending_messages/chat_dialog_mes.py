import os
import time

import schedule
from loguru import logger
from rich import print

from system.account_actions.sending_messages.telegram_chat_dialog import sending_messages_via_chats_times


def send_mess(db_handler) -> None:
    entities = []  # Создаем словарь с именами найденных аккаунтов в папке user_settings/accounts
    for x in os.listdir(path="user_settings/message"):
        if x.endswith(".json"):
            file = os.path.splitext(x)[0]
            logger.info(f"Найденные файлы: {file}.json")  # Выводим имена найденных аккаунтов
            entities.append([file])

    sending_messages_via_chats_times(entities, db_handler)


def message_time() -> None:
    """
    Пишем сообщения от 1 до 5 раз в ча
    Метод every() модуля schedule, чтобы указать, что задача должна выполняться каждый день
    Метод at() для указания времени выполнения задачи, используя текущий час и значение минут, указанные пользователем
    Метод do() для указания функции, которую нужно вызвать в указанное время
    """
    print("[magenta]Сколько сообщений в час, мы будем отправлять\n",
          "[magenta][1[magenta]] - 1 сообщение в час\n",
          "[magenta][2[magenta]] - 2 сообщение в час\n",
          "[magenta][3[magenta]] - 3 сообщение в час\n",
          "[magenta][4[magenta]] - 4 сообщение в час\n",
          "[magenta][5[magenta]] - 5 сообщение в час\n", )
    user_input_mes_hour: str = input("[+] Введите от 1 до 5: ")
    if user_input_mes_hour == "1":  # Пишем сообщения 1 раз в час
        # Выводим на экран сообщение о том, что сообщения будут публиковаться раз в час
        print("[medium_purple3]Пишем сообщения 1 раз в час")
        # Получаем от пользователя значение минут для публикации сообщений
        user_input_minute_1 = input("[+] Введите минуты, публикации: ")
        # Создаем расписание на каждый час с помощью цикла for
        for hour in range(24):
            schedule.every().day.at(f"{hour:02d}:{user_input_minute_1}").do(send_mess)
    elif user_input_mes_hour == "2":  # Пишем сообщения 2 раза в час
        print("[medium_purple3]Пишем сообщения 2 раза в час")
        user_input_minute_1 = input("[+] Введите минуты, публикации: ")
        user_input_minute_2 = input("[+] Введите минуты, публикации: ")
        for hour in range(24):  # Перебираем часы от 0 до 23
            schedule.every().day.at(f"{hour:02d}:{user_input_minute_1}").do(send_mess)
            schedule.every().day.at(f"{hour:02d}:{user_input_minute_2}").do(send_mess)
    elif user_input_mes_hour == "3":  # Пишем сообщения 3 раза в час
        print("[medium_purple3]Пишем сообщения 3 раза в час")
        # Вводим часы и минуты, повторяем до тех пор, пока не будет нужное количество
        user_input_minute_1: str = input("[+] Введите минуты, публикации: ")
        user_input_minute_2: str = input("[+] Введите минуты, публикации: ")
        user_input_minute_3: str = input("[+] Введите минуты, публикации: ")
        for hour in range(24):  # Перебираем часы от 0 до 23
            schedule.every().day.at(f"{hour:02d}:{user_input_minute_1}").do(send_mess)
            schedule.every().day.at(f"{hour:02d}:{user_input_minute_2}").do(send_mess)
            schedule.every().day.at(f"{hour:02d}:{user_input_minute_3}").do(send_mess)
    elif user_input_mes_hour == "4":  # Пишем сообщения 4 раза в час
        print("[medium_purple3]Пишем сообщения 4 раза в час")
        # Вводим часы и минуты, повторяем до тех пор, пока не будет нужное количество
        user_input_minute_1: str = input("[+] Введите минуты, публикации: ")
        user_input_minute_2: str = input("[+] Введите минуты, публикации: ")
        user_input_minute_3: str = input("[+] Введите минуты, публикации: ")
        user_input_minute_4: str = input("[+] Введите минуты, публикации: ")
        for hour in range(24):  # Перебираем часы от 0 до 23
            schedule.every().day.at(f"{hour:02d}:{user_input_minute_1}").do(send_mess)
            schedule.every().day.at(f"{hour:02d}:{user_input_minute_2}").do(send_mess)
            schedule.every().day.at(f"{hour:02d}:{user_input_minute_3}").do(send_mess)
            schedule.every().day.at(f"{hour:02d}:{user_input_minute_4}").do(send_mess)
    elif user_input_mes_hour == "5":  # Пишем сообщения 5 раз в час
        print("[medium_purple3]Пишем сообщения 5 раза в час")
        # Вводим часы и минуты, повторяем до тех пор, пока не будет нужное количество
        user_input_minute_1: str = input("[+] Введите минуты, публикации: ")
        user_input_minute_2: str = input("[+] Введите минуты, публикации: ")
        user_input_minute_3: str = input("[+] Введите минуты, публикации: ")
        user_input_minute_4: str = input("[+] Введите минуты, публикации: ")
        user_input_minute_5: str = input("[+] Введите минуты, публикации: ")
        for hour in range(24):  # Перебираем часы от 0 до 23
            schedule.every().day.at(f"{hour:02d}:{user_input_minute_1}").do(send_mess)
            schedule.every().day.at(f"{hour:02d}:{user_input_minute_2}").do(send_mess)
            schedule.every().day.at(f"{hour:02d}:{user_input_minute_3}").do(send_mess)
            schedule.every().day.at(f"{hour:02d}:{user_input_minute_4}").do(send_mess)
            schedule.every().day.at(f"{hour:02d}:{user_input_minute_5}").do(send_mess)
    else:
        print("Ошибка выбора!")
    while True:
        schedule.run_pending()
        time.sleep(1)
