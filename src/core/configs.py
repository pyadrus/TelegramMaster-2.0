# -*- coding: utf-8 -*-
import configparser

path_accounts_folder = "user_data/accounts"  # Папка для аккаунтов


class ConfigReader:

    def __init__(self):
        self.config = configparser.ConfigParser(empty_lines_in_values=False, allow_no_value=True)
        self.config.read('user_data/config/config.ini', encoding='utf-8')

        self.config_gui = configparser.ConfigParser(empty_lines_in_values=False, allow_no_value=True)
        self.config_gui.read('user_data/config/config_gui.ini', encoding='utf-8')

        self.config_path = configparser.ConfigParser(empty_lines_in_values=False, allow_no_value=True)
        self.config_path.read('user_data/config/config_path.ini', encoding='utf-8')

    def get_config_time_changing_accounts(self):
        """Получение времени смены аккаунтов"""
        return (self.config.get('time_changing_accounts', 'time_changing_accounts_1', fallback=None),
                self.config.get('time_changing_accounts', 'time_changing_accounts_2', fallback=None))

    def get_time_subscription(self):
        return (self.config.getint('time_subscription', 'time_subscription_1', fallback=None),
                self.config.getint('time_subscription', 'time_subscription_2', fallback=None))

    def get_time_inviting(self):
        return (self.config.getint('time_inviting', 'time_inviting_1', fallback=None),
                self.config.getint('time_inviting', 'time_inviting_2', fallback=None))

    def get_limits(self):
        return self.config.getint('account_limits', 'account_limits', fallback=None)

    def get_time_activity_user(self):
        return (self.config.getint('time_activity_user', 'time_activity_user_1', fallback=None),
                self.config.getint('time_activity_user', 'time_activity_user_2', fallback=None))

    def time_activity_user_2(self):
        """   """
        return self.config.get('time_activity_user', 'time_activity_user_2', fallback=None)

    def get_time_sending_messages(self):
        return (self.config.getint('time_sending_messages', 'time_sending_messages_1', fallback=None),
                self.config.getint('time_sending_messages', 'time_sending_messages_2', fallback=None))

    def get_api_id_data_api_hash_data(self):
        return (self.config.get('telegram_settings', 'id', fallback=None),
                self.config.get('telegram_settings', 'hash', fallback=None))

    def get_hour_minutes_every_day(self):
        return (self.config.get('hour_minutes_every_day', 'hour', fallback=None),
                self.config.get('hour_minutes_every_day', 'minutes', fallback=None))

    def get_line_width_button(self) -> str | None:
        """
        Получение ширины кнопки
        """
        return self.config_gui.get('line_width_button', 'line_width_button', fallback=None)

    def get_line_height_button(self) -> str | None:
        """
        Получение высоты кнопки
        """
        return self.config_gui.get('height_button', 'height_button', fallback=None)

    def get_small_button_width(self) -> str | None:
        """
        Получение ширины мало малой кнопки
        """
        return self.config_gui.get('small_button_width', 'small_button_width', fallback=None)

    def line_width(self) -> str | None:
        """
        Ширина окна и ширина строки
        """
        return self.config_gui.get('line_width', 'line_width', fallback=None)

    def program_name(self) -> str | None:
        """
        Имя программы
        """
        return self.config_gui.get('program_name', 'program_name', fallback=None)

    def program_version(self) -> str | None:
        """
        Версия программы
        """
        return self.config_gui.get('program_version', 'program_version', fallback=None)

    def date_of_program_change(self) -> str | None:
        """
        Дата изменения
        """
        return self.config_gui.get('date_of_program_change', 'date_of_program_change', fallback=None)

    def window_width(self) -> str | None:
        """
        Ширина программы
        """
        return self.config_gui.get('window_width', 'window_width', fallback=None)

    def window_height(self) -> str | None:
        """
        Высота программы
        """
        return self.config_gui.get('window_height', 'window_height', fallback=None)

    def window_resizable(self) -> str | None:
        """
        Разрешение на изменение размера программы, если False, то запрещено изменять размер программы
        """
        return self.config_gui.get('window_resizable', 'window_resizable', fallback=None)

    def path_send_message_folder_answering_machine(self) -> str | None:
        """
        Путь к папке для автоответчика (путь к config файлу user_data/config/config_path.ini)
        """
        return self.config_path.get('path_send_message_folder_answering_machine',
                                    'path_send_message_folder_answering_machine', fallback=None)

    def path_send_message_folder_answering_machine_message(self) -> str | None:
        """
        Путь к папке с сообщениями для автоответчика (путь к config файлу user_data/config/config_path.ini)
        """
        return self.config_path.get('path_send_message_folder_answering_machine_message',
                                    'path_send_message_folder_answering_machine_message', fallback=None)

    def path_folder_with_messages(self) -> str | None:
        """
        Путь к папке с сообщениями (путь к config файлу user_data/config/config_path.ini)
        """
        return self.config_path.get('path_folder_with_messages',
                                    'path_folder_with_messages', fallback=None)

    def path_folder_database(self) -> str | None:
        """
        Путь к папке с базой данных (путь к config файлу user_data/config/config_path.ini)
        """
        return self.config_path.get('path_folder_database',
                                    'path_folder_database', fallback=None)


# TODO - Все переменные должны быть с главных буквы
"""Размеры кнопок"""
WIDTH_WIDE_BUTTON = ConfigReader().get_line_width_button()  # Получение ширины широкой кнопки (Широкая кнопка)
BUTTON_HEIGHT = ConfigReader().get_line_height_button()  # Получение ширины кнопки
SMALL_BUTTON_WIDTH = ConfigReader().get_small_button_width()  # Ширина малой кнопки
BUTTON_WIDTH = ConfigReader().line_width()  # Ширина окна и ширина строки

"""Текст для пользователя"""
PROGRAM_NAME = ConfigReader().program_name()  # Имя программы
PROGRAM_VERSION = ConfigReader().program_version()  # Версия программы
DATE_OF_PROGRAM_CHANGE = ConfigReader().date_of_program_change()  # Версия программы

"""Общие размеры программы"""
WINDOW_WIDTH = ConfigReader().window_width()  # Ширина программы
WINDOW_HEIGHT = ConfigReader().window_height()  # Ширина программы
WINDOW_RESIZABLE = ConfigReader().window_resizable()  # Ширина программы

"""Путь к папкам"""
path_send_message_folder_answering_machine = ConfigReader().path_send_message_folder_answering_machine()  # Путь к папке для аккаунтов с автоответчиком
path_send_message_folder_answering_machine_message = ConfigReader().path_send_message_folder_answering_machine_message()  # Путь к папке c сообщениями для автоответчика
path_folder_with_messages = ConfigReader().path_folder_with_messages()  # Путь к папке с сообщениями
path_folder_database = ConfigReader().path_folder_database()  # Путь к папке с базой данных

"""Настройки времени, лимитов и прочего"""
LIMITS = ConfigReader().get_limits()  # Лимиты
time_activity_user_2 = ConfigReader().time_activity_user_2()
time_sending_messages_1, time_sending_messages_2 = ConfigReader().get_time_inviting()  # Время между сообщениями
time_inviting_1, time_inviting_2 = ConfigReader().get_time_inviting()  # Время между инвайтингом, рассылка сообщений
time_changing_accounts_1, time_changing_accounts_2 = ConfigReader().get_config_time_changing_accounts()  # Время смены аккаунтов
time_subscription_1, time_subscription_2 = ConfigReader().get_time_subscription()
