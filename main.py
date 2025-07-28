# -*- coding: utf-8 -*-
import asyncio

import flet as ft
from loguru import logger

from src.core.checking_program import CheckingProgram
from src.core.configs import (PROGRAM_NAME, PROGRAM_VERSION, DATE_OF_PROGRAM_CHANGE, WINDOW_WIDTH,
                              WINDOW_HEIGHT, WINDOW_RESIZABLE, time_sending_messages_1, time_sending_messages_2,
                              time_inviting_1, time_inviting_2, time_changing_accounts_1, time_changing_accounts_2,
                              time_subscription_1, time_subscription_2)
from src.core.sqlite_working_tools import create_database, open_and_read_data
from src.features.account.TGAccountBIO import AccountBIO
from src.features.account.TGChek import TGChek
from src.features.account.TGConnect import TGConnect
from src.features.account.TGContact import TGContact
from src.features.account.TGCreating import CreatingGroupsAndChats
from src.features.account.TGReactions import WorkingWithReactions
from src.features.account.TGSendingMessages import SendTelegramMessages
from src.features.account.TGSubUnsub import SubscribeUnsubscribeTelegram
from src.features.account.TGViewingPosts import ViewingPosts
from src.features.account.inviting.inviting import InvitingToAGroup
from src.features.account.parsing.parsing import ParsingGroupMembers
from src.features.auth.logging_in import loging
from src.features.recording.receiving_and_recording import ReceivingAndRecording
from src.features.settings.setting import SettingPage, get_unique_filename, reaction_gui
from src.gui.gui import end_time, start_time
from src.gui.main_menu import main_menu_program
from src.gui.menu import (bio_editing_menu, settings_menu, reactions_menu,
                          viewing_posts_menu, working_with_contacts_menu)
from src.gui.notification import show_notification

logger.add("user_data/log/log_ERROR.log", rotation="500 KB", compression="zip", level="ERROR")  # Логирование программы


