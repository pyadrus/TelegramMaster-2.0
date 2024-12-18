# -*- coding: utf-8 -*-
import flet as ft
from loguru import logger

from system.auxiliary_functions.config import height_button, small_button_width, line_width, line_width_button
from system.localization.localization import (parse_single_or_multiple_groups, parse_selected_user_subscribed_group,
                                              parse_active_group_members, parse_account_subscribed_groups_channels,
                                              clear_previously_parsed_data_list,
                                              inviting_every_day, invitation_at_a_certain_time,
                                              invitation_1_time_per_hour, inviting, importing_a_list_of_parsed_data,
                                              setting_reactions, automatic_setting_of_reactions,
                                              sending_messages_via_chats,
                                              sending_messages_via_chats_with_answering_machine,
                                              sending_files_via_chats, sending_messages_files_via_chats,
                                              sending_personal_messages_with_limits,
                                              sending_files_to_personal_account_with_limits, choice_of_reactions_ru,
                                              proxy_entry_ru, changing_accounts_ru, recording_api_id_api_hash_ru,
                                              time_between_subscriptions_ru, message_recording_ru, link_entry_ru, account_limits_ru,
                                              message_limits_ru, time_between_subscriptionss_ru, creating_username_list_ru,
                                              recording_the_time_between_messages,
                                              time_between_invites_sending_messages, recording_reaction_link,
                                              forming_list_of_chats_channels, we_are_winding_up_post_views, editing_bio,
                                              changing_the_username, changing_the_photo, changing_the_description,
                                              name_change_n, name_change_f, creating_a_contact_list,
                                              show_a_list_of_contacts, deleting_contacts, adding_contacts,
                                              working_with_contacts_menu_ru, subscribe_unsubscribe, subscription,
                                              unsubscribe,
                                              checking_accounts, checking_through_a_spam_bot, validation_check,
                                              renaming_accounts, full_verification, connecting_accounts,
                                              connecting_accounts_by_phone_number, connecting_session_accounts,
                                              to_boost_views, to_unsubscribe, to_subscribe, to_send_messages,
                                              for_marking_reactions, to_work_with_reactions, for_parsing, for_inviting,
                                              to_create_groups, to_work_with_numbers, to_edit_bio,
                                              for_the_answering_machine, working_with_reactions, parsing,
                                              sending_messages, settings, main_menu, creating_groups_chats)


