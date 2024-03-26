from tkinter import *
import flet as ft
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


def output_the_input_field(db_handler) -> None:
    """Выводим ссылки в поле ввода поле ввода для записи ссылок групп"""

    def main_inviting(page) -> None:
        create_window(page=page, width=600, height=600, resizable=False)  # Создаем окно с размером 600 на 600 пикселей
        text_to_send = ft.TextField(label="Введите список ссылок на группы", multiline=True, max_lines=19)
        greetings = ft.Column()

        def btn_click(e) -> None:
            page.update()
            print(f"Вы ввели: {text_to_send}")
            db_handler.open_and_read_data("writing_group_links")  # Удаление списка с группами
            db_handler.write_to_single_column_table(name_database="writing_group_links",
                                                    database_columns="writing_group_links",
                                                    into_columns="writing_group_links",
                                                    recorded_data=text_to_send.value.split())
            page.window_close()

        page.add(text_to_send, ft.ElevatedButton("Готово", on_click=btn_click), greetings, )

    ft.app(target=main_inviting)


def writing_members(db_handler) -> None:
    """Запись username в software_database.db в графическое окно Flet"""

    def main_inviting(page) -> None:
        create_window(page=page, width=600, height=600, resizable=False)  # Создаем окно с размером 600 на 600 пикселей
        text_to_send = ft.TextField(label="Введите список username", multiline=True, max_lines=19)
        greetings = ft.Column()

        def btn_click(e) -> None:
            page.update()
            print(f"Вы ввели: {text_to_send}")
            db_handler.write_to_single_column_table(name_database="members",
                                                    database_columns="username, id, access_hash, first_name, last_name, "
                                                                     "user_phone, online_at, photos_id, user_premium",
                                                    into_columns="members (username)",
                                                    recorded_data=text_to_send.value.split())

            page.window_close()

        page.add(text_to_send, ft.ElevatedButton("Готово", on_click=btn_click), greetings, )

    ft.app(target=main_inviting)


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
