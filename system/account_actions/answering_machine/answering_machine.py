import time

from telethon import events
from telethon.tl.functions.users import GetFullUserRequest

from system.account_actions.creating.account_registration import telegram_connects


def launching_an_answering_machine(db_handler) -> None:
    # Подключение к Telegram и вывод имени аккаунта в консоль / терминал

    client = telegram_connects(db_handler, session=f"user_settings/accounts/sending_messages_chats/79252182362")

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