async def settings_menu(page):
    """
    Меню настройки

    Аргументы:
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
                         ft.ElevatedButton(width=small_button_width, height=height_button, text=choice_of_reactions_ru,
                                           on_click=lambda _: page.go("/choice_of_reactions")),
                         # 🔐 Запись proxy
                         ft.ElevatedButton(width=small_button_width, height=height_button, text=proxy_entry_ru,
                                           on_click=lambda _: page.go("/proxy_entry"))]),
                     ft.Row([
                         # 🔄 Смена аккаунтов
                         ft.ElevatedButton(width=small_button_width, height=height_button, text=changing_accounts_ru,
                                           on_click=lambda _: page.go("/changing_accounts")),
                         # 📝 Запись api_id, api_hash
                         ft.ElevatedButton(width=small_button_width, height=height_button,
                                           text=recording_api_id_api_hash_ru,
                                           on_click=lambda _: page.go("/recording_api_id_api_hash"))]),
                     ft.Row([
                         # ⏰ Запись времени
                         ft.ElevatedButton(width=small_button_width, height=height_button,
                                           text=time_between_subscriptions_ru,
                                           on_click=lambda _: page.go("/time_between_subscriptions")),
                         # ✉️ Запись сообщений
                         ft.ElevatedButton(width=small_button_width, height=height_button,
                                           text=message_recording_ru,
                                           on_click=lambda _: page.go("/message_recording"))]),
                     ft.Row([
                         # 🔗 Запись ссылки для инвайтинга
                         ft.ElevatedButton(width=small_button_width, height=height_button,
                                           text=link_entry_ru,
                                           on_click=lambda _: page.go("/link_entry")),
                         # 📊 Лимиты на аккаунт
                         ft.ElevatedButton(width=small_button_width, height=height_button,
                                           text=account_limits_ru,
                                           on_click=lambda _: page.go("/account_limits"))]),
                     ft.Row([
                         # 📨 Лимиты на сообщения
                         ft.ElevatedButton(width=small_button_width, height=height_button,
                                           text=message_limits_ru,
                                           on_click=lambda _: page.go("/message_limits")),
                         # ⏳ Время между подпиской
                         ft.ElevatedButton(width=small_button_width, height=height_button,
                                           text=time_between_subscriptionss_ru,
                                           on_click=lambda _: page.go("/time_between_subscriptionss")), ]),
                     # 📋 Формирование списка username
                     ft.ElevatedButton(width=line_width, height=height_button, text=creating_username_list_ru,
                                       on_click=lambda _: page.go("/creating_username_list")),
                     # ⏱️ Запись времени между сообщениями
                     ft.ElevatedButton(width=line_width, height=height_button,
                                       text=recording_the_time_between_messages,
                                       on_click=lambda _: page.go("/recording_the_time_between_messages")),
                     # 🕒 Время между инвайтингом, рассылка сообщений
                     ft.ElevatedButton(width=line_width, height=height_button,
                                       text=time_between_invites_sending_messages,
                                       on_click=lambda _: page.go("/time_between_invites_sending_messages")),
                     # 🔗 Запись ссылки для реакций
                     ft.ElevatedButton(width=line_width, height=height_button, text=recording_reaction_link,
                                       on_click=lambda _: page.go("/recording_reaction_link")),
                     # 📑 Формирование списка чатов / каналов
                     ft.ElevatedButton(width=line_width, height=height_button,
                                       text=forming_list_of_chats_channels,
                                       on_click=lambda _: page.go("/forming_list_of_chats_channels")),
                 ])]))


async def bio_editing_menu(page):
    """
    Меню редактирование БИО

    Аргументы:
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
                     ft.ElevatedButton(width=line_width, height=height_button, text=changing_the_username,
                                       on_click=lambda _: page.go("/changing_username")),
                     # 🖼️ Изменение фото
                     ft.ElevatedButton(width=line_width, height=height_button, text=changing_the_photo,
                                       on_click=lambda _: page.go("/edit_photo")),
                     # ✏️ Изменение описания
                     ft.ElevatedButton(width=line_width, height=height_button, text=changing_the_description,
                                       on_click=lambda _: page.go("/edit_description")),
                     # 📝 Изменение имени
                     ft.ElevatedButton(width=line_width, height=height_button, text=name_change_n,
                                       on_click=lambda _: page.go("/name_change")),
                     # 📝 Изменение фамилии
                     ft.ElevatedButton(width=line_width, height=height_button, text=name_change_f,
                                       on_click=lambda _: page.go("/change_surname")),
                 ])]))


async def inviting_menu(page):
    """
    Меню инвайтинг

    Аргументы:
    :param page: Страница интерфейса Flet для отображения элементов управления.
    """
    page.views.append(
        ft.View("/inviting",
                [ft.AppBar(title=ft.Text(main_menu),
                           bgcolor=ft.colors.SURFACE_VARIANT),
                 ft.Text(spans=[ft.TextSpan(
                     inviting,
                     ft.TextStyle(
                         size=20,
                         weight=ft.FontWeight.BOLD,
                         foreground=ft.Paint(
                             gradient=ft.PaintLinearGradient((0, 20), (150, 20), [ft.colors.PINK,
                                                                                  ft.colors.PURPLE])), ), ), ], ),
                 ft.Column([  # Добавляет все чекбоксы и кнопку на страницу (page) в виде колонок.
                     # 🚀 Инвайтинг
                     ft.ElevatedButton(width=line_width, height=height_button, text=inviting,
                                       on_click=lambda _: page.go("/inviting_without_limits")),
                     # ⏰ Инвайтинг 1 раз в час
                     ft.ElevatedButton(width=line_width, height=height_button, text=invitation_1_time_per_hour,
                                       on_click=lambda _: page.go("/inviting_1_time_per_hour")),
                     # 🕒 Инвайтинг в определенное время
                     ft.ElevatedButton(width=line_width, height=height_button, text=invitation_at_a_certain_time,
                                       on_click=lambda _: page.go("/inviting_certain_time")),
                     # 📅 Инвайтинг каждый день
                     ft.ElevatedButton(width=line_width, height=height_button, text=inviting_every_day,
                                       on_click=lambda _: page.go("/inviting_every_day")),
                 ])]))


