# -*- coding: utf-8 -*-
import openpyxl

from src.core.sqlite_working_tools import DatabaseHandler


class ReceivingAndRecording:

    def __init__(self):
        self.db_handler = DatabaseHandler()

    async def write_data_to_excel(self, file_name):
        """
        Запись данных в Excel файл.
        :param file_name: Имя файла для сохранения данных
        """
        workbook = openpyxl.Workbook()  # Создание новой рабочей книги
        sheet = workbook.active
        sheet.title = "Chat Participants"
        # Заголовки столбцов
        sheet.append(
            ["username", "id", "access_hash", "first_name", "last_name", "user_phone", "online_at", "photos_id",
             "user_premium"]
            )
        for row in await self.db_handler.read_parsed_chat_participants_from_db():
            sheet.append(row)  # Запись данных
        workbook.save(file_name)  # Сохранение файла
