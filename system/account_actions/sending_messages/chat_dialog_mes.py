import asyncio

from telethon import TelegramClient, events
from telethon.errors import UserBannedInChannelError
from telethon.tl.functions.channels import JoinChannelRequest
from loguru import logger

from system.auxiliary_functions.global_variables import api_id_data, api_hash_data


def mains():
    phone_number = '77076324730'  # Номер телефона и имя пользователя
    # Создаем клиент Telegram
    client = TelegramClient(f"user_settings/accounts/{phone_number}", api_id_data, api_hash_data)

    async def send_messages():  # Функция для отправки сообщений по чатам
        while True:
            # Получаем список чатов, которым нужно отправить сообщение
            chats = ['pyadminru_1', 'pyadminru_2']  # Замените на актуальные имена чатов
            for chat in chats:
                try:
                    await client.send_message(chat, 'Ваше сообщение здесь')
                except UserBannedInChannelError:
                    logger.error('Вам запрещено отправлять сообщения в супергруппах/каналах '
                                 '(вызвано запросом SendMessageRequest)')  # Выводим в лог ошибку
            logger.info('Спим 30 сек')
            await asyncio.sleep(30)

    @client.on(events.NewMessage())
    async def handle_private_messages(event):  # Функция для обработки входящих личных сообщений
        if event.is_private:  # Проверяем, является ли сообщение личным
            await event.respond('Ваш ответ на личное сообщение')  # Отвечаем на входящее сообщение

    async def join_chat(chat_link):
        await client(JoinChannelRequest(chat_link))

    async def main():
        await client.connect()  # Запускаем клиент Telegram
        chats = ['pyadminru_1', 'pyadminru_2']  # Замените на актуальные имена чатов
        for chat in chats:
            await join_chat(f'{chat}')  # Присоединяемся к чату
            logger.info(f'Подписываемся на чат {chat}')
        # Запускаем асинхронную функцию отправки сообщений по чатам
        asyncio.ensure_future(send_messages())
        await client.run_until_disconnected()

    client.loop.run_until_complete(main())  # Запускаем программу


if __name__ == '__main__':
    mains()
