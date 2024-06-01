# def subscribe_unsubscribe_write_to_file() -> None:  # 4 - Подписка, отписка, запись в файл групп
#     """Подписка, отписка, запись в файл групп"""
#     clear_console_and_display_banner()  # Чистим консоль, выводим банер
#     table = Table(title="[medium_purple3]Подписываемся / отписываемся!", box=box.HORIZONTALS)  # Выводим таблицу
#     column_names(table)  # Формируем колонки таблицы
#     # Выводим текст в таблице
#     table.add_row("1", "Подписка")
#     table.add_row("2", "Отписываемся")
#     table.add_row("0", "Вернуться назад")
#     console.print(table, justify="left")  # Отображаем таблицу
#     user_input = console.input("[medium_purple3][+] Введите номер: ")
#     clear_console_and_display_banner()  # Чистим консоль, выводим банер
#     if user_input == "1":  # Запись: групп, каналов в файл, в файл user_settings/software_database.db
#         subscription_all(DatabaseHandler())
#     elif user_input == "2":  # Отписываемся от групп / каналов (работа с несколькими аккаунтами)
#         unsubscribe_all(DatabaseHandler())
#     elif user_input == "0":  # Вернуться назад
#         main_menu()  # После отработки функции переходим в начальное меню
#     else:
#         subscribe_unsubscribe_write_to_file()
#     main_menu()  # После отработки функции переходим в начальное меню
#
#
# def personal_account_chat_messages_distribution() -> None:  # 6 - Рассылка сообщений в личку
#     """Рассылка сообщений в личку"""
#     clear_console_and_display_banner()  # Чистим консоль, выводим банер
#     table = Table(title="[medium_purple3]Рассылка сообщений в личку!", box=box.HORIZONTALS)  # Выводим таблицу
#     column_names(table)  # Формируем колонки таблицы
#     # Выводим текст в таблице
#     table.add_row("1", "Отправка сообщений в личку")
#     table.add_row("2", "Отправка файлов в личку")
#     table.add_row("3", "Рассылка сообщений по чатам")
#     table.add_row("4", "Рассылка сообщений по чатам с автоответчиком")
#     table.add_row("5", "Рассылка файлов по чатам")
#     table.add_row("6", "Рассылка сообщений + файлов по чатам")
#     table.add_row("7", "Отправка сообщений в личку (с лимитами)")
#     table.add_row("8", "Отправка файлов в личку (с лимитами)")
#     table.add_row("0", "В начальное меню")
#     console.print(table, justify="left")  # Отображаем таблицу
#     user_input = console.input("[medium_purple3][+] Введите номер: ")
#     clear_console_and_display_banner()  # Чистим консоль, выводим банер
#     if user_input == "1":  # Отправка сообщений в личку
#         send_message_from_all_accounts(limits=None, db_handler=DatabaseHandler())
#     elif user_input == "2":  # Отправка файлов в личку
#         send_files_to_personal_chats(limits=None, db_handler=DatabaseHandler())
#     elif user_input == "3":  # Рассылка сообщений по чатам
#         entities = find_files(directory_path="user_settings/message", extension="json")
#         logger.info(entities)
#         sending_messages_via_chats_times(entities, DatabaseHandler())
#     elif user_input == "4":  # ✅ Рассылка сообщений по чатам по времени
#         mains(DatabaseHandler())
#     elif user_input == "5":  # Рассылка файлов по чатам
#         sending_files_via_chats(DatabaseHandler())
#     elif user_input == "6":  # Рассылка сообщений + файлов по чатам
#         sending_messages_files_via_chats()
#     elif user_input == "7":  # Отправка сообщений в личку (с лимитами)
#         send_message_from_all_accounts(limits=limits_message, db_handler=DatabaseHandler())
#     elif user_input == "8":  # Отправка файлов в личку (с лимитами)
#         send_files_to_personal_chats(limits=limits_message, db_handler=DatabaseHandler())
#     elif user_input == "0":  # Вернуться назад
#         main_menu()  # После отработки функции переходим в начальное меню
#     else:
#         personal_account_chat_messages_distribution()
#
#
# def working_with_the_reaction() -> None:  # 7 - Работа с реакциями на посты группы или канала
#     """Работа с реакциями на посты группы или канала"""
#     clear_console_and_display_banner()  # Чистим консоль, выводим банер
#     table = Table(title="[medium_purple3]Работа с реакциями / постами!", box=box.HORIZONTALS)  # Выводим таблицу
#     column_names(table)  # Формируем колонки таблицы
#     # Выводим текст в таблице
#     table.add_row("1", "Ставим реакции")
#     table.add_row("2", "Накручиваем просмотры постов")
#     table.add_row("3", "Автоматическое выставление реакций")
#     table.add_row("0", "Вернуться назад")
#     console.print(table, justify="left")  # Отображаем таблицу
#     user_input = console.input("[medium_purple3][+] Введите номер: ")
#     clear_console_and_display_banner()  # Чистим консоль, выводим банер
#     if user_input == "1":  # Ставим реакции на один пост в группе / канале
#         reaction_worker = WorkingWithReactions(DatabaseHandler())  # Создаем экземпляр класса WorkingWithReactions
#         reaction_worker.users_choice_of_reaction()  # Вызываем метод для выбора реакции и установки её на сообщение
#     elif user_input == "2":  # Накручиваем просмотры постов
#         viewing_posts(DatabaseHandler())
#     elif user_input == "3":
#         setting_reactions(DatabaseHandler())  # Автоматическое выставление реакций
#     elif user_input == "0":  # Вернуться назад
#         main_menu()  # После отработки функции переходим в начальное меню
#     else:
#         working_with_the_reaction()
#     main_menu()  # После отработки функции переходим в начальное меню
#
#
# if __name__ == "__main__":
#     try:
#         main_menu()
#     except Exception as e:
#         logger.exception(e)
#         print("[medium_purple3][!] Произошла ошибка, для подробного изучения проблемы просмотрите файл log.log")
