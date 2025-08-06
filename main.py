# -*- coding: utf-8 -*-
import flet as ft
from loguru import logger

from src.core.checking_program import CheckingProgram
from src.core.configs import (PROGRAM_NAME, PROGRAM_VERSION, DATE_OF_PROGRAM_CHANGE, WINDOW_WIDTH,
                              WINDOW_HEIGHT, WINDOW_RESIZABLE, TIME_SENDING_MESSAGES_1, time_sending_messages_2,
                              time_changing_accounts_1, time_changing_accounts_2)
from src.core.sqlite_working_tools import create_database, open_and_read_data
from src.features.account.TGAccountBIO import AccountBIO
from src.features.account.TGChek import TGChek
from src.features.account.TGConnect import TGConnect
from src.features.account.TGContact import TGContact
from src.features.account.TGCreating import CreatingGroupsAndChats
from src.features.account.TGReactions import WorkingWithReactions
from src.features.account.TGSendingMessages import SendTelegramMessages
from src.features.account.TGViewingPosts import ViewingPosts
from src.features.account.inviting import InvitingToAGroup
from src.features.account.parsing.parsing import ParsingGroupMembers
from src.features.account.subscribe_unsubscribe.subscribe_unsubscribe import SubscribeUnsubscribeTelegram
from src.features.auth.logging_in import loging
from src.features.recording.receiving_and_recording import ReceivingAndRecording
from src.features.settings.setting import SettingPage, get_unique_filename, reaction_gui
from src.gui.gui import end_time, start_time
from src.gui.main_menu import main_menu_program
from src.gui.menu import bio_editing_menu, settings_menu, reactions_menu, viewing_posts_menu, working_with_contacts_menu
from src.gui.notification import show_notification

logger.add("user_data/log/log_ERROR.log", rotation="500 KB", compression="zip", level="ERROR")  # Логирование программы