async def message_distribution_menu(page):
    """
    Меню рассылка сообщений

    Аргументы:
    :param page: Страница интерфейса Flet для отображения элементов управления.
    """
    page.views.append(
        ft.View("/sending_messages",
                [ft.AppBar(title=ft.Text(main_menu),
                           bgcolor=ft.colors.SURFACE_VARIANT),
                 ft.Text(spans=[ft.TextSpan(
                     sending_messages,
                     ft.TextStyle(
                         size=20,
                         weight=ft.FontWeight.BOLD,
                         foreground=ft.Paint(
                             gradient=ft.PaintLinearGradient((0, 20), (150, 20), [ft.colors.PINK,
                                                                                  ft.colors.PURPLE])), ), ), ], ),
                 ft.Column([  # Добавляет все чекбоксы и кнопку на страницу (page) в виде колонок.
                     # 💬 Рассылка сообщений по чатам
                     ft.ElevatedButton(width=line_width, height=height_button, text=sending_messages_via_chats,
                                       on_click=lambda _: page.go("/sending_messages_via_chats")),
                     # 🤖 Рассылка сообщений по чатам с автоответчиком
                     ft.ElevatedButton(width=line_width, height=height_button,
                                       text=sending_messages_via_chats_with_answering_machine,
                                       on_click=lambda _: page.go(
                                           "/sending_messages_via_chats_with_answering_machine")),
                     # 📂 Рассылка файлов по чатам
                     ft.ElevatedButton(width=line_width, height=height_button, text=sending_files_via_chats,
                                       on_click=lambda _: page.go("/sending_files_via_chats")),
                     # 💬📂 Рассылка сообщений + файлов по чатам
                     ft.ElevatedButton(width=line_width, height=height_button,
                                       text=sending_messages_files_via_chats,
                                       on_click=lambda _: page.go("/sending_messages_files_via_chats")),

                     # 📨 Отправка сообщений в личку
                     ft.ElevatedButton(width=line_width, height=height_button,
                                       text=sending_personal_messages_with_limits,
                                       on_click=lambda _: page.go("/sending_personal_messages_with_limits")),
                     # 📁 Отправка файлов в личку
                     ft.ElevatedButton(width=line_width, height=height_button,
                                       text=sending_files_to_personal_account_with_limits,
                                       on_click=lambda _: page.go("/sending_files_to_personal_account_with_limits")),
                 ])]))


