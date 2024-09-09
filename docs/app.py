from flask import Flask, render_template
import threading
import webbrowser

app = Flask(__name__, template_folder='templates')

@app.route('/')
def index():
    return render_template('index.html')  # Маршрут для главной страницы

@app.route('/menu')
def menu():
    return render_template('menu.html')

@app.route('/inviting')
def inviting():
    return render_template('inviting.html')

@app.route('/sending_messages')
def sending_messages():
    return render_template('sending_messages.html')

@app.route('/editing_bio')
def editing_bio():
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


def run_flask():
    app.run(debug=False, port=8000)

if __name__ == "__main__":
    # Запускаем сервер Flask в отдельном потоке
    threading.Thread(target=run_flask).start()
    # Открываем браузер
    webbrowser.open('http://localhost:8000')
