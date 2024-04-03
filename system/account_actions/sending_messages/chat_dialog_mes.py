import asyncio
import json
import random

from loguru import logger
from rich.progress import track
from telethon import TelegramClient, events
from telethon.errors import UserBannedInChannelError
from telethon.tl.functions.channels import JoinChannelRequest

from system.account_actions.sending_messages.telegram_chat_dialog import select_and_read_random_file
from system.auxiliary_functions.auxiliary_functions import find_files
from system.auxiliary_functions.global_variables import api_id_data, api_hash_data, time_sending_messages_1, \
    time_sending_messages_2, account_name_newsletter


def mains(db_handler):
    # phone_number = '77076324730'  # Номер телефона и имя пользователя
    # Создаем клиент Telegram
    client = TelegramClient(f"user_settings/accounts/{account_name_newsletter}", api_id_data, api_hash_data)

    async def send_messages():
        """Отправляет сообщения в чаты"""
        while True:
            # Получаем список чатов, которым нужно отправить сообщение
            records: list = db_handler.open_and_read_data("writing_group_links")  # Открываем базу данных
            logger.info(records)
            for chat in records:
                try:
                    entities = find_files(directory_path="user_settings/message", extension="json")  # Выбираем случайное сообщение из файла
                    logger.info(entities)  # Выводим список чатов
                    data = select_and_read_random_file(entities)  # Выбираем случайное сообщение из файла
                    await client.send_message(chat[0], f'{data}')
                    logger.info(f'Сообщение {data} отправлено в чат {chat[0]}')
                except UserBannedInChannelError:
                    logger.error('Вам запрещено отправлять сообщения в супергруппах/каналах '
                                 '(вызвано запросом SendMessageRequest)')  # Выводим в лог ошибку
            logger.info('Спим 30 сек')

            selected_shift_time = random.randrange(time_sending_messages_1, time_sending_messages_2)
            time_in_seconds = selected_shift_time * 60
            for _ in track(range(time_in_seconds), description=f"[red]Спим {time_in_seconds/60} минуты / минут..."):
                await asyncio.sleep(1)  # Спим 1 секунду



    def select_and_read_random_filess(entities):
        if entities:  # Проверяем, что список не пустой, если он не пустой
            # Выбираем рандомный файл для чтения
            random_file = random.choice(entities)  # Выбираем случайный файл для чтения из списка файлов
            logger.info(f"Выбран файл для чтения: {random_file[0]}.json")
            # Открываем выбранный файл с настройками
            with open(f"user_settings/answering_machine/{random_file[0]}.json", "r", encoding="utf-8") as file:
                data = json.load(file)  # Чтение файла
        return data  # Возвращаем данные из файла

    @client.on(events.NewMessage())
    async def handle_private_messages(event):
        """Обрабатывает входящие личные сообщения"""
        if event.is_private:  # Проверяем, является ли сообщение личным
            logger.info(f'Входящее сообщение: {event.message.message}')
            entities = find_files(directory_path="user_settings/answering_machine", extension="json")  # Получаем список аккаунтов
            logger.info(entities)  # Выводим список чатов
            data = select_and_read_random_filess(entities)
            logger.info(data)
            await event.respond(f'{data}')  # Отвечаем на входящее сообщение

    async def join_chat(chat_link):
        """Присоединяется к чату"""
        await client(JoinChannelRequest(chat_link))

    async def main(db_handler):
        """Главная функция"""
        await client.connect()  # Запускаем клиент Telegram
        records: list = db_handler.open_and_read_data("writing_group_links")  # Открываем базу данных
        logger.info(records)
        for chat in records:
            logger.info(f'Подписываемся на чат {chat[0]}')  # Выводим в лог имя чата, для проверки, что все работает
            await join_chat(f'{chat[0]}')  # Присоединяемся к чату
        asyncio.ensure_future(send_messages())  # Запускаем асинхронную функцию отправки сообщений по чатам
        await client.run_until_disconnected()

    client.loop.run_until_complete(main(db_handler))  # Запускаем программу
