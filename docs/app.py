from flask import Flask, render_template

app = Flask(__name__, template_folder='templates')


@app.route('/')
def index():
    return render_template('index.html')  # Маршрут для главной страницы


@app.route('/menu')
def menu():
    """Меню программы"""
    # Версия и дата обновления
    program_version = "2.1.7"
    update_date = "09.09.2024"
    return render_template('menu.html', program_version=program_version, update_date=update_date)


@app.route('/inviting')
def inviting():
    """Инвайтинг"""
    return render_template('inviting.html')


@app.route('/sending_messages')
def sending_messages():
    """Рассылка сообщений"""
    return render_template('sending_messages.html')


@app.route('/editing_bio')
def editing_bio():
    """Редактирование БИЛ"""
    return render_template('editing_bio.html')


@app.route('/working_with_contacts')
def working_with_contacts():
    """Работа с контактами"""
    return render_template('working_with_contacts.html')


@app.route('/settings')
def settings():
    """Настройки"""
    return render_template('settings.html')


@app.route('/working_with_reactions')
def working_with_reactions():
    """Работа с реакциями"""
    return render_template('working_with_reactions.html')


@app.route('/parsing')
def parsing():
    """Парсинг"""
    return render_template('parsing.html')


@app.route('/subscribe_unsubscribe')
def subscribe_unsubscribe():
    """Подписка, отписка"""
    return render_template('subscribe_unsubscribe.html')


@app.route('/connect_accounts')
def connect_accounts():
    """Подключение аккаунтов"""
    return render_template('connect_accounts.html')


@app.route('/account_verification')
def account_verification():
    """Проверка аккаунтов"""
    return render_template('account_verification.html')


@app.route('/creating_groups')
def creating_groups():
    """Создание групп (чатов)"""
    return render_template('creating_groups.html')

@app.route('/launch_telegrammaster')
def launch_telegrammaster():
    """Запуск TelegramMaster"""
    return render_template('launch_telegrammaster.html')

def run_flask():
    app.run(debug=True, port=8000)


if __name__ == "__main__":
    run_flask()
