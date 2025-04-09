# -*- coding: utf-8 -*-
import flet as ft
from loguru import logger

from src.core.configs import BUTTON_HEIGHT, small_button_width, BUTTON_WIDTH, line_width_button
from src.core.localization import (parse_single_or_multiple_groups, parse_selected_user_subscribed_group,
                                   parse_active_group_members, parse_account_subscribed_groups_channels,
                                   clear_previously_parsed_data_list, inviting_every_day_ru,
                                   invitation_at_a_certain_time_ru, invitation_1_time_per_hour_ru, inviting_ru,
                                   importing_a_list_of_parsed_data, setting_reactions,
                                   automatic_setting_of_reactions, choice_of_reactions_ru,
                                   proxy_entry_ru, changing_accounts_ru, recording_api_id_api_hash_ru,
                                   time_between_subscriptions_ru, message_recording_ru, link_entry_ru,
                                   account_limits_ru, message_limits_ru, time_between_subscriptionss_ru,
                                   creating_username_list_ru, recording_the_time_between_messages_ru,
                                   time_between_invites_sending_messages_ru, recording_reaction_link_ru,
                                   forming_list_of_chats_channels_ru, we_are_winding_up_post_views_ru,
                                   editing_bio, changing_the_username, changing_the_photo, changing_the_description,
                                   name_change_n, name_change_f, creating_a_contact_list, show_a_list_of_contacts,
                                   deleting_contacts, adding_contacts, working_with_contacts_menu_ru,
                                   subscribe_unsubscribe, subscription, unsubscribe, checking_accounts,
                                   checking_through_a_spam_bot, validation_check, renaming_accounts, full_verification,
                                   connecting_accounts, connecting_accounts_by_phone_number,
                                   connecting_session_accounts, to_boost_views, to_unsubscribe, to_subscribe,
                                   to_send_messages, for_marking_reactions, to_work_with_reactions, for_parsing,
                                   for_inviting, to_create_groups, to_work_with_numbers, to_edit_bio,
                                   for_the_answering_machine, working_with_reactions, parsing, settings, main_menu,
                                   creating_groups_chats, clearing_generated_chat_list)


