from quart import Quart, render_template
import asyncio

app = Quart(__name__, template_folder='templates')


@app.route('/')
async def index():
    return await render_template('index.html')  # Маршрут для главной страницы


@app.route('/menu')
async def menu():
    """Меню программы"""
    # Версия и дата обновления
    program_version = "2.1.7"
    update_date = "09.09.2024"
    return await render_template('menu.html', program_version=program_version, update_date=update_date)


@app.route('/inviting')
async def inviting():
    """Инвайтинг"""
    return await render_template('inviting.html')


@app.route('/sending_messages')
async def sending_messages():
    """Рассылка сообщений"""
    return await render_template('sending_messages.html')


@app.route('/editing_bio')
async def editing_bio():
    """Редактирование БИЛ"""
    return await render_template('editing_bio.html')


@app.route('/working_with_contacts')
async def working_with_contacts():
    """Работа с контактами"""
    return await render_template('working_with_contacts.html')


@app.route('/settings')
async def settings():
    """Настройки"""
    return await render_template('settings.html')


@app.route('/working_with_reactions')
async def working_with_reactions():
    """Работа с реакциями"""
    return await render_template('working_with_reactions.html')


@app.route('/parsing')
async def parsing():
    """Парсинг"""
    return await render_template('parsing.html')


@app.route('/subscribe_unsubscribe')
async def subscribe_unsubscribe():
    """Подписка, отписка"""
    return await render_template('subscribe_unsubscribe.html')


@app.route('/connect_accounts')
async def connect_accounts():
    """Подключение аккаунтов"""
    return await render_template('connect_accounts.html')


@app.route('/account_verification')
async def account_verification():
    """Проверка аккаунтов"""
    return await render_template('account_verification.html')


@app.route('/creating_groups')
async def creating_groups():
    """Создание групп (чатов)"""
    return await render_template('creating_groups.html')


@app.route('/launch_telegrammaster')
async def launch_telegrammaster():
    """Запуск TelegramMaster"""
    return await render_template('launch_telegrammaster.html')


# def run_flask():
#     app.run(debug=True, port=8000)


# if __name__ == "__main__":
#     run_flask()
