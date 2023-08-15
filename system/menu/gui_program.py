from tkinter import *
import tkinter as tk
from system.menu.baner import program_version, date_of_program_change


def done_button(root, output_values_from_the_input_field):
    """Кнопка готово"""
    # Создаем кнопку по нажатии которой выведется поле ввода. После ввода чатов данные запишутся во временный файл
    but = Button(root, text="Готово", command=output_values_from_the_input_field)
    but.pack()


def program_window_with_dimensions(geometry):
    """Размер окна с геометрией окна"""
    root = tk.Tk()  # Создаем главное окно
    root.title("Telegram_BOT_SMM")
    root.geometry(geometry)  # Устанавливаем размер окна

    return root


def program_window():
    """Создаем графическое окно ввода"""
    root = Tk()  # Создаем программу
    root.title(f"Telegram_BOT_SMM: {program_version} от {date_of_program_change}")
    text = Text(width=50, height=25)  # Создаем окно ввода текста, width=50, height=25 выбираем размер программы
    text.pack()  # Создаем поле ввода

    return root, text


if __name__ == "__main__":
    program_window()
