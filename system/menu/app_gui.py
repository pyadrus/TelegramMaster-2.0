from tkinter import *

from system.menu.app_banner import program_version, date_of_program_change


def create_window(page, width, height, resizable):
    """
    Создание окна flet https://flet.dev/docs/
    :param page: Page для создания окна
    :param width: ширина окна (по умолчанию 600)
    :param height: высота окна (по умолчанию 600)
    :param resizable: Запрет на изменение размера окна (True/False)
    """
    page.window_width = width  # ширина окна
    page.window_height = height  # высота окна
    page.window_resizable = resizable  # Запрет на изменение размера окна


def done_button(root, output_values_from_the_input_field) -> None:
    """Кнопка готово"""
    # Создаем кнопку по нажатии которой выведется поле ввода. После ввода чатов данные запишутся во временный файл
    but = Button(root, text="Готово", command=output_values_from_the_input_field)
    but.pack()


def program_window():
    """Создаем графическое окно ввода"""
    root = Tk()  # Создаем программу
    root.title(f"Telegram_BOT_SMM: {program_version} от {date_of_program_change}")
    text = Text(width=50, height=25)  # Создаем окно ввода текста, width=50, height=25 выбираем размер программы
    text.pack()  # Создаем поле ввода

    return root, text


if __name__ == "__main__":
    program_window()
