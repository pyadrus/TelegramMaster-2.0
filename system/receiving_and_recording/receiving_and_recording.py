# -*- coding: utf-8 -*-
import openpyxl

from system.sqlite_working_tools.sqlite_working_tools import DatabaseHandler


class ReceivingAndRecording:

    def __init__(self):
        self.db_handler = DatabaseHandler()

    async def write_data_to_excel(self, file_name):
        """
        Запись данных в Excel файл.

        Аргументы:
        :param file_name: Имя файла для сохранения данных
        """
        data = await self.db_handler.read_parsed_chat_participants_from_db()

        # Создание новой рабочей книги
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "Chat Participants"

        # Заголовки столбцов
        headers = ["username", "id", "access_hash", "first_name", "last_name", "user_phone", "online_at", "photos_id",
                   "user_premium"]
        sheet.append(headers)

        # Запись данных
        for row in data:
            sheet.append(row)

        # Сохранение файла
        workbook.save(file_name)