async def working_with_contacts_menu(page):
    """
    Меню работа с контактами

    Аргументы:
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
                     ft.ElevatedButton(width=line_width, height=height_button, text=creating_a_contact_list,
                                       on_click=lambda _: page.go("/creating_contact_list")),
                     # 👥 Показать список контактов
                     ft.ElevatedButton(width=line_width, height=height_button, text=show_a_list_of_contacts,
                                       on_click=lambda _: page.go("/show_list_contacts")),
                     # 🗑️ Удаление контактов
                     ft.ElevatedButton(width=line_width, height=height_button, text=deleting_contacts,
                                       on_click=lambda _: page.go("/deleting_contacts")),
                     # ➕ Добавление контактов
                     ft.ElevatedButton(width=line_width, height=height_button, text=adding_contacts,
                                       on_click=lambda _: page.go("/adding_contacts")),
                 ])]))


async def menu_parsing(page):
    """
    Парсинг меню

    Аргументы:
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
                     ft.ElevatedButton(width=line_width, height=height_button,
                                       text=parse_single_or_multiple_groups,
                                       on_click=lambda _: page.go("/parsing_single_groups")),
                     # 📂 Парсинг выбранной группы из подписанных пользователем
                     ft.ElevatedButton(width=line_width, height=height_button,
                                       text=parse_selected_user_subscribed_group,
                                       on_click=lambda _: page.go("/parsing_selected_group_user_subscribed")),
                     # 👥 Парсинг активных участников группы
                     ft.ElevatedButton(width=line_width, height=height_button,
                                       text=parse_active_group_members,
                                       on_click=lambda _: page.go("/parsing_active_group_members")),
                     # 📜 Парсинг групп / каналов на которые подписан аккаунт
                     ft.ElevatedButton(width=line_width, height=height_button,
                                       text=parse_account_subscribed_groups_channels,
                                       on_click=lambda _: page.go("/parsing_groups_channels_account_subscribed")),
                     # 🗑️ Очистка списка от ранее спарсенных данных
                     ft.ElevatedButton(width=line_width, height=height_button,
                                       text=clear_previously_parsed_data_list,
                                       on_click=lambda _: page.go("/clearing_list_previously_saved_data")),

                     # 📋 Импорт списка от ранее спарсенных данных
                     ft.ElevatedButton(width=line_width, height=height_button,
                                       text=importing_a_list_of_parsed_data,
                                       on_click=lambda _: page.go("/importing_a_list_of_parsed_data")),

                 ])]))


async def reactions_menu(page):
    """
    Меню работа с реакциями

    Аргументы:
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
                     ft.ElevatedButton(width=line_width, height=height_button, text=setting_reactions,
                                       on_click=lambda _: page.go("/setting_reactions")),
                     # 🤖 Автоматическое выставление реакций
                     ft.ElevatedButton(width=line_width, height=height_button,
                                       text=automatic_setting_of_reactions,
                                       on_click=lambda _: page.go("/automatic_setting_of_reactions")),
                 ])]))


async def viewing_posts_menu(page):
    """
    Меню работа с просмотрами

    Аргументы:
    :param page: Страница интерфейса Flet для отображения элементов управления.
    """
    page.views.append(
        ft.View("/viewing_posts_menu",
                [ft.AppBar(title=ft.Text(main_menu),
                           bgcolor=ft.colors.SURFACE_VARIANT),
                 ft.Text(spans=[ft.TextSpan(
                     we_are_winding_up_post_views,
                     ft.TextStyle(
                         size=20,
                         weight=ft.FontWeight.BOLD,
                         foreground=ft.Paint(
                             gradient=ft.PaintLinearGradient((0, 20), (150, 20), [ft.colors.PINK,
                                                                                  ft.colors.PURPLE])), ), ), ], ),
                 ft.Column([  # Добавляет все чекбоксы и кнопку на страницу (page) в виде колонок.
                     # 👁️‍🗨️ Накручиваем просмотры постов
                     ft.ElevatedButton(width=line_width_button, height=height_button,
                                       text=we_are_winding_up_post_views,
                                       on_click=lambda _: page.go("/we_are_winding_up_post_views")),
                 ])]))


async def subscribe_and_unsubscribe_menu(page):
    """
    Меню подписка и отписка

    Аргументы:
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
                     ft.ElevatedButton(width=line_width, height=height_button, text=subscription,
                                       on_click=lambda _: page.go("/subscription_all")),
                     # 🚫 Отписываемся
                     ft.ElevatedButton(width=line_width, height=height_button, text=unsubscribe,
                                       on_click=lambda _: page.go("/unsubscribe_all")),
                 ])]))