async def main(page: ft.Page):
    """
    Главное меню программы

    Аргументы:
    :param page: Страница интерфейса Flet для отображения элементов управления.
    """
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
        try:
            if page.route == "/inviting":  # Меню "🚀 Инвайтинг"
                # TODO миграция на Peewee. вернуть проверку на наличие аккаунтов, username, ссылки на инвайтинг
                # await CheckingProgram().check_before_inviting(page=page)
                await InvitingToAGroup().inviting_menu(page=page)
            # __________________________________________________________________________________________________________
            elif page.route == "/account_verification_menu":  # "Проверка аккаунтов"
                await TGChek().account_verification_menu(page=page)
            # __________________________________________________________________________________________________________
            elif page.route == "/subscribe_unsubscribe":  # Меню "Подписка и отписка"
                await SubscribeUnsubscribeTelegram().subscribe_and_unsubscribe_menu(page=page)
            # elif page.route == "/subscription_all":  # Подписка
            #     await SubscribeUnsubscribeTelegram().subscribe_telegram(page=page)
            # elif page.route == "/unsubscribe_all":  # Отписываемся
            #     start = await start_time(page=page)
            #     logger.info("▶️ Начало Отписка")
            #     await SubscribeUnsubscribeTelegram().unsubscribe_all(page=page)
            #     logger.info("🔚 Конец Отписки")
            #     await end_time(start, page=page)
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
                await ViewingPosts().viewing_posts_request(page=page)
                logger.info("🔚 Конец Накрутки просмотров постов")
                await end_time(start, page=page)
            # __________________________________________________________________________________________________________
            elif page.route == "/parsing":  # Меню "Парсинг"
                await ParsingGroupMembers().account_selection_menu(page=page)
            elif page.route == "/importing_a_list_of_parsed_data":  # 📋 Импорт списка от ранее спарсенных данных
                await ReceivingAndRecording().write_data_to_excel(file_name="user_data/parsed_chat_participants.xlsx")
            # __________________________________________________________________________________________________________
            elif page.route == "/working_with_contacts":  # Меню "Работа с контактами"
                await working_with_contacts_menu(page=page)
            elif page.route == "/creating_contact_list":  # Формирование списка контактов
                start = await start_time(page=page)
                logger.info("▶️ Начало Формирования списка контактов")
                open_and_read_data(table_name="contact", page=page)  # Удаление списка с контактами
                # TODO миграция на PEEWEE
                await SettingPage().output_the_input_field(page=page, table_name="contact",
                                                           column_name="contact", route="/working_with_contacts",
                                                           into_columns="contact")
                logger.info("🔚 Конец Формирования списка контактов")
                await end_time(start, page=page)
            elif page.route == "/show_list_contacts":  # Показать список контактов
                start = await start_time(page=page)
                logger.info("▶️ Начало Показа списка контактов")
                await TGContact().show_account_contact_list(page=page)
                logger.info("🔚 Конец Показа списка контактов")
                await end_time(start, page=page)
            elif page.route == "/deleting_contacts":  # Удаление контактов
                start = await start_time(page=page)
                logger.info("▶️ Начало Удаления контактов")
                await TGContact().delete_contact(page=page)
                logger.info("🔚 Конец Удаления контактов")
                await end_time(start, page=page)
            elif page.route == "/adding_contacts":  # Добавление контактов
                start = await start_time(page=page)
                logger.info("▶️ Начало Добавления контактов")
                await TGContact().inviting_contact(page=page)
                logger.info("🔚 Конец Добавления контактов")
                await end_time(start, page=page)
            # __________________________________________________________________________________________________________
            elif page.route == "/account_connection_menu":  # Подключение аккаунтов 'меню'.
                await TGConnect().account_connection_menu(page=page)
            # __________________________________________________________________________________________________________
            elif page.route == "/creating_groups":  # Создание групп (чатов)
                await CreatingGroupsAndChats().creating_groups_and_chats(page=page)
            # __________________________________________________________________________________________________________
            elif page.route == "/sending_messages_files_via_chats":  # Рассылка сообщений по чатам
                await CheckingProgram().check_before_sending_messages_via_chats(page=page)
                await SendTelegramMessages().sending_messages_files_via_chats(page=page)
            elif page.route == "/sending_files_to_personal_account_with_limits":  # Отправка сообщений в личку
                await SendTelegramMessages().send_files_to_personal_chats(page=page)
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
                await SettingPage().writing_api_id_api_hash(page=page)
            elif page.route == "/message_limits":  # Лимиты на сообщения
                await SettingPage().record_setting(page, "message_limits", "Введите лимит на сообщения")
            elif page.route == "/account_limits":  # Лимиты на аккаунт
                await SettingPage().record_setting(page, "account_limits", "Введите лимит на аккаунт")
            elif page.route == "/creating_username_list":  # Формирование списка username
                await SettingPage().output_the_input_field(page, "members",
                                                           "username, id, access_hash, first_name, last_name, "
                                                           "user_phone, online_at, photos_id, user_premium",
                                                           "/settings", "members (username)")


            elif page.route == "/forming_list_of_chats_channels":  # Формирование списка чатов / каналов
                await SettingPage().output_the_input_field(page, "writing_group_links", "writing_group_links",
                                                           "/settings", "writing_group_links")



            # elif page.route == "/link_entry":  # Запись ссылки для инвайтинга
            #     await SettingPage().output_the_input_field(page, "Введите ссылку на группу для инвайтинга",
            #                                                "links_inviting",
            #                                                "links_inviting", "/settings", "links_inviting")
            elif page.route == "/proxy_entry":  # Запись proxy
                await SettingPage().creating_the_main_window_for_proxy_data_entry(page=page)
            elif page.route == "/message_recording":  # Запись сообщений
                await SettingPage().recording_text_for_sending_messages(page, "Введите текст для сообщения",
                                                                        get_unique_filename(
                                                                            base_filename='user_data/message/message'))
            elif page.route == "/recording_reaction_link":  # Запись ссылки для реакций
                await SettingPage().recording_text_for_sending_messages(page, "Введите ссылку для реакций",
                                                                        'user_data/reactions/link_channel.json')
            elif page.route == "/choice_of_reactions":  # Выбор реакций
                await reaction_gui(page=page)
            elif page.route == "/recording_the_time_between_messages":  # Запись времени между сообщениями

                await SettingPage().create_main_window(page=page, variable="time_sending_messages",
                                                       time_range=[time_sending_messages_1, time_sending_messages_2])
            elif page.route == "/time_between_invites_sending_messages":  # Время между инвайтингом, рассылка сообщений
                await SettingPage().create_main_window(page=page, variable="time_inviting",
                                                       time_range=[time_inviting_1, time_inviting_2])
            elif page.route == "/changing_accounts":  # Смена аккаунтов
                await SettingPage().create_main_window(page=page, variable="time_changing_accounts",
                                                       time_range=[time_changing_accounts_1, time_changing_accounts_2])
            elif page.route == "/time_between_subscriptions":
                await SettingPage().recording_the_time_to_launch_an_invite_every_day(page=page)
            elif page.route == "/time_between_subscriptionss":  # Время между подпиской
                await SettingPage().create_main_window(page=page, variable="time_subscription",
                                                       time_range=[time_subscription_1, time_subscription_2])
            elif page.route == "/errors":
                # Пустая страница с уведомлением
                page.views.append(ft.View("/errors", []))

            page.update()
        except Exception as error:
            logger.exception(error)

    def view_pop(_):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)


async def main_run(page):
    """Запуск программы"""
    await loging(page)


if __name__ == '__main__':
    def app(page: ft.Page):

        try:
            asyncio.run(main_run(page=page))
        except Exception as error:
            logger.exception(error)


    ft.app(target=main)