async def settings_menu(page: ft.Page):
    """
    Меню настройки

    :param page: Страница интерфейса Flet для отображения элементов управления.
    """
    page.views.append(
        ft.View("/settings",
                [ft.AppBar(title=ft.Text(main_menu),
                           bgcolor=ft.colors.SURFACE_VARIANT),
                 ft.Text(spans=[ft.TextSpan(
                     settings,
                     ft.TextStyle(
                         size=20,
                         weight=ft.FontWeight.BOLD,
                         foreground=ft.Paint(
                             gradient=ft.PaintLinearGradient((0, 20), (150, 20), [ft.colors.PINK,
                                                                                  ft.colors.PURPLE])), ), ), ], ),
                 ft.Column([  # Добавляет все чекбоксы и кнопку на страницу (page) в виде колонок.
                     ft.Row([
                         # 👍 Выбор реакций
                         ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT, text=choice_of_reactions_ru,
                                           on_click=lambda _: page.go("/choice_of_reactions")),
                         # 🔐 Запись proxy
                         ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT, text=proxy_entry_ru,
                                           on_click=lambda _: page.go("/proxy_entry"))]),
                     ft.Row([
                         # 🔄 Смена аккаунтов
                         ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT, text=changing_accounts_ru,
                                           on_click=lambda _: page.go("/changing_accounts")),
                         # 📝 Запись api_id, api_hash
                         ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT,
                                           text=recording_api_id_api_hash_ru,
                                           on_click=lambda _: page.go("/recording_api_id_api_hash"))]),
                     ft.Row([
                         # ⏰ Запись времени
                         ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT,
                                           text=time_between_subscriptions_ru,
                                           on_click=lambda _: page.go("/time_between_subscriptions")),
                         # ✉️ Запись сообщений
                         ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT,
                                           text=message_recording_ru,
                                           on_click=lambda _: page.go("/message_recording"))]),
                     ft.Row([
                         # 🔗 Запись ссылки для инвайтинга
                         ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT,
                                           text=link_entry_ru,
                                           on_click=lambda _: page.go("/link_entry")),
                         # 📊 Лимиты на аккаунт
                         ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT,
                                           text=account_limits_ru,
                                           on_click=lambda _: page.go("/account_limits"))]),
                     ft.Row([
                         # 📨 Лимиты на сообщения
                         ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT,
                                           text=message_limits_ru,
                                           on_click=lambda _: page.go("/message_limits")),
                         # ⏳ Время между подпиской
                         ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT,
                                           text=time_between_subscriptionss_ru,
                                           on_click=lambda _: page.go("/time_between_subscriptionss")), ]),
                     # 📋 Формирование списка username
                     ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT, text=creating_username_list_ru,
                                       on_click=lambda _: page.go("/creating_username_list")),
                     # ⏱️ Запись времени между сообщениями
                     ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
                                       text=recording_the_time_between_messages_ru,
                                       on_click=lambda _: page.go("/recording_the_time_between_messages")),
                     # 🕒 Время между инвайтингом, рассылка сообщений
                     ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
                                       text=time_between_invites_sending_messages_ru,
                                       on_click=lambda _: page.go("/time_between_invites_sending_messages")),
                     # 🔗 Запись ссылки для реакций
                     ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT, text=recording_reaction_link_ru,
                                       on_click=lambda _: page.go("/recording_reaction_link")),
                     # 📑 Формирование списка чатов / каналов
                     ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
                                       text=forming_list_of_chats_channels_ru,
                                       on_click=lambda _: page.go("/forming_list_of_chats_channels")),
                     # 🧹 Очистка сформированного списка чатов
                     ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
                                       text=clearing_generated_chat_list,
                                       on_click=lambda _: page.go("/clearing_generated_chat_list")),
                 ])]))


async def bio_editing_menu(page: ft.Page):
    """
    Меню редактирование БИО

    :param page: Страница интерфейса Flet для отображения элементов управления.
    """
    page.views.append(
        ft.View("/bio_editing",
                [ft.AppBar(title=ft.Text(main_menu),
                           bgcolor=ft.colors.SURFACE_VARIANT),
                 ft.Text(spans=[ft.TextSpan(
                     editing_bio,
                     ft.TextStyle(
                         size=20,
                         weight=ft.FontWeight.BOLD,
                         foreground=ft.Paint(
                             gradient=ft.PaintLinearGradient((0, 20), (150, 20), [ft.colors.PINK,
                                                                                  ft.colors.PURPLE])), ), ), ], ),
                 ft.Column([  # Добавляет все чекбоксы и кнопку на страницу (page) в виде колонок.
                     # 🔄 Изменение username
                     ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT, text=changing_the_username,
                                       on_click=lambda _: page.go("/changing_username")),
                     # 🖼️ Изменение фото
                     ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT, text=changing_the_photo,
                                       on_click=lambda _: page.go("/edit_photo")),
                     # ✏️ Изменение описания
                     ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT, text=changing_the_description,
                                       on_click=lambda _: page.go("/edit_description")),
                     # 📝 Изменение имени
                     ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT, text=name_change_n,
                                       on_click=lambda _: page.go("/name_change")),
                     # 📝 Изменение фамилии
                     ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT, text=name_change_f,
                                       on_click=lambda _: page.go("/change_surname")),
                 ])]))


