import asyncio

from telethon import TelegramClient, events
from telethon.errors import UserBannedInChannelError
from telethon.tl.functions.channels import JoinChannelRequest
from loguru import logger
from rich.progress import track
from system.auxiliary_functions.global_variables import api_id_data, api_hash_data, time_sending_messages


def mains():
    phone_number = '77076324730'  # Номер телефона и имя пользователя
    # Создаем клиент Telegram
    client = TelegramClient(f"user_settings/accounts/{phone_number}", api_id_data, api_hash_data)

    async def send_messages():
        """Отправляет сообщения в чаты"""
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

            time_in_seconds = time_sending_messages * 60
            for _ in track(range(time_in_seconds), description=f"[red]Спим {time_sending_messages} минуты / минут..."):
                await asyncio.sleep(1)  # Спим 1 секунду

    @client.on(events.NewMessage())
    async def handle_private_messages(event):
        """Обрабатывает входящие личные сообщения"""
        if event.is_private:  # Проверяем, является ли сообщение личным
            await event.respond('Ваш ответ на личное сообщение')  # Отвечаем на входящее сообщение

    async def join_chat(chat_link):
        """Присоединяется к чату"""
        await client(JoinChannelRequest(chat_link))

    async def main():
        """Главная функция"""
        await client.connect()  # Запускаем клиент Telegram
        chats = ['pyadminru_1', 'pyadminru_2']  # Замените на актуальные имена чатов
        for chat in chats:
            await join_chat(f'{chat}')  # Присоединяемся к чату
            logger.info(f'Подписываемся на чат {chat}')
        asyncio.ensure_future(send_messages())  # Запускаем асинхронную функцию отправки сообщений по чатам
        await client.run_until_disconnected()

    client.loop.run_until_complete(main())  # Запускаем программу


if __name__ == '__main__':
    mains()
