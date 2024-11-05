import os

os.system("""pip install -r requirements.txt""")


# Список всех необходимых директорий
directories = [
    'user_settings/accounts/answering_machine',
    'user_settings/accounts/banned',
    'user_settings/accounts/bio',
    'user_settings/accounts/contact',
    'user_settings/accounts/creating',
    'user_settings/accounts/inviting',
    'user_settings/accounts/parsing',
    'user_settings/accounts/reactions',
    'user_settings/accounts/reactions_list',
    'user_settings/accounts/send_message',
    'user_settings/accounts/subscription',
    'user_settings/accounts/unsubscribe',
    'user_settings/accounts/viewing'
]

for directory in directories:
    try:
        # Создаём директорию с возможностью игнорирования ошибки существования
        os.makedirs(directory, exist_ok=True)
        print(f"Папка '{directory}' создана")
    except OSError as e:
        print(f"Ошибка создания папки '{directory}': {e}")