async def inviting_menu(page: ft.Page):
    """
    Меню инвайтинг

    :param page: Страница интерфейса Flet для отображения элементов управления.
    """
    page.views.append(
        ft.View("/inviting",
                [ft.AppBar(title=ft.Text(main_menu),
                           bgcolor=ft.colors.SURFACE_VARIANT),
                 ft.Text(spans=[ft.TextSpan(
                     inviting_ru,
                     ft.TextStyle(
                         size=20,
                         weight=ft.FontWeight.BOLD,
                         foreground=ft.Paint(
                             gradient=ft.PaintLinearGradient((0, 20), (150, 20), [ft.colors.PINK,
                                                                                  ft.colors.PURPLE])), ), ), ], ),
                 ft.Column([  # Добавляет все чекбоксы и кнопку на страницу (page) в виде колонок.
                     # 🚀 Инвайтинг
                     ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT, text=inviting_ru,
                                       on_click=lambda _: page.go("/inviting_without_limits")),
                     # ⏰ Инвайтинг 1 раз в час
                     ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT, text=invitation_1_time_per_hour_ru,
                                       on_click=lambda _: page.go("/inviting_1_time_per_hour")),
                     # 🕒 Инвайтинг в определенное время
                     ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT, text=invitation_at_a_certain_time_ru,
                                       on_click=lambda _: page.go("/inviting_certain_time")),
                     # 📅 Инвайтинг каждый день
                     ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT, text=inviting_every_day_ru,
                                       on_click=lambda _: page.go("/inviting_every_day")),
                 ])]))


async def working_with_contacts_menu(page: ft.Page):
    """
    Меню работа с контактами

    :param page: Страница интерфейса Flet для отображения элементов управления.
    """
    page.views.append(
        ft.View("/working_with_contacts",
                [ft.AppBar(title=ft.Text(main_menu),
                           bgcolor=ft.colors.SURFACE_VARIANT),
                 ft.Text(spans=[ft.TextSpan(
                     working_with_contacts_menu_ru,
                     ft.TextStyle(
                         size=20,
                         weight=ft.FontWeight.BOLD,
                         foreground=ft.Paint(
                             gradient=ft.PaintLinearGradient((0, 20), (150, 20), [ft.colors.PINK,
                                                                                  ft.colors.PURPLE])), ), ), ], ),
                 ft.Column([  # Добавляет все чекбоксы и кнопку на страницу (page) в виде колонок.
                     # 📋 Формирование списка контактов
                     ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT, text=creating_a_contact_list,
                                       on_click=lambda _: page.go("/creating_contact_list")),
                     # 👥 Показать список контактов
                     ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT, text=show_a_list_of_contacts,
                                       on_click=lambda _: page.go("/show_list_contacts")),
                     # 🗑️ Удаление контактов
                     ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT, text=deleting_contacts,
                                       on_click=lambda _: page.go("/deleting_contacts")),
                     # ➕ Добавление контактов
                     ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT, text=adding_contacts,
                                       on_click=lambda _: page.go("/adding_contacts")),
                 ])]))


async def menu_parsing(page: ft.Page):
    """
    Парсинг меню

    :param page: Страница интерфейса Flet для отображения элементов управления.
    """
    page.views.append(
        ft.View("/parsing",
                [ft.AppBar(title=ft.Text(main_menu),
                           bgcolor=ft.colors.SURFACE_VARIANT),
                 ft.Text(spans=[ft.TextSpan(
                     parsing,
                     ft.TextStyle(
                         size=20,
                         weight=ft.FontWeight.BOLD,
                         foreground=ft.Paint(
                             gradient=ft.PaintLinearGradient((0, 20), (150, 20), [ft.colors.PINK,
                                                                                  ft.colors.PURPLE])), ), ), ], ),
                 ft.Column([  # Добавляет все чекбоксы и кнопку на страницу (page) в виде колонок.
                     # 🔍 Парсинг одной группы / групп
                     ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
                                       text=parse_single_or_multiple_groups,
                                       on_click=lambda _: page.go("/parsing_single_groups")),
                     # 📂 Парсинг выбранной группы из подписанных пользователем
                     ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
                                       text=parse_selected_user_subscribed_group,
                                       on_click=lambda _: page.go("/parsing_selected_group_user_subscribed")),
                     # 👥 Парсинг активных участников группы
                     ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
                                       text=parse_active_group_members,
                                       on_click=lambda _: page.go("/parsing_active_group_members")),
                     # 📜 Парсинг групп / каналов на которые подписан аккаунт
                     ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
                                       text=parse_account_subscribed_groups_channels,
                                       on_click=lambda _: page.go("/parsing_groups_channels_account_subscribed")),
                     # 🗑️ Очистка списка от ранее спарсенных данных
                     ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
                                       text=clear_previously_parsed_data_list,
                                       on_click=lambda _: page.go("/clearing_list_previously_saved_data")),

                     # 📋 Импорт списка от ранее спарсенных данных
                     ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
                                       text=importing_a_list_of_parsed_data,
                                       on_click=lambda _: page.go("/importing_a_list_of_parsed_data")),

                 ])]))