async def account_verification_menu(page):
    """
    Меню проверки аккаунтов

    Аргументы:
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
                     ft.ElevatedButton(width=line_width, height=height_button, text=checking_through_a_spam_bot,
                                       on_click=lambda _: page.go("/checking_for_spam_bots")),
                     # ✅ Проверка на валидность
                     ft.ElevatedButton(width=line_width, height=height_button, text=validation_check,
                                       on_click=lambda _: page.go("/validation_check")),
                     # ✏️ Переименование аккаунтов
                     ft.ElevatedButton(width=line_width, height=height_button, text=renaming_accounts,
                                       on_click=lambda _: page.go("/renaming_accounts")),
                     # 🔍 Полная проверка
                     ft.ElevatedButton(width=line_width, height=height_button, text=full_verification,
                                       on_click=lambda _: page.go("/full_verification")),

                 ])]))


async def account_connection_menu(page):
    """
    Меню подключения аккаунтов

    Аргументы:
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
                     ft.ElevatedButton(width=line_width, height=height_button,
                                       text=connecting_accounts_by_phone_number,
                                       on_click=lambda _: page.go("/connecting_accounts_by_number")),
                     # 🔑 Подключение session аккаунтов
                     ft.ElevatedButton(width=line_width, height=height_button, text=connecting_session_accounts,
                                       on_click=lambda _: page.go("/connecting_accounts_by_session")),
                 ])]))


