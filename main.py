# -*- coding: utf-8 -*-
import asyncio
import datetime

import flet as ft
from loguru import logger

from docs.app import start_app
from src.core.checking_program import CheckingProgram
from src.core.configs import (ConfigReader, program_name, program_version, date_of_program_change, window_width,
                              window_height, window_resizable)
from src.core.sqlite_working_tools import DatabaseHandler
from src.features.account.TGAccountBIO import AccountBIO
from src.features.account.TGChek import TGChek
from src.features.account.TGConnect import TGConnect
from src.features.account.TGContact import TGContact
from src.features.account.TGCreating import CreatingGroupsAndChats
from src.features.account.TGInviting import InvitingToAGroup
from src.features.account.TGParsing import ParsingGroupMembers
from src.features.account.TGReactions import WorkingWithReactions
from src.features.account.TGSendingMessages import SendTelegramMessages
from src.features.account.TGSubUnsub import SubscribeUnsubscribeTelegram
from src.features.account.TGViewingPosts import ViewingPosts
from src.features.auth.logging_in import loging
from src.features.recording.receiving_and_recording import ReceivingAndRecording
from src.features.settings.setting import SettingPage, get_unique_filename, reaction_gui
from src.gui.menu import (inviting_menu, bio_editing_menu, settings_menu, menu_parsing, reactions_menu,
                          subscribe_and_unsubscribe_menu, account_verification_menu, account_connection_menu,
                          connecting_accounts_by_number_menu, connecting_accounts_by_session_menu, viewing_posts_menu,
                          show_notification, creating_groups_and_chats_menu, working_with_contacts_menu,
                          main_menu_program)
from src.gui.sending_messages_menu import display_message_distribution_menu

logger.add("user_data/log/log.log", rotation="500 KB", compression="zip", level="INFO")  # Логирование программы
logger.add("user_data/log/log_ERROR.log", rotation="500 KB", compression="zip", level="ERROR")  # Логирование программы


