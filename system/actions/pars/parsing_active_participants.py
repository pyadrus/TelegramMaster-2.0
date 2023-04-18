# coding: utf-8
import time

from rich import print

from system.actions.subscription.subscription import subscribe_to_group_or_channel
from system.error.telegram_errors import handle_exceptions_pars
from system.sqlite_working_tools.sqlite_working_tools import delete_duplicates
from system.sqlite_working_tools.sqlite_working_tools import open_the_db_and_read_the_data_lim
from system.sqlite_working_tools.sqlite_working_tools import writing_data_to_the_db
from system.telegram_actions.telegram_actions import connect_to_telegram_account_and_output_name

creating_a_table = "CREATE TABLE IF NOT EXISTS members_active (username, id, access_hash, name)"
writing_data_to_a_table = "INSERT INTO members_active (username, id, access_hash, name) VALUES (?, ?, ?, ?)"


@handle_exceptions_pars
def we_get_the_data_of_the_group_members_who_wrote_messages(client, chat, limit_active_user) -> None:
    """Получаем данные участников группы которые писали сообщения"""
    for message in client.iter_messages(chat, limit=int(limit_active_user)):
        from_user = client.get_entity(message.from_id.user_id)  # Получаем отправителя по ИД
        name = f"{from_user.first_name} {from_user.last_name}"
        entities = [from_user.username, from_user.id, from_user.access_hash, name]
        print(entities)
        writing_data_to_the_db(creating_a_table, writing_data_to_a_table, entities)


def parsing_of_active_participants(chat_input, limit_active_user) -> None:
    """Parsing участников, которые пишут в чат"""
    # Открываем базу с аккаунтами и с выставленными лимитами
    records: list = open_the_db_and_read_the_data_lim(name_database_table="config", number_of_accounts=1)
    for row in records:
        # Подключение к Telegram и вывод имя аккаунта в консоль / терминал
        client, phone = connect_to_telegram_account_and_output_name(row)
        # Подписываемся на чат, с которого будем parsing активных участников
        subscribe_to_group_or_channel(client, chat_input, phone)
        time.sleep(2)
        we_get_the_data_of_the_group_members_who_wrote_messages(client, chat_input, limit_active_user)
        client.disconnect()  # Разрываем соединение telegram
    delete_duplicates(table_name="members_active", column_name="id")  # Чистка дублирующих username по столбцу id