async def connecting_accounts_by_number_menu(page):
    """
    Меню подключения аккаунтов по номеру телефона

    Аргументы:
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
                         [ft.ElevatedButton(width=small_button_width, height=height_button,
                                            text=for_the_answering_machine,
                                            on_click=lambda _: page.go(
                                                "/account_connection_number_answering_machine")),
                          # 📝 Для редактирования BIO
                          ft.ElevatedButton(width=small_button_width, height=height_button,
                                            text=to_edit_bio,
                                            on_click=lambda _: page.go("/account_connection_number_bio"))]),
                     # 📞 Для работы с номерами
                     ft.Row([ft.ElevatedButton(width=small_button_width, height=height_button,
                                               text=to_work_with_numbers,
                                               on_click=lambda _: page.go("/account_connection_number_contact")),
                             # 👥 Для создания групп
                             ft.ElevatedButton(width=small_button_width, height=height_button,
                                               text=to_create_groups,
                                               on_click=lambda _: page.go("/account_connection_number_creating"))]),
                     # 🔗 Для инвайтинга
                     ft.Row([ft.ElevatedButton(width=small_button_width, height=height_button, text=for_inviting,
                                               on_click=lambda _: page.go("/account_connection_number_inviting")),
                             # 📊 Для парсинга
                             ft.ElevatedButton(width=small_button_width, height=height_button, text=for_parsing,
                                               on_click=lambda _: page.go("/account_connection_number_parsing"))]),
                     # 🎭 Для работы с реакциями
                     ft.Row([ft.ElevatedButton(width=small_button_width, height=height_button,
                                               text=to_work_with_reactions,
                                               on_click=lambda _: page.go("/account_connection_number_reactions")),
                             # 👍 Для проставления реакций
                             ft.ElevatedButton(width=small_button_width, height=height_button,
                                               text=for_marking_reactions,
                                               on_click=lambda _: page.go(
                                                   "/account_connection_number_reactions_list"))]),
                     # ✉️ Для рассылки сообщений
                     ft.Row([ft.ElevatedButton(width=small_button_width, height=height_button,
                                               text=to_send_messages,
                                               on_click=lambda _: page.go("/account_connection_number_send_message")),
                             # 🔔 Для подписки
                             ft.ElevatedButton(width=small_button_width, height=height_button, text=to_subscribe,
                                               on_click=lambda _: page.go("/account_connection_number_subscription"))]),
                     # 🚫 Для отписки
                     ft.Row([ft.ElevatedButton(width=small_button_width, height=height_button, text=to_unsubscribe,
                                               on_click=lambda _: page.go("/account_connection_number_unsubscribe")),
                             # 📈 Для накрутки просмотров
                             ft.ElevatedButton(width=small_button_width, height=height_button,
                                               text=to_boost_views,
                                               on_click=lambda _: page.go("/account_connection_number_viewing"))]),

                 ])]))


async def connecting_accounts_by_session_menu(page):
    """
    Меню подключения аккаунтов по номеру телефона

    Аргументы:
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
                         [ft.ElevatedButton(width=small_button_width, height=height_button,
                                            text=for_the_answering_machine,
                                            on_click=lambda _: page.go(
                                                "/account_connection_session_answering_machine")),
                          # 📝 Для редактирования BIO
                          ft.ElevatedButton(width=small_button_width, height=height_button,
                                            text=to_edit_bio,
                                            on_click=lambda _: page.go("/account_connection_session_bio"))]),
                     # 📞 Для работы с номерами
                     ft.Row([ft.ElevatedButton(width=small_button_width, height=height_button,
                                               text=to_work_with_numbers,
                                               on_click=lambda _: page.go("/account_connection_session_contact")),
                             # 👥 Для создания групп
                             ft.ElevatedButton(width=small_button_width, height=height_button,
                                               text=to_create_groups,
                                               on_click=lambda _: page.go("/account_connection_session_creating"))]),
                     # 🔗 Для инвайтинга
                     ft.Row([ft.ElevatedButton(width=small_button_width, height=height_button, text=for_inviting,
                                               on_click=lambda _: page.go("/account_connection_session_inviting")),
                             # 📊 Для парсинга
                             ft.ElevatedButton(width=small_button_width, height=height_button, text=for_parsing,
                                               on_click=lambda _: page.go("/account_connection_session_parsing"))]),
                     # 🎭 Для работы с реакциями
                     ft.Row([ft.ElevatedButton(width=small_button_width, height=height_button,
                                               text=to_work_with_reactions,
                                               on_click=lambda _: page.go("/account_connection_session_reactions")),
                             # 👍 Для проставления реакций
                             ft.ElevatedButton(width=small_button_width, height=height_button,
                                               text=for_marking_reactions,
                                               on_click=lambda _: page.go(
                                                   "/account_connection_session_reactions_list"))]),
                     # ✉️ Для рассылки сообщений
                     ft.Row([ft.ElevatedButton(width=small_button_width, height=height_button,
                                               text=to_send_messages,
                                               on_click=lambda _: page.go(
                                                   "/account_connection_session_send_message")),
                             # 🔔 Для подписки
                             ft.ElevatedButton(width=small_button_width, height=height_button, text=to_subscribe,
                                               on_click=lambda _: page.go(
                                                   "/account_connection_session_subscription"))]),
                     # 🚫 Для отписки
                     ft.Row([ft.ElevatedButton(width=small_button_width, height=height_button, text=to_unsubscribe,
                                               on_click=lambda _: page.go(
                                                   "/account_connection_session_unsubscribe")),
                             # 📈 Для накрутки просмотров
                             ft.ElevatedButton(width=small_button_width, height=height_button,
                                               text=to_boost_views,
                                               on_click=lambda _: page.go("/account_connection_session_viewing"))]),

                 ])]))


async def creating_groups_and_chats_menu(page):
    """
    Меню создания групп и чатов

    Аргументы:
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
                     ft.ElevatedButton(width=line_width_button, height=height_button,
                                       text=creating_groups_chats,
                                       on_click=lambda _: page.go("/creating_groups")),
                 ])]))


async def log_and_display(message: str, lv, page):
    """
    Выводит сообщение в GUI и записывает лог.

    Аргументы:
    :param message: Текст сообщения для отображения и записи в лог.
    :param lv: ListView для отображения сообщений.
    :param page: Страница интерфейса Flet для отображения элементов управления.
    """
    logger.info(message)  # записываем сообщение в лог
    lv.controls.append(ft.Text(message))  # отображаем сообщение в ListView
    page.update()  # обновляем страницу для отображения нового сообщения


async def show_notification(page: ft.Page, message: str):
    """
    Функция для показа уведомления

    Аргументы:
    :param page: Страница интерфейса Flet для отображения элементов управления.
    :param message: Текст уведомления.
    """
    dlg = ft.AlertDialog(
        title=ft.Text(message),
        on_dismiss=lambda e: page.go("/"),  # Переход обратно после закрытия диалога
    )
    page.overlay.append(dlg)
    dlg.open = True
    page.update()
