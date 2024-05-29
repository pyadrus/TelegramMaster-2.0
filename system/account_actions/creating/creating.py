import flet as ft  # Импортируем библиотеку flet
from loguru import logger
from telethon import functions

from system.sqlite_working_tools.sqlite_working_tools import select_from_config_by_phone, DatabaseHandler
from system.telegram_actions.telegram_actions import telegram_connect_and_output_name


def creating_groups_and_chats(page: ft.Page, records, db_handler) -> None:
    """Создание групп (чатов) в автоматическом режиме"""

    phones = [rows[0] for rows in records]  # Извлечение номеров телефонов из списка учетных записей

    result = select_from_config_by_phone(phones)
    logger.info(result)

    t = ft.Text(
        value='Выберите Telegram аккаунт, в котором будут создаваться группы (чаты): ')  # Создает текстовое поле.

    # Создаем список чекбоксов для каждого аккаунта
    checkboxes = []
    for row in result:
        phone = row[0]  # Предполагая, что первый элемент в строке - это номер телефона
        checkboxes.append(ft.Checkbox(label=phone))

    def button_clicked(e):
        """Выбранная реакция"""

        selected_account = None
        for checkbox in checkboxes:
            if checkbox.value:  # Проверяет, отмечен ли чекбокс.
                selected_account = checkbox.label  # Получаем номер телефона из метки чекбокса
                break

        if selected_account:
            row = next(row for row in result if row[0] == selected_account)
            # Подключение к Telegram и вывод имени аккаунта в консоль / терминал
            client, phone = telegram_connect_and_output_name(row, db_handler)
            # Создаем группу (чат) в выбранном аккаунте
            response = client(functions.channels.CreateChannelRequest(
                title='My awesome title',
                about='Description for your group',
                megagroup=True
            ))
            print(response.stringify())

        page.go("/settings")  # Изменение маршрута в представлении существующих настроек

    # Кнопка "Готово" и связывает ее с функцией button_clicked.
    button = ft.ElevatedButton("Готово", on_click=button_clicked)

    # Добавляем чекбоксы и кнопку на страницу
    page.views.append(
        ft.View(
            "/settings",
            controls=[
                t,  # Добавляет текстовое поле t на страницу.
                ft.Column(checkboxes),  # Добавляет все чекбоксы на страницу в виде колонок.
                button,  # Добавляет кнопку на страницу.
            ]
        )
    )
