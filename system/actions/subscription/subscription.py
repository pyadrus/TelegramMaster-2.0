import datetime
import random
import time

from rich import print
from rich.progress import track
from telethon.errors import *
from telethon.tl.functions.channels import JoinChannelRequest

from system.auxiliary_functions.auxiliary_functions import record_and_interrupt
from system.auxiliary_functions.global_variables import time_subscription_1
from system.auxiliary_functions.global_variables import time_subscription_2
from system.error.telegram_errors import record_account_actions
from system.menu.app_gui import program_window, done_button
from system.notification.notification import app_notifications
from system.sqlite_working_tools.sqlite_working_tools import DatabaseHandler
from system.telegram_actions.telegram_actions import connect_to_telegram_account_and_output_name

creating_a_table = """SELECT * from writing_group_links"""
writing_data_to_a_table = """DELETE from writing_group_links where writing_group_links = ?"""


def writing_group_links_to_file(name_database) -> None:
    """Запускаем окно программы (большого поля ввода)"""
    root, text = program_window()

    def output_values_from_the_input_field() -> None:
        """Выводим значения с поля ввода (то что ввел пользователь)"""
        message_text = text.get("1.0", "end-1c")
        closing_the_input_field()
        lines = message_text.split("\n")
        db_handler = DatabaseHandler()
        db_handler.write_to_single_column_table(name_database, lines)

    def closing_the_input_field() -> None:
        """Закрываем программу"""
        root.destroy()

    done_button(root, output_values_from_the_input_field)  # Кнопка "Готово"
    root.mainloop()  # Запускаем программу


def subscription_all() -> None:
    """Подписываемся на каналы и группы, работаем по базе данных"""
    # Открываем базу данных для работы с аккаунтами user_settings/software_database.db
    db_handler = DatabaseHandler()
    records: list = db_handler.open_and_read_data("config")
    print(f"[medium_purple3]Всего accounts: {len(records)}")
    for row in track(records, description="[medium_purple3]Прогресс выполнения работы\n"):
        # Подключение к Telegram и вывод имя аккаунта в консоль / терминал
        client, phone = connect_to_telegram_account_and_output_name(row)
        # Открываем базу данных
        records: list = db_handler.open_and_read_data("writing_group_links")
        print(f"[medium_purple3]Всего групп: {len(records)}")
        for groups in records:  # Поочередно выводим записанные группы
            try:
                groups_wr = subscribe_to_the_group_and_send_the_link(client, groups, phone)
                print(f"[medium_purple3][+] Присоединился к группе или чату {groups_wr}")
                print(f"[magenta][+] Подождите {time_subscription_1}-{time_subscription_2} Секунд...")
                time.sleep(random.randrange(int(time_subscription_1), int(time_subscription_2)))
            except FloodWaitError as e:
                print(f"Flood! wait for {str(datetime.timedelta(seconds=e.seconds))}")
                time.sleep(e.seconds)
        client.disconnect()  # Разрываем соединение Telegram
    app_notifications(notification_text="На группы подписались!")  # Выводим уведомление


def subscribe_to_group_or_channel(client, groups_wr, phone) -> None:
    """Подписываемся на группу или канал"""
    actions: str = "Подписался на группу или чат, если ранее не был подписан"
    event: str = f"Subscription: {groups_wr}"
    description_action = f"channel / group: {groups_wr}"
    # цикл for нужен для того, что бы сработала команда brake
    # команда break в Python используется только для выхода из цикла, а не выхода из программы в целом.
    groups_wra = [groups_wr]
    for groups_wrs in groups_wra:
        try:
            client(JoinChannelRequest(groups_wrs))
            print(f"[magenta] Аккаунт подписался на группу: {groups_wrs}")
            # Записываем данные о действии аккаунта в базу данных
            record_account_actions(phone, description_action, event, actions)
        except ChannelsTooMuchError:
            """Если аккаунт подписан на множество групп и каналов, то отписываемся от них"""
            for dialog in client.iter_dialogs():
                print(f"[magenta]{dialog.name}, {dialog.id}")
                try:
                    client.delete_dialog(dialog)
                    client.disconnect()
                except ConnectionError:
                    break
            print("[magenta][+] Список почистили, и в файл записали.")
        except ChannelPrivateError:
            actions: str = "Указанный канал является приватным, или вам запретили подписываться."
            record_account_actions(phone, description_action, event, actions)
        except (UsernameInvalidError, ValueError, TypeError):
            actions: str = f"Не верное имя или cсылка {groups_wrs} не является группой / каналом: {groups_wrs}"
            record_account_actions(phone, description_action, event, actions)
            db_handler = DatabaseHandler()
            db_handler.write_data_to_db(creating_a_table, writing_data_to_a_table, groups_wrs)
        except PeerFloodError:
            actions: str = "Предупреждение о Flood от Telegram."
            record_account_actions(phone, description_action, event, actions)
            time.sleep(random.randrange(50, 60))
        except FloodWaitError as e:
            actions: str = f"Flood! wait for {str(datetime.timedelta(seconds=e.seconds))}"
            print(f"[red][!] {actions}")
            record_and_interrupt(actions, phone, description_action, event)
            break  # Прерываем работу и меняем аккаунт
        except InviteRequestSentError:
            actions: str = "Действия будут доступны после одобрения администратором на вступление в группу"
            record_account_actions(phone, description_action, event, actions)


def subscribe_to_the_group_and_send_the_link(client, groups, phone):
    """Подписываемся на группу и передаем ссылку"""
    group = {"writing_group_links": groups[0]}
    # Вытягиваем данные из кортежа, для подстановки
    groups_wr = group["writing_group_links"]
    subscribe_to_group_or_channel(client, groups_wr, phone)
    return groups_wr


if __name__ == "__main__":
    subscription_all()
    # writing_group_links_to_file()