async def reactions_menu(page: ft.Page):
    """
    Меню работа с реакциями

    :param page: Страница интерфейса Flet для отображения элементов управления.
    """
    page.views.append(
        ft.View("/working_with_reactions",
                [ft.AppBar(title=ft.Text(main_menu),
                           bgcolor=ft.colors.SURFACE_VARIANT),
                 ft.Text(spans=[ft.TextSpan(
                     working_with_reactions,
                     ft.TextStyle(
                         size=20,
                         weight=ft.FontWeight.BOLD,
                         foreground=ft.Paint(
                             gradient=ft.PaintLinearGradient((0, 20), (150, 20), [ft.colors.PINK,
                                                                                  ft.colors.PURPLE])), ), ), ], ),
                 ft.Column([  # Добавляет все чекбоксы и кнопку на страницу (page) в виде колонок.
                     # 👍 Ставим реакции
                     ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT, text=setting_reactions,
                                       on_click=lambda _: page.go("/setting_reactions")),
                     # 🤖 Автоматическое выставление реакций
                     ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
                                       text=automatic_setting_of_reactions,
                                       on_click=lambda _: page.go("/automatic_setting_of_reactions")),
                 ])]))


async def viewing_posts_menu(page: ft.Page):
    """
    Меню работа с просмотрами

    :param page: Страница интерфейса Flet для отображения элементов управления.
    """
    page.views.append(
        ft.View("/viewing_posts_menu",
                [ft.AppBar(title=ft.Text(main_menu),
                           bgcolor=ft.colors.SURFACE_VARIANT),
                 ft.Text(spans=[ft.TextSpan(
                     we_are_winding_up_post_views_ru,
                     ft.TextStyle(
                         size=20,
                         weight=ft.FontWeight.BOLD,
                         foreground=ft.Paint(
                             gradient=ft.PaintLinearGradient((0, 20), (150, 20), [ft.colors.PINK,
                                                                                  ft.colors.PURPLE])), ), ), ], ),
                 ft.Column([  # Добавляет все чекбоксы и кнопку на страницу (page) в виде колонок.
                     # 👁️‍🗨️ Накручиваем просмотры постов
                     ft.ElevatedButton(width=line_width_button, height=BUTTON_HEIGHT,
                                       text=we_are_winding_up_post_views_ru,
                                       on_click=lambda _: page.go("/we_are_winding_up_post_views")),
                 ])]))


async def subscribe_and_unsubscribe_menu(page: ft.Page):
    """
    Меню подписка и отписка

    :param page: Страница интерфейса Flet для отображения элементов управления.
    """
    page.views.append(
        ft.View("/subscribe_unsubscribe",
                [ft.AppBar(title=ft.Text(main_menu),
                           bgcolor=ft.colors.SURFACE_VARIANT),
                 ft.Text(spans=[ft.TextSpan(
                     subscribe_unsubscribe,
                     ft.TextStyle(
                         size=20,
                         weight=ft.FontWeight.BOLD,
                         foreground=ft.Paint(
                             gradient=ft.PaintLinearGradient((0, 20), (150, 20), [ft.colors.PINK,
                                                                                  ft.colors.PURPLE])), ), ), ], ),
                 ft.Column([  # Добавляет все чекбоксы и кнопку на страницу (page) в виде колонок.
                     # 🔔 Подписка
                     ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT, text=subscription,
                                       on_click=lambda _: page.go("/subscription_all")),
                     # 🚫 Отписываемся
                     ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT, text=unsubscribe,
                                       on_click=lambda _: page.go("/unsubscribe_all")),
                 ])]))


