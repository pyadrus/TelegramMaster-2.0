Для формирования списка пользователей (username), выполните следующие действия:

1. Запустить TelegramMaster (см. [Запуск TelegramMaster](https://github.com/pyadrus/TelegramMaster/blob/be6a5227cc285e000763645563b2d21c600939f6/docs/%D0%9D%D0%B0%D1%81%D1%82%D1%80%D0%BE%D0%B9%D0%BA%D0%B8_%D0%B8_%D0%BA%D0%BE%D0%BD%D1%84%D0%B8%D0%B3%D1%83%D1%80%D0%B0%D1%86%D0%B8%D1%8F/%D0%97%D0%B0%D0%BF%D1%83%D1%81%D0%BA_TelegramMaster.md)).
2. Перейти в раздел «[Настройки](Настройки.md)»
3. Выбрать функцию «[Формирование_списка_username](Формирование_списка_username.md)».
4. В графическое окно программы вставить список username
5. Нажать «Готово»

Список username записывается в базу данных (в файл `TelegramMaster/user_settings/software_database.db` в таблицу **members**)
Если вы уже выполняли [[Парсинг]] ранее, программа добавит username в ранее созданный список (в файл `TelegramMaster/user_settings/software_database.db` в таблицу **members**).
