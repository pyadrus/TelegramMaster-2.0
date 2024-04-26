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
config = configparser.ConfigParser(empty_lines_in_values=False, allow_no_value=True)

config.read('user_settings/config.ini')
link_group = config['link_to_the_group']['target_group_entity']

time_subscription_1 = int(config['time_subscription']['time_subscription_1'])
time_subscription_2 = int(config['time_subscription']['time_subscription_2'])

time_inviting_1 = int(config['time_inviting']['time_inviting_1'])
time_inviting_2 = int(config['time_inviting']['time_inviting_2'])

time_changing_accounts_1 = int(config['time_changing_accounts']['time_changing_accounts_1'])
time_changing_accounts_2 = int(config['time_changing_accounts']['time_changing_accounts_2'])

limits = int(config['account_limits']['limits'])

limits_message = int(config['message_limits']['message_limits'])

time_activity_user_1 = int(config['time_activity_user']['time_activity_user_1'])
time_activity_user_2 = int(config['time_activity_user']['time_activity_user_2'])

time_sending_messages_1 = int(config['time_sending_messages']['time_sending_messages_1'])
time_sending_messages_2 = int(config['time_sending_messages']['time_sending_messages_2'])

api_id_data = config["telegram_settings"]["id"]  # api_id с файла user_settings/config.ini
api_hash_data = config["telegram_settings"]["hash"]  # api_hash с файла user_settings/config.ini

device_model = config["device_model"]["device_model"]  # api_id с файла user_settings/config.ini
system_version = config["system_version"]["system_version"]  # api_hash с файла user_settings/config.ini
app_version = config["app_version"]["app_version"]  # api_hash с файла user_settings/config.ini

hour = config["hour_minutes_every_day"]["hour"]  # api_id с файла user_settings/config.ini
minutes = config["hour_minutes_every_day"]["minutes"]  # api_hash с файла user_settings/config.ini

account_name_newsletter = config["account_name_newsletter"]["account_name_newsletter"]