async def account_verification_menu(page: ft.Page):
    """
    Меню проверки аккаунтов

    :param page: Страница интерфейса Flet для отображения элементов управления.
    """
    page.views.append(
        ft.View("/account_verification_menu",
                [ft.AppBar(title=ft.Text(main_menu),
                           bgcolor=ft.colors.SURFACE_VARIANT),
                 ft.Text(spans=[ft.TextSpan(
                     checking_accounts,
                     ft.TextStyle(
                         size=20,
                         weight=ft.FontWeight.BOLD,
                         foreground=ft.Paint(
                             gradient=ft.PaintLinearGradient((0, 20), (150, 20), [ft.colors.PINK,
                                                                                  ft.colors.PURPLE])), ), ), ], ),
                 ft.Column([  # Добавляет все чекбоксы и кнопку на страницу (page) в виде колонок.
                     # 🤖 Проверка через спам бот
                     ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT, text=checking_through_a_spam_bot,
                                       on_click=lambda _: page.go("/checking_for_spam_bots")),
                     # ✅ Проверка на валидность
                     ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT, text=validation_check,
                                       on_click=lambda _: page.go("/validation_check")),
                     # ✏️ Переименование аккаунтов
                     ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT, text=renaming_accounts,
                                       on_click=lambda _: page.go("/renaming_accounts")),
                     # 🔍 Полная проверка
                     ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT, text=full_verification,
                                       on_click=lambda _: page.go("/full_verification")),

                 ])]))


async def account_connection_menu(page: ft.Page):
    """
    Меню подключения аккаунтов

    :param page: Страница интерфейса Flet для отображения элементов управления.
    """
    page.views.append(
        ft.View("/account_connection_menu",
                [ft.AppBar(title=ft.Text(main_menu),
                           bgcolor=ft.colors.SURFACE_VARIANT),
                 ft.Text(spans=[ft.TextSpan(
                     connecting_accounts,
                     ft.TextStyle(
                         size=20,
                         weight=ft.FontWeight.BOLD,
                         foreground=ft.Paint(
                             gradient=ft.PaintLinearGradient((0, 20), (150, 20), [ft.colors.PINK,
                                                                                  ft.colors.PURPLE])), ), ), ], ),

                 ft.Column([  # Добавляет все чекбоксы и кнопку на страницу (page) в виде колонок.
                     # 📞 Подключение аккаунтов по номеру телефона
                     ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
                                       text=connecting_accounts_by_phone_number,
                                       on_click=lambda _: page.go("/connecting_accounts_by_number")),
                     # 🔑 Подключение session аккаунтов
                     ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT, text=connecting_session_accounts,
                                       on_click=lambda _: page.go("/connecting_accounts_by_session")),
                 ])]))


