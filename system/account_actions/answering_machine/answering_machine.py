import time

from telethon import TelegramClient
from telethon import events
from telethon.tl.functions.users import GetFullUserRequest

from system.auxiliary_functions.global_variables import api_id_data, api_hash_data
from system.proxy.checking_proxy import reading_proxy_data_from_the_database


def launching_an_answering_machine(db_handler) -> None:
    # Подключение к Telegram и вывод имени аккаунта в консоль / терминал
    proxy = reading_proxy_data_from_the_database(db_handler)  # Proxy IPV6 - НЕ РАБОТАЮТ
    client = TelegramClient(session=f"user_settings/accounts/sending_messages_chats/79252182362",
                            api_id=int(api_id_data),
                            api_hash=api_hash_data,
                            system_version="4.16.30-vxCUSTOM",
                            proxy=proxy)
    client.connect()  # Подсоединяемся к Telegram
    full = client(GetFullUserRequest('79252182362'))

    for user in full.users:
        first_name = user.first_name if user.first_name else ""
        last_name = user.last_name if user.last_name else ""
        phone = user.phone if user.phone else ""
        username = user.username if user.username else ""

    print(f'Номер телефона: {phone}, Фамилия: {last_name}, Имя: {first_name}, Username: {username}')

    message = "your message for replying your contacts"

    @client.on(events.NewMessage())
    async def normal_handler(event):
        if event.is_private:
            from_ = await event.client.get_entity(event.from_id)
            if not from_.bot:
                print(time.asctime(), '-', event.message)
                time.sleep(1)
                await event.respond(message)

    client.run_until_disconnected()  # Запуск клиента