async def main(page: ft.Page):
    """
    Главное меню программы

    Аргументы:
    :param page: Страница интерфейса Flet для отображения элементов управления.
    """
    await loging(page)


    create_database()  # Создание базы данных

    page.title = f"{PROGRAM_NAME}: {PROGRAM_VERSION} (Дата изменения {DATE_OF_PROGRAM_CHANGE})"
    page.window.width = WINDOW_WIDTH  # Ширина окна
    page.window.height = WINDOW_HEIGHT  # Высота окна
    page.window.resizable = WINDOW_RESIZABLE  # Разрешение изменения размера окна

    async def route_change(_):
        page.views.clear()
        # ______________________________________________________________________________________________________________
        await main_menu_program(page=page)  # Главное меню программы
        # ______________________________________________________________________________________________________________
        # try:
        if page.route == "/inviting":  # Меню "🚀 Инвайтинг"
            # TODO миграция на Peewee. вернуть проверку на наличие аккаунтов, username, ссылки на инвайтинг
            await InvitingToAGroup(page=page).inviting_menu()
        # __________________________________________________________________________________________________________
        elif page.route == "/account_verification_menu":  # "Проверка аккаунтов"
            await TGChek(page=page).account_verification_menu()
        # __________________________________________________________________________________________________________
        elif page.route == "/subscribe_unsubscribe":  # Меню "Подписка и отписка"
            await SubscribeUnsubscribeTelegram(page=page).subscribe_and_unsubscribe_menu()
        # __________________________________________________________________________________________________________
        elif page.route == "/working_with_reactions":  # Меню "Работа с реакциями"
            await reactions_menu(page=page)
        elif page.route == "/setting_reactions":  # Ставим реакции
            start = await start_time(page=page)
            logger.info("▶️ Начало Проставления реакций")
            await WorkingWithReactions().send_reaction_request(page=page)
            logger.info("🔚 Конец Проставления реакций")
            await end_time(start, page=page)
        elif page.route == "/automatic_setting_of_reactions":  # Автоматическое выставление реакций
            start = await start_time(page=page)
            logger.info("▶️ Начало Автоматического выставления реакций")
            await WorkingWithReactions().setting_reactions(page=page)
            logger.info("🔚 Конец Автоматического выставления реакций")
            await end_time(start, page=page)
        # __________________________________________________________________________________________________________
        elif page.route == "/viewing_posts_menu":  # Автоматическое выставление просмотров меню
            await viewing_posts_menu(page=page)
        elif page.route == "/we_are_winding_up_post_views":  # ️‍🗨️ Накручиваем просмотры постов
            start = await start_time(page=page)
            logger.info("▶️ Начало Накрутки просмотров постов")
            await ViewingPosts(page=page).viewing_posts_request()
            logger.info("🔚 Конец Накрутки просмотров постов")
            await end_time(start, page=page)
        # __________________________________________________________________________________________________________
        elif page.route == "/parsing":  # Меню "Парсинг"
            await ParsingGroupMembers(page=page).account_selection_menu()
        # __________________________________________________________________________________________________________
        elif page.route == "/importing_a_list_of_parsed_data":  # 📋 Импорт списка от ранее спарсенных данных
            await ReceivingAndRecording().write_data_to_excel(file_name="user_data/parsed_chat_participants.xlsx")
        # __________________________________________________________________________________________________________
        elif page.route == "/working_with_contacts":  # Меню "Работа с контактами"
            await working_with_contacts_menu(page=page)
        elif page.route == "/creating_contact_list":  # Формирование списка контактов
            start = await start_time(page=page)
            logger.info("▶️ Начало Формирования списка контактов")
            open_and_read_data(table_name="contact")  # Удаление списка с контактами
            # TODO миграция на PEEWEE
            await SettingPage(page=page).output_the_input_field(page=page, table_name="contact",
                                                                column_name="contact", route="/working_with_contacts",
                                                                into_columns="contact")
            logger.info("🔚 Конец Формирования списка контактов")
            await end_time(start, page=page)
        elif page.route == "/show_list_contacts":  # Показать список контактов
            start = await start_time(page=page)
            logger.info("▶️ Начало Показа списка контактов")
            await TGContact(page=page).show_account_contact_list()
            logger.info("🔚 Конец Показа списка контактов")
            await end_time(start, page=page)
        elif page.route == "/deleting_contacts":  # Удаление контактов
            start = await start_time(page=page)
            logger.info("▶️ Начало Удаления контактов")
            await TGContact(page=page).delete_contact()
            logger.info("🔚 Конец Удаления контактов")
            await end_time(start, page=page)
        elif page.route == "/adding_contacts":  # Добавление контактов
            start = await start_time(page=page)
            logger.info("▶️ Начало Добавления контактов")
            await TGContact(page=page).inviting_contact()
            logger.info("🔚 Конец Добавления контактов")
            await end_time(start, page=page)
        # __________________________________________________________________________________________________________
        elif page.route == "/account_connection_menu":  # Подключение аккаунтов 'меню'.
            await TGConnect(page=page).account_connection_menu()
        # __________________________________________________________________________________________________________
        elif page.route == "/creating_groups":  # Создание групп (чатов)
            await CreatingGroupsAndChats(page=page).creating_groups_and_chats()
        # __________________________________________________________________________________________________________
        elif page.route == "/sending_messages_files_via_chats":  # Рассылка сообщений по чатам
            await CheckingProgram().check_before_sending_messages_via_chats(page=page)
            await SendTelegramMessages(page=page).sending_messages_files_via_chats()
        elif page.route == "/sending_files_to_personal_account_with_limits":  # Отправка сообщений в личку
            await SendTelegramMessages(page=page).send_files_to_personal_chats()
        # __________________________________________________________________________________________________________
        elif page.route == "/bio_editing":  # Меню "Редактирование_BIO"
            await bio_editing_menu(page=page)
        elif page.route == "/edit_description":  # Изменение описания
            await AccountBIO().change_bio_profile_gui(page=page)
        elif page.route == "/name_change":  # Изменение имени профиля Telegram
            await AccountBIO().change_name_profile_gui(page=page)
        elif page.route == "/change_surname":  # Изменение фамилии
            await AccountBIO().change_last_name_profile_gui(page=page)
        elif page.route == "/edit_photo":  # Изменение фото
            await AccountBIO().change_photo_profile_gui(page=page)
            await show_notification(page=page, message="🔚 Фото изменено")  # Выводим уведомление пользователю
        elif page.route == "/changing_username":  # Изменение username
            await AccountBIO().change_username_profile_gui(page=page)
        # __________________________________________________________________________________________________________
        elif page.route == "/settings":  # Меню "Настройки TelegramMaster"
            await settings_menu(page=page)
        elif page.route == "/recording_api_id_api_hash":  # Запись api_id, api_hash
            await SettingPage(page=page).writing_api_id_api_hash(page=page)
        elif page.route == "/message_limits":  # Лимиты на сообщения
            await SettingPage(page=page).record_setting( "message_limits", "Введите лимит на сообщения")
        elif page.route == "/creating_username_list":  # Формирование списка username
            await SettingPage(page=page).output_the_input_field(page, "members",
                                                                "username, id, access_hash, first_name, last_name, "
                                                                "user_phone, online_at, photos_id, user_premium",
                                                                "/settings", "members (username)")
        elif page.route == "/forming_list_of_chats_channels":  # Формирование списка чатов / каналов
            await SettingPage(page=page).output_the_input_field(page, "writing_group_links", "writing_group_links",
                                                                "/settings", "writing_group_links")
        elif page.route == "/proxy_entry":  # Запись proxy
            await SettingPage(page=page).creating_the_main_window_for_proxy_data_entry()
        elif page.route == "/message_recording":  # Запись сообщений
            await SettingPage(page=page).recording_text_for_sending_messages(page, "Введите текст для сообщения",
                                                                             get_unique_filename(
                                                                                 base_filename='user_data/message/message'))
        elif page.route == "/recording_reaction_link":  # Запись ссылки для реакций
            await SettingPage(page=page).recording_text_for_sending_messages(page, "Введите ссылку для реакций",
                                                                             'user_data/reactions/link_channel.json')
        elif page.route == "/choice_of_reactions":  # Выбор реакций
            await reaction_gui(page=page)
        elif page.route == "/recording_the_time_between_messages":  # Запись времени между сообщениями

            await SettingPage(page=page).create_main_window(variable="time_sending_messages",
                                                            time_range=[TIME_SENDING_MESSAGES_1,
                                                                        time_sending_messages_2])
        elif page.route == "/changing_accounts":  # Смена аккаунтов
            await SettingPage(page=page).create_main_window(variable="time_changing_accounts",
                                                            time_range=[time_changing_accounts_1,
                                                                        time_changing_accounts_2])

        page.update()

    def view_pop(_):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)


if __name__ == '__main__':

    ft.app(target=main)