async def connecting_accounts_by_number_menu(page: ft.Page):
    """
    Меню подключения аккаунтов по номеру телефона

    :param page: Страница интерфейса Flet для отображения элементов управления.
    """
    page.views.append(
        ft.View("/connecting_accounts_by_number",
                [ft.AppBar(title=ft.Text(main_menu),
                           bgcolor=ft.colors.SURFACE_VARIANT),
                 ft.Text(spans=[ft.TextSpan(
                     connecting_accounts_by_phone_number,
                     ft.TextStyle(
                         size=20,
                         weight=ft.FontWeight.BOLD,
                         foreground=ft.Paint(
                             gradient=ft.PaintLinearGradient((0, 20), (150, 20), [ft.colors.PINK,
                                                                                  ft.colors.PURPLE])), ), ), ], ),
                 ft.Column([  # Добавляет все чекбоксы и кнопку на страницу (page) в виде колонок.

                     ft.Row(
                         # 🤖 Для автоответчика
                         [ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT,
                                            text=for_the_answering_machine,
                                            on_click=lambda _: page.go(
                                                "/account_connection_number_answering_machine")),
                          # 📝 Для редактирования BIO
                          ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT,
                                            text=to_edit_bio,
                                            on_click=lambda _: page.go("/account_connection_number_bio"))]),
                     # 📞 Для работы с номерами
                     ft.Row([ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT,
                                               text=to_work_with_numbers,
                                               on_click=lambda _: page.go("/account_connection_number_contact")),
                             # 👥 Для создания групп
                             ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT,
                                               text=to_create_groups,
                                               on_click=lambda _: page.go("/account_connection_number_creating"))]),
                     # 🔗 Для инвайтинга
                     ft.Row([ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT, text=for_inviting,
                                               on_click=lambda _: page.go("/account_connection_number_inviting")),
                             # 📊 Для парсинга
                             ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT, text=for_parsing,
                                               on_click=lambda _: page.go("/account_connection_number_parsing"))]),
                     # 🎭 Для работы с реакциями
                     ft.Row([ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT,
                                               text=to_work_with_reactions,
                                               on_click=lambda _: page.go("/account_connection_number_reactions")),
                             # 👍 Для проставления реакций
                             ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT,
                                               text=for_marking_reactions,
                                               on_click=lambda _: page.go(
                                                   "/account_connection_number_reactions_list"))]),
                     # ✉️ Для рассылки сообщений
                     ft.Row([ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT,
                                               text=to_send_messages,
                                               on_click=lambda _: page.go("/account_connection_number_send_message")),
                             # 🔔 Для подписки
                             ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT, text=to_subscribe,
                                               on_click=lambda _: page.go("/account_connection_number_subscription"))]),
                     # 🚫 Для отписки
                     ft.Row([ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT, text=to_unsubscribe,
                                               on_click=lambda _: page.go("/account_connection_number_unsubscribe")),
                             # 📈 Для накрутки просмотров
                             ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT,
                                               text=to_boost_views,
                                               on_click=lambda _: page.go("/account_connection_number_viewing"))]),

                 ])]))


