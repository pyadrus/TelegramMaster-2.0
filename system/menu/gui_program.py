from tkinter import *

from system.menu.baner import program_version, date_of_program_change


def program_window():
    """Создаем графическое окно ввода"""

    root = Tk()  # Создаем программу
    root.title(f"Telegram_BOT_SMM: {program_version} от {date_of_program_change}")
    # Создаем окно ввода текста, width=50, height=25 выбираем размер программы
    text = Text(width=50, height=25)
    text.pack()  # Создаем поле ввода

    return root, text


if __name__ == "__main__":
    program_window()
