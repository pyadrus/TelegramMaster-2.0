import configparser
from rich.console import Console

console = Console()
config = configparser.ConfigParser(empty_lines_in_values=False, allow_no_value=True)

config.read('setting_user/config.ini')
link_group = config['link_to_the_group']['target_group_entity']

time_subscription_1 = int(config['time_subscription']['time_subscription_1'])
time_subscription_2 = int(config['time_subscription']['time_subscription_2'])

time_inviting_1 = int(config['time_inviting']['time_inviting_1'])
time_inviting_2 = int(config['time_inviting']['time_inviting_2'])

time_changing_accounts_1 = int(config['time_changing_accounts']['time_changing_accounts_1'])
time_changing_accounts_2 = int(config['time_changing_accounts']['time_changing_accounts_2'])

limits = int(config['account_limits']['limits'])
