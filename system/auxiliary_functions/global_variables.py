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
        return self.config.get('link_to_the_group', 'link_to_the_group', fallback=None)

    def get_time_subscription(self):
        return (self.config.getint('time_subscription', 'time_subscription_1', fallback=None),
                self.config.getint('time_subscription', 'time_subscription_2', fallback=None))

    def get_time_inviting(self):
        return (self.config.getint('time_inviting', 'time_inviting_1', fallback=None),
                self.config.getint('time_inviting', 'time_inviting_2', fallback=None))

    def get_time_changing_accounts(self):
        return (self.config.getint('time_changing_accounts', 'time_changing_accounts_1', fallback=None),
                self.config.getint('time_changing_accounts', 'time_changing_accounts_2', fallback=None))

    def get_limits(self):
        return self.config.getint('account_limits', 'account_limits', fallback=None)

    def get_message_limits(self):
        return self.config.getint('message_limits', 'message_limits', fallback=None)

    def get_time_activity_user(self):
        return (self.config.getint('time_activity_user', 'time_activity_user_1', fallback=None),
                self.config.getint('time_activity_user', 'time_activity_user_2', fallback=None))

    def get_time_sending_messages(self):
        return (self.config.getint('time_sending_messages', 'time_sending_messages_1', fallback=None),
                self.config.getint('time_sending_messages', 'time_sending_messages_2', fallback=None))

    def get_api_id_data_api_hash_data(self):
        return (self.config.get('telegram_settings', 'id', fallback=None),
                self.config.get('telegram_settings', 'hash', fallback=None))

    def get_device_model(self):
        return (self.config.get('device_model', 'device_model', fallback=None),
                self.config.get('system_version', 'system_version', fallback=None),
                self.config.get('app_version', 'app_version', fallback=None))

    def get_hour_minutes_every_day(self):
        return (self.config.get('hour_minutes_every_day', 'hour', fallback=None),
                self.config.get('hour_minutes_every_day', 'minutes', fallback=None))


# Пример использования
config_reader = ConfigReader()
