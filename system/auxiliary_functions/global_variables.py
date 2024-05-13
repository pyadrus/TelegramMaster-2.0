import configparser
from rich.console import Console
from loguru import logger

logger.add("user_settings/log/log.log", rotation="1 MB", compression="zip")  # Логирование программы

# Создаем логгер для информационных сообщений с [deadly] в сообщении
logger_info = logger.bind()
# Обработчик для информационных сообщений с [deadly] в сообщении
logger_info.add('user_settings/log/info.log', filter=lambda record: '[deadly]' in record['message'],
                format="{time:YYYY-MM-DD HH:mm:ss} | {message}")

console = Console()


class ConfigReader:
    def __init__(self):
        self.config = configparser.ConfigParser(empty_lines_in_values=False, allow_no_value=True)
        self.config.read('user_settings/config.ini')

    def get_link_group(self):
        link_group = self.config['link_to_the_group']['target_group_entity']
        return link_group

    def get_time_subscription(self):
        time_subscription_1 = int(self.config['time_subscription']['time_subscription_1'])
        time_subscription_2 = int(self.config['time_subscription']['time_subscription_2'])
        return time_subscription_1, time_subscription_2

    def get_time_inviting(self):
        time_inviting_1 = int(self.config['time_inviting']['time_inviting_1'])
        time_inviting_2 = int(self.config['time_inviting']['time_inviting_2'])
        return time_inviting_1, time_inviting_2

    def get_time_changing_accounts(self):
        time_changing_accounts_1 = int(self.config['time_changing_accounts']['time_changing_accounts_1'])
        time_changing_accounts_2 = int(self.config['time_changing_accounts']['time_changing_accounts_2'])
        return time_changing_accounts_1, time_changing_accounts_2

    def get_limits(self):
        limits = int(self.config['account_limits']['limits'])
        return limits

    def get_message_limits(self):
        limits_message = int(self.config['message_limits']['message_limits'])
        return limits_message

    def get_time_activity_user(self):
        time_activity_user_1 = int(self.config['time_activity_user']['time_activity_user_1'])
        time_activity_user_2 = int(self.config['time_activity_user']['time_activity_user_2'])
        return time_activity_user_1, time_activity_user_2

    def get_time_sending_messages(self):
        time_sending_messages_1 = int(self.config['time_sending_messages']['time_sending_messages_1'])
        time_sending_messages_2 = int(self.config['time_sending_messages']['time_sending_messages_2'])
        return time_sending_messages_1, time_sending_messages_2

    def get_api_id_data_api_hash_data(self):
        api_id_data = self.config["telegram_settings"]["id"]  # api_id с файла user_settings/config.ini
        api_hash_data = self.config["telegram_settings"]["hash"]  # api_hash с файла user_settings/config.ini
        return api_id_data, api_hash_data

    def get_device_model(self):
        device_model = self.config["device_model"]["device_model"]  # api_id с файла user_settings/config.ini
        system_version = self.config["system_version"]["system_version"]  # api_hash с файла user_settings/config.ini
        app_version = self.config["app_version"]["app_version"]  # api_hash с файла user_settings/config.ini
        return device_model, system_version, app_version

    def get_hour_minutes_every_day(self):
        hour = self.config["hour_minutes_every_day"]["hour"]  # api_id с файла user_settings/config.ini
        minutes = self.config["hour_minutes_every_day"]["minutes"]  # api_hash с файла user_settings/config.ini
        return hour, minutes

    def get_account_name_newsletter(self):
        account_name_newsletter = self.config["account_name_newsletter"]["account_name_newsletter"]
        return account_name_newsletter