async def connecting_accounts_by_session_menu(page: ft.Page):
    """
    Меню подключения аккаунтов по номеру телефона

    :param page: Страница интерфейса Flet для отображения элементов управления.
    """
    page.views.append(
        ft.View("/connecting_accounts_by_session",
                [ft.AppBar(title=ft.Text(main_menu),
                           bgcolor=ft.colors.SURFACE_VARIANT),
                 ft.Text(spans=[ft.TextSpan(
                     connecting_session_accounts,
                     ft.TextStyle(
                         size=20,
                         weight=ft.FontWeight.BOLD,
                         foreground=ft.Paint(
                             gradient=ft.PaintLinearGradient((0, 20), (150, 20), [ft.colors.PINK,
                                                                                  ft.colors.PURPLE])), ), ), ], ),
                 ft.Column([  # Добавляет все чекбоксы и кнопку на страницу (page) в виде колонок.

                     ft.Row(
                         # 🤖 Для автоответчика
                         [ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT,
                                            text=for_the_answering_machine,
                                            on_click=lambda _: page.go(
                                                "/account_connection_session_answering_machine")),
                          # 📝 Для редактирования BIO
                          ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT,
                                            text=to_edit_bio,
                                            on_click=lambda _: page.go("/account_connection_session_bio"))]),
                     # 📞 Для работы с номерами
                     ft.Row([ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT,
                                               text=to_work_with_numbers,
                                               on_click=lambda _: page.go("/account_connection_session_contact")),
                             # 👥 Для создания групп
                             ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT,
                                               text=to_create_groups,
                                               on_click=lambda _: page.go("/account_connection_session_creating"))]),
                     # 🔗 Для инвайтинга
                     ft.Row([ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT, text=for_inviting,
                                               on_click=lambda _: page.go("/account_connection_session_inviting")),
                             # 📊 Для парсинга
                             ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT, text=for_parsing,
                                               on_click=lambda _: page.go("/account_connection_session_parsing"))]),
                     # 🎭 Для работы с реакциями
                     ft.Row([ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT,
                                               text=to_work_with_reactions,
                                               on_click=lambda _: page.go("/account_connection_session_reactions")),
                             # 👍 Для проставления реакций
                             ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT,
                                               text=for_marking_reactions,
                                               on_click=lambda _: page.go(
                                                   "/account_connection_session_reactions_list"))]),
                     # ✉️ Для рассылки сообщений
                     ft.Row([ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT,
                                               text=to_send_messages,
                                               on_click=lambda _: page.go(
                                                   "/account_connection_session_send_message")),
                             # 🔔 Для подписки
                             ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT, text=to_subscribe,
                                               on_click=lambda _: page.go(
                                                   "/account_connection_session_subscription"))]),
                     # 🚫 Для отписки
                     ft.Row([ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT, text=to_unsubscribe,
                                               on_click=lambda _: page.go(
                                                   "/account_connection_session_unsubscribe")),
                             # 📈 Для накрутки просмотров
                             ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT,
                                               text=to_boost_views,
                                               on_click=lambda _: page.go("/account_connection_session_viewing"))]),

                 ])]))


async def creating_groups_and_chats_menu(page: ft.Page):
    """
    Меню создания групп и чатов

    :param page: Страница интерфейса Flet для отображения элементов управления.
    """

    page.views.append(
        ft.View("/creating_groups_and_chats_menu",
                [ft.AppBar(title=ft.Text(main_menu),
                           bgcolor=ft.colors.SURFACE_VARIANT),
                 ft.Text(spans=[ft.TextSpan(
                     creating_groups_chats,
                     ft.TextStyle(
                         size=20,
                         weight=ft.FontWeight.BOLD,
                         foreground=ft.Paint(
                             gradient=ft.PaintLinearGradient((0, 20), (150, 20), [ft.colors.PINK,
                                                                                  ft.colors.PURPLE])), ), ), ], ),
                 ft.Column([  # Добавляет все чекбоксы и кнопку на страницу (page) в виде колонок.
                     # 👥 Создание групп (чатов)
                     ft.ElevatedButton(width=line_width_button, height=BUTTON_HEIGHT,
                                       text=creating_groups_chats,
                                       on_click=lambda _: page.go("/creating_groups")),
                 ])]))


async def log_and_display(message: str, lv: ft.ListView, page: ft.Page, level: str = "info"):
    """
    Выводит сообщение в GUI и записывает лог с указанным уровнем с помощью loguru.

    :param message: Текст сообщения для отображения и записи в лог
    :param lv: ListView для отображения сообщений
    :param page: Страница интерфейса Flet для отображения элементов управления
    :param level: Уровень логирования ("info" или "error"), по умолчанию "info"
    """
    if level.lower() == "error":
        logger.error(message)
    else:
        logger.info(message)
    lv.controls.append(ft.Text(message))
    page.update()


async def show_notification(page: ft.Page, message: str):
    """
    Функция для показа уведомления

    :param page: Страница интерфейса Flet для отображения элементов управления.
    :param message: Текст уведомления.
    """
    # Переход обратно после закрытия диалога
    dlg = ft.AlertDialog(title=ft.Text(message), on_dismiss=lambda e: page.go("/"))
    page.overlay.append(dlg)
    dlg.open = True
    page.update()
