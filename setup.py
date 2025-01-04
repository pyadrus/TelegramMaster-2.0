import os

os.system("""pip install -r requirements.txt""")

# Список всех необходимых директорий
directories = [
    'user_data/accounts/answering_machine',
    'user_data/accounts/banned',
    'user_data/accounts/bio',
    'user_data/accounts/contact',
    'user_data/accounts/creating',
    'user_data/accounts/inviting',
    'user_data/accounts/parsing',
    'user_data/accounts/reactions',
    'user_data/accounts/reactions_list',
    'user_data/accounts/send_message',
    'user_data/accounts/subscription',
    'user_data/accounts/unsubscribe',
    'user_data/accounts/viewing'
]

for directory in directories:
    try:
        # Создаём директорию с возможностью игнорирования ошибки существования
        os.makedirs(directory, exist_ok=True)
        print(f"Папка '{directory}' создана")
    except OSError as e:
        print(f"❌ Ошибка создания папки '{directory}': {e}")