async def main(page: ft.Page):
    """
    Главное меню программы

    Аргументы:
    :param page: Страница интерфейса Flet для отображения элементов управления.
    """
    page.title = f"{program_name}: {program_version} (Дата изменения {date_of_program_change})"
    page.window.width = window_width  # Ширина окна
    page.window.height = window_height  # Высота окна
    page.window.resizable = window_resizable  # Разрешение изменения размера окна
    logger.info(f"Program version: {program_version}. Date of change: {date_of_program_change}")

    async def route_change(route):

        page.views.clear()
        # ______________________________________________________________________________________________________________
        await main_menu_program(page)  # Главное меню программы
        # ______________________________________________________________________________________________________________
        try:
            if page.route == "/inviting":  # Меню "🚀 Инвайтинг"
                await inviting_menu(page)
            elif page.route == "/inviting_without_limits":  # 🚀 Инвайтинг
                await CheckingProgram().check_before_inviting(page=page)
                await InvitingToAGroup().inviting_without_limits(page=page)
            elif page.route == "/inviting_1_time_per_hour":  # ⏰ Инвайтинг 1 раз в час
                await CheckingProgram().check_before_inviting(page=page)
                await InvitingToAGroup().launching_an_invite_once_an_hour(page=page)
            elif page.route == "/inviting_certain_time":  # 🕒 Инвайтинг в определенное время
                await CheckingProgram().check_before_inviting(page=page)
                await InvitingToAGroup().schedule_invite(page=page)
            elif page.route == "/inviting_every_day":  # 📅 Инвайтинг каждый день
                await CheckingProgram().check_before_inviting(page=page)
                await InvitingToAGroup().launching_invite_every_day_certain_time(page=page)
            # ______________________________________________________________________________________________________________
            elif page.route == "/account_verification_menu":  # Меню "Проверка аккаунтов"
                await account_verification_menu(page)
            elif page.route == "/validation_check":  # Проверка на валидность
                await TGChek().validation_check(page=page)
            elif page.route == "/checking_for_spam_bots":  # Проверка через спам бот
                await TGChek().checking_for_spam_bots(page=page)
            elif page.route == "/renaming_accounts":  # Переименование аккаунтов
                await TGChek().renaming_accounts(page=page)
            elif page.route == "/full_verification":  # Полная проверка
                await TGChek().full_verification(page=page)
            # ______________________________________________________________________________________________________________
            elif page.route == "/subscribe_unsubscribe":  # Меню "Подписка и отписка"
                await subscribe_and_unsubscribe_menu(page)
            elif page.route == "/subscription_all":  # Подписка
                await CheckingProgram().checking_for_subscription_account(page=page)
                await SubscribeUnsubscribeTelegram().subscribe_telegram(page=page)
            elif page.route == "/unsubscribe_all":  # Отписываемся
                await CheckingProgram().checking_for_unsubscribe_all(page=page)
                start = datetime.datetime.now()  # фиксируем и выводим время старта работы кода
                logger.info('Время старта: ' + str(start))
                logger.info("▶️ Начало Отписка")
                await SubscribeUnsubscribeTelegram().unsubscribe_all(page=page)
                logger.info("🔚 Конец Отписки")
                finish = datetime.datetime.now()  # фиксируем и выводим время окончания работы кода
                logger.info('Время окончания: ' + str(finish))
                logger.info('Время работы: ' + str(finish - start))  # вычитаем время старта из времени окончания
            # ______________________________________________________________________________________________________________
            elif page.route == "/working_with_reactions":  # Меню "Работа с реакциями"
                await reactions_menu(page)
            elif page.route == "/setting_reactions":  # Ставим реакции
                await CheckingProgram().checking_for_setting_reactions(page=page)
                start = datetime.datetime.now()  # фиксируем и выводим время старта работы кода
                logger.info('Время старта: ' + str(start))
                logger.info("▶️ Начало Проставления реакций")
                await WorkingWithReactions().send_reaction_request(page)
                logger.info("🔚 Конец Проставления реакций")
                finish = datetime.datetime.now()  # фиксируем и выводим время окончания работы кода
                logger.info('Время окончания: ' + str(finish))
                logger.info('Время работы: ' + str(finish - start))  # вычитаем время старта из времени окончания
            elif page.route == "/automatic_setting_of_reactions":  # Автоматическое выставление реакций
                await CheckingProgram().checking_for_setting_reactions(page=page)
                start = datetime.datetime.now()  # фиксируем и выводим время старта работы кода
                logger.info('Время старта: ' + str(start))
                logger.info("▶️ Начало Автоматического выставления реакций")
                await WorkingWithReactions().setting_reactions(page=page)
                logger.info("🔚 Конец Автоматического выставления реакций")
                finish = datetime.datetime.now()  # фиксируем и выводим время окончания работы кода
                logger.info('Время окончания: ' + str(finish))
                logger.info('Время работы: ' + str(finish - start))  # вычитаем время старта из времени окончания
            # ______________________________________________________________________________________________________________
            elif page.route == "/viewing_posts_menu":  # Автоматическое выставление просмотров меню
                await viewing_posts_menu(page)
            elif page.route == "/we_are_winding_up_post_views":  # ️‍🗨️ Накручиваем просмотры постов
                await CheckingProgram().checking_for_viewing_posts_menu(page=page)
                start = datetime.datetime.now()  # фиксируем и выводим время старта работы кода
                logger.info('Время старта: ' + str(start))
                logger.info("▶️ Начало Накрутки просмотров постов")
                await ViewingPosts().viewing_posts_request(page)
                logger.info("🔚 Конец Накрутки просмотров постов")
                finish = datetime.datetime.now()  # фиксируем и выводим время окончания работы кода
                logger.info('Время окончания: ' + str(finish))
                logger.info('Время работы: ' + str(finish - start))  # вычитаем время старта из времени окончания
            # ______________________________________________________________________________________________________________
            elif page.route == "/parsing":  # Меню "Парсинг"
                await menu_parsing(page)
            elif page.route == "/parsing_single_groups":  # 🔍 Парсинг одной группы / групп
                await CheckingProgram().checking_for_parsing_single_groups(page=page)
                await ParsingGroupMembers().parse_groups(page)
            elif page.route == "/parsing_selected_group_user_subscribed":  # Парсинг выбранной группы
                await CheckingProgram().checking_for_parsing_single_groups(page=page)
                await ParsingGroupMembers().choose_and_parse_group(page)
            elif page.route == "/parsing_active_group_members":  # Парсинг активных участников группы
                await CheckingProgram().checking_for_parsing_single_groups(page=page)
                await ParsingGroupMembers().entering_data_for_parsing_active(page)
            elif page.route == "/parsing_groups_channels_account_subscribed":  # Парсинг групп / каналов аккаунта
                await CheckingProgram().checking_for_parsing_single_groups(page=page)
                await ParsingGroupMembers().parse_subscribed_groups(page)
            elif page.route == "/clearing_list_previously_saved_data":  # Очистка списка от ранее спарсенных данных
                await DatabaseHandler().cleaning_db("members")
                await show_notification(page, "Очистка списка окончена")  # Сообщение пользователю
            elif page.route == "/importing_a_list_of_parsed_data":  # 📋 Импорт списка от ранее спарсенных данных
                await ReceivingAndRecording().write_data_to_excel(file_name="user_data/parsed_chat_participants.xlsx")
            # ______________________________________________________________________________________________________________
            elif page.route == "/working_with_contacts":  # Меню "Работа с контактами"
                await working_with_contacts_menu(page)
            elif page.route == "/creating_contact_list":  # Формирование списка контактов
                await CheckingProgram().checking_creating_contact_list(page=page)
                start = datetime.datetime.now()  # фиксируем и выводим время старта работы кода
                logger.info('Время старта: ' + str(start))
                logger.info("▶️ Начало Формирования списка контактов")
                await DatabaseHandler().open_and_read_data("contact")  # Удаление списка с контактами
                SettingPage().output_the_input_field(page, "Введите список номеров телефонов", "contact",
                                                     "contact", "/working_with_contacts", "contact")
                logger.info("🔚 Конец Формирования списка контактов")
                finish = datetime.datetime.now()  # фиксируем и выводим время окончания работы кода
                logger.info('Время окончания: ' + str(finish))
                logger.info('Время работы: ' + str(finish - start))  # вычитаем время старта из времени окончания
            elif page.route == "/show_list_contacts":  # Показать список контактов
                await CheckingProgram().checking_creating_contact_list(page=page)
                start = datetime.datetime.now()  # фиксируем и выводим время старта работы кода
                logger.info('Время старта: ' + str(start))
                logger.info("▶️ Начало Показа списка контактов")
                await TGContact().show_account_contact_list(page=page)
                logger.info("🔚 Конец Показа списка контактов")
                finish = datetime.datetime.now()  # фиксируем и выводим время окончания работы кода
                logger.info('Время окончания: ' + str(finish))
                logger.info('Время работы: ' + str(finish - start))  # вычитаем время старта из времени окончания
            elif page.route == "/deleting_contacts":  # Удаление контактов
                await CheckingProgram().checking_creating_contact_list(page=page)
                start = datetime.datetime.now()  # фиксируем и выводим время старта работы кода
                logger.info('Время старта: ' + str(start))
                logger.info("▶️ Начало Удаления контактов")
                await TGContact().delete_contact(page=page)
                logger.info("🔚 Конец Удаления контактов")
                finish = datetime.datetime.now()  # фиксируем и выводим время окончания работы кода
                logger.info('Время окончания: ' + str(finish))
                logger.info('Время работы: ' + str(finish - start))  # вычитаем время старта из времени окончания
            elif page.route == "/adding_contacts":  # Добавление контактов
                await CheckingProgram().checking_creating_contact_list(page=page)
                start = datetime.datetime.now()  # фиксируем и выводим время старта работы кода
                logger.info('Время старта: ' + str(start))
                logger.info("▶️ Начало Добавления контактов")
                await TGContact().inviting_contact(page=page)
                logger.info("🔚 Конец Добавления контактов")
                finish = datetime.datetime.now()  # фиксируем и выводим время окончания работы кода
                logger.info('Время окончания: ' + str(finish))
                logger.info('Время работы: ' + str(finish - start))  # вычитаем время старта из времени окончания
            # ______________________________________________________________________________________________________________
            elif page.route == "/account_connection_menu":  # Подключение аккаунтов 'меню'.
                await account_connection_menu(page)
            # _______________________________________________________________________________________________________________
            elif page.route == "/connecting_accounts_by_number":  # Подключение аккаунтов по номеру телефона 'Меню'
                await connecting_accounts_by_number_menu(page)
            elif page.route == "/account_connection_number_answering_machine":  # Для автоответчика
                await TGConnect().connecting_number_accounts(page, 'answering_machine', 'автоответчика')
            elif page.route == "/account_connection_number_bio":  # Для редактирования BIO
                await TGConnect().connecting_number_accounts(page, 'bio', 'редактирования BIO')
            elif page.route == "/account_connection_number_contact":  # Для работы с номерами
                await TGConnect().connecting_number_accounts(page, 'contact', 'работы с номерами')
            elif page.route == "/account_connection_number_creating":  # Для создания групп
                await TGConnect().connecting_number_accounts(page, 'creating', 'создания групп')
            elif page.route == "/account_connection_number_inviting":  # Для инвайтинга
                await TGConnect().connecting_number_accounts(page, 'inviting', 'инвайтинга')
            elif page.route == "/account_connection_number_parsing":  # Для парсинга
                await TGConnect().connecting_number_accounts(page, 'parsing', 'парсинга')
            elif page.route == "/account_connection_number_reactions":  # Для работы с реакциями
                await TGConnect().connecting_number_accounts(page, 'reactions', 'работы с реакциями')
            elif page.route == "/account_connection_number_reactions_list":  # Для проставления реакций
                await TGConnect().connecting_number_accounts(page, 'reactions_list', 'проставления реакций')
            elif page.route == "/account_connection_number_send_message":  # Для рассылки сообщений
                await TGConnect().connecting_number_accounts(page, 'send_message', 'рассылки сообщений')
            elif page.route == "/account_connection_number_subscription":  # Для подписки
                await TGConnect().connecting_number_accounts(page, 'subscription', 'подписки')
            elif page.route == "/account_connection_number_unsubscribe":  # Для отписки
                await TGConnect().connecting_number_accounts(page, 'unsubscribe', 'отписки')
            elif page.route == "/account_connection_number_viewing":  # Для накрутки просмотров
                await TGConnect().connecting_number_accounts(page, 'viewing', 'накрутки просмотров')
            # _______________________________________________________________________________________________________________
            elif page.route == "/connecting_accounts_by_session":  # Подключение session аккаунтов 'Меню'
                await connecting_accounts_by_session_menu(page)
            elif page.route == "/account_connection_session_answering_machine":  # Для автоответчика (session)
                await TGConnect().connecting_session_accounts(page, 'answering_machine', 'автоответчика')
            elif page.route == "/account_connection_session_bio":  # Для редактирования BIO (session)
                await TGConnect().connecting_session_accounts(page, 'bio', 'редактирования BIO')
            elif page.route == "/account_connection_session_contact":  # Для работы с номерами (session)
                await TGConnect().connecting_session_accounts(page, 'contact', 'работы с номерами')
            elif page.route == "/account_connection_session_creating":  # Для создания групп (session)
                await TGConnect().connecting_session_accounts(page, 'creating', 'создания групп')
            elif page.route == "/account_connection_session_inviting":  # Для инвайтинга (session)
                await TGConnect().connecting_session_accounts(page, 'inviting', 'инвайтинга')
            elif page.route == "/account_connection_session_parsing":  # Для парсинга (session)
                await TGConnect().connecting_session_accounts(page, 'parsing', 'парсинга')
            elif page.route == "/account_connection_session_reactions":  # Для работы с реакциями (session)
                await TGConnect().connecting_session_accounts(page, 'reactions', 'работы с реакциями')
            elif page.route == "/account_connection_session_reactions_list":  # Для проставления реакций (session)
                await TGConnect().connecting_session_accounts(page, 'reactions_list', 'проставления реакций')
            elif page.route == "/account_connection_session_send_message":  # Для рассылки сообщений (session)
                await TGConnect().connecting_session_accounts(page, 'send_message', 'рассылки сообщений')
            elif page.route == "/account_connection_session_subscription":  # Для подписки (session)
                await TGConnect().connecting_session_accounts(page, 'subscription', 'подписки')
            elif page.route == "/account_connection_session_unsubscribe":  # Для отписки (session)
                await TGConnect().connecting_session_accounts(page, 'unsubscribe', 'отписки')
            elif page.route == "/account_connection_session_viewing":  # Для накрутки просмотров (session)
                await TGConnect().connecting_session_accounts(page, 'viewing', 'накрутки просмотров')
            # _______________________________________________________________________________________________________________
            elif page.route == "/creating_groups_and_chats_menu":  # Меню "Создание групп и чатов"
                await creating_groups_and_chats_menu(page)
            elif page.route == "/creating_groups":  # Создание групп (чатов)
                await CheckingProgram().checking_creating_groups(page=page)
                await CreatingGroupsAndChats().creating_groups_and_chats(page=page)
            # _______________________________________________________________________________________________________________
            elif page.route == "/sending_messages":  # Меню "Рассылка сообщений"
                await display_message_distribution_menu(page)

            elif page.route == "/sending_messages_files_via_chats":  # Рассылка сообщений по чатам
                await CheckingProgram().check_before_sending_messages_via_chats(page=page)
                await SendTelegramMessages().sending_messages_files_via_chats(page=page)

            elif page.route == "/sending_files_to_personal_account_with_limits":  # Отправка сообщений в личку
                await CheckingProgram().checking_sending_to_personal(page=page)
                await SendTelegramMessages().send_files_to_personal_chats(page=page)

            # ______________________________________________________________________________________________________________
            elif page.route == "/bio_editing":  # Меню "Редактирование_BIO"
                await bio_editing_menu(page)
            elif page.route == "/edit_description":  # Изменение описания
                await CheckingProgram().checking_for_bio(page=page)
                await AccountBIO().change_bio_profile_gui(page)
            elif page.route == "/name_change":  # Изменение имени профиля Telegram
                await CheckingProgram().checking_for_bio(page=page)
                await AccountBIO().change_name_profile_gui(page)
            elif page.route == "/change_surname":  # Изменение фамилии
                await CheckingProgram().checking_for_bio(page=page)
                await AccountBIO().change_last_name_profile_gui(page)
            elif page.route == "/edit_photo":  # Изменение фото
                await CheckingProgram().checking_for_bio(page=page)
                await AccountBIO().change_photo_profile_gui(page)
                await show_notification(page, "🔚 Фото изменено")  # Выводим уведомление пользователю
            elif page.route == "/changing_username":  # Изменение username
                await CheckingProgram().checking_for_bio(page=page)
                await AccountBIO().change_username_profile_gui(page)
            # ______________________________________________________________________________________________________________
            elif page.route == "/settings":  # Меню "Настройки TelegramMaster"
                await settings_menu(page)
            elif page.route == "/recording_api_id_api_hash":  # Запись api_id, api_hash
                await SettingPage().writing_api_id_api_hash(page)
            elif page.route == "/message_limits":  # Лимиты на сообщения
                await SettingPage().record_setting(page, "message_limits", "Введите лимит на сообщения")
            elif page.route == "/account_limits":  # Лимиты на аккаунт
                await SettingPage().record_setting(page, "account_limits", "Введите лимит на аккаунт")
            elif page.route == "/creating_username_list":  # Формирование списка username
                SettingPage().output_the_input_field(page, "Введите список username", "members",
                                                     "username, id, access_hash, first_name, last_name, "
                                                     "user_phone, online_at, photos_id, user_premium",
                                                     "/settings", "members (username)")
            elif page.route == "/forming_list_of_chats_channels":  # Формирование списка чатов / каналов
                SettingPage().output_the_input_field(page, "Введите список ссылок на группы", "writing_group_links",
                                                     "writing_group_links", "/settings", "writing_group_links")
            elif page.route == "/link_entry":  # Запись ссылки для инвайтинга
                SettingPage().output_the_input_field(page, "Введите ссылку на группу для инвайтинга", "links_inviting",
                                                     "links_inviting", "/settings", "links_inviting")
            elif page.route == "/proxy_entry":  # Запись proxy
                await SettingPage().creating_the_main_window_for_proxy_data_entry(page)
            elif page.route == "/message_recording":  # Запись сообщений
                await SettingPage().recording_text_for_sending_messages(page, "Введите текст для сообщения",
                                                                        get_unique_filename(
                                                                            base_filename='user_data/message/message'))
            elif page.route == "/recording_reaction_link":  # Запись ссылки для реакций
                await SettingPage().recording_text_for_sending_messages(page, "Введите ссылку для реакций",
                                                                        'user_data/reactions/link_channel.json')
            elif page.route == "/choice_of_reactions":  # Выбор реакций
                await reaction_gui(page)
            elif page.route == "/recording_the_time_between_messages":  # Запись времени между сообщениями
                time_sending_messages_1, time_sending_messages_2 = ConfigReader().get_time_inviting()  # Время между сообщениями
                time_sending_messages = [time_sending_messages_1, time_sending_messages_2]
                await SettingPage().create_main_window(page, variable="time_sending_messages",
                                                       time_range=time_sending_messages)
            elif page.route == "/time_between_invites_sending_messages":  # Время между инвайтингом, рассылка сообщений
                time_inviting_1, time_inviting_2 = ConfigReader().get_time_inviting()  # Время между инвайтингом, рассылка сообщений
                time_inviting = [time_inviting_1, time_inviting_2]
                await SettingPage().create_main_window(page, variable="time_inviting", time_range=time_inviting)
            elif page.route == "/changing_accounts":  # Смена аккаунтов
                time_changing_accounts_1, time_changing_accounts_2 = ConfigReader().get_config_time_changing_accounts()  # Время смены аккаунтов
                time_changing_accounts = [time_changing_accounts_1, time_changing_accounts_2]
                await SettingPage().create_main_window(page, variable="time_changing_accounts",
                                                       time_range=time_changing_accounts)
            elif page.route == "/time_between_subscriptions":
                await SettingPage().recording_the_time_to_launch_an_invite_every_day(page)
            elif page.route == "/time_between_subscriptionss":  # Время между подпиской
                time_subscription_1, time_subscription_2 = ConfigReader().get_time_subscription()
                time_subscription = [time_subscription_1, time_subscription_2]
                await SettingPage().create_main_window(page, variable="time_subscription", time_range=time_subscription)
            elif page.route == "/clearing_generated_chat_list":  # 🧹 Очистка сформированного списка чатов
                await DatabaseHandler().cleaning_db("writing_group_links")
                await show_notification(page, "Очистка списка окончена")  # Сообщение пользователю
            elif page.route == "/documentation":  # Открытие документации
                start_app()
            elif page.route == "/errors":
                # Пустая страница с уведомлением
                page.views.append(ft.View("/errors", []))

            page.update()
        except Exception as error:
            logger.exception(f"❌ Ошибка: {error}")

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)


async def main_run():
    """Запуск программы"""
    await loging()


if __name__ == '__main__':

    try:
        asyncio.run(main_run())
    except Exception as error:
        logger.exception(f"❌ Ошибка: {error}")

    ft.app(target=main)
