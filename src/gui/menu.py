# -*- coding: utf-8 -*-
import flet as ft

from src.core.configs import BUTTON_HEIGHT, small_button_width, BUTTON_WIDTH, line_width_button
from src.locales.translations_loader import translations


async def settings_menu(page: ft.Page):
    """
    Меню настройки

    :param page: Страница интерфейса Flet для отображения элементов управления.
    """
    page.views.append(
        ft.View("/settings",
                [ft.AppBar(title=ft.Text(translations["ru"]["menu"]["main"]),
                           bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST),
                 ft.Text(spans=[ft.TextSpan(
                     translations["ru"]["menu"]["settings"],
                     ft.TextStyle(size=20, weight=ft.FontWeight.BOLD, foreground=ft.Paint(
                         gradient=ft.PaintLinearGradient((0, 20), (150, 20), [ft.Colors.PINK, ft.Colors.PURPLE]))))]),
                 ft.Column([  # Добавляет все чекбоксы и кнопку на страницу (page) в виде колонок.
                     ft.Row([
                         # 👍 Выбор реакций
                         ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT,
                                           text=translations["ru"]["menu_settings"]["choice_of_reactions"],
                                           on_click=lambda _: page.go("/choice_of_reactions")),
                         # 🔐 Запись proxy
                         ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT,
                                           text=translations["ru"]["menu_settings"]["proxy_entry"],
                                           on_click=lambda _: page.go("/proxy_entry"))]),
                     ft.Row([
                         # 🔄 Смена аккаунтов
                         ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT,
                                           text=translations["ru"]["menu_settings"]["changing_accounts"],
                                           on_click=lambda _: page.go("/changing_accounts")),
                         # 📝 Запись api_id, api_hash
                         ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT,
                                           text=translations["ru"]["menu_settings"]["recording_api_id_api_hash"],
                                           on_click=lambda _: page.go("/recording_api_id_api_hash"))]),
                     ft.Row([
                         # ⏰ Запись времени
                         ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT,
                                           text=translations["ru"]["menu_settings"]["time_between_subscriptions"],
                                           on_click=lambda _: page.go("/time_between_subscriptions")),
                         # ✉️ Запись сообщений
                         ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT,
                                           text=translations["ru"]["menu_settings"]["message_recording"],
                                           on_click=lambda _: page.go("/message_recording"))]),
                     ft.Row([
                         # 🔗 Запись ссылки для инвайтинга
                         ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT,
                                           text=translations["ru"]["menu_settings"]["link_entry"],
                                           on_click=lambda _: page.go("/link_entry")),
                         # 📊 Лимиты на аккаунт
                         ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT,
                                           text=translations["ru"]["menu_settings"]["account_limits"],
                                           on_click=lambda _: page.go("/account_limits"))]),
                     ft.Row([
                         # 📨 Лимиты на сообщения
                         ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT,
                                           text=translations["ru"]["menu_settings"]["message_limits"],
                                           on_click=lambda _: page.go("/message_limits")),
                         # ⏳ Время между подпиской
                         ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT,
                                           text=translations["ru"]["menu_settings"]["time_between_subscriptionss"],
                                           on_click=lambda _: page.go("/time_between_subscriptionss")), ]),
                     # 📋 Формирование списка username
                     ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
                                       text=translations["ru"]["menu_settings"]["creating_username_list"],
                                       on_click=lambda _: page.go("/creating_username_list")),
                     # ⏱️ Запись времени между сообщениями
                     ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
                                       text=translations["ru"]["menu_settings"]["recording_the_time_between_messages"],
                                       on_click=lambda _: page.go("/recording_the_time_between_messages")),
                     # 🕒 Время между инвайтингом, рассылка сообщений
                     ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
                                       text=translations["ru"]["menu_settings"][
                                           "time_between_invites_sending_messages"],
                                       on_click=lambda _: page.go("/time_between_invites_sending_messages")),
                     # 🔗 Запись ссылки для реакций
                     ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
                                       text=translations["ru"]["menu_settings"]["recording_reaction_link"],
                                       on_click=lambda _: page.go("/recording_reaction_link")),
                     # 📑 Формирование списка чатов / каналов
                     ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
                                       text=translations["ru"]["menu_settings"]["forming_list_of_chats_channels"],
                                       on_click=lambda _: page.go("/forming_list_of_chats_channels")),
                 ])]))


async def bio_editing_menu(page: ft.Page):
    """
    Меню редактирование БИО

    :param page: Страница интерфейса Flet для отображения элементов управления.
    """
    page.views.append(
        ft.View("/bio_editing",
                [ft.AppBar(title=ft.Text(translations["ru"]["menu"]["main"]),
                           bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST),
                 ft.Text(spans=[ft.TextSpan(
                     translations["ru"]["menu"]["edit_bio"],
                     ft.TextStyle(
                         size=20, weight=ft.FontWeight.BOLD,
                         foreground=ft.Paint(
                             gradient=ft.PaintLinearGradient((0, 20), (150, 20), [ft.Colors.PINK,
                                                                                  ft.Colors.PURPLE])), ), ), ], ),
                 ft.Column([  # Добавляет все чекбоксы и кнопку на страницу (page) в виде колонок.
                     # 🔄 Изменение username
                     ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
                                       text=translations["ru"]["edit_bio_menu"]["changing_the_username"],
                                       on_click=lambda _: page.go("/changing_username")),
                     # 🖼️ Изменение фото
                     ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
                                       text=translations["ru"]["edit_bio_menu"]["changing_the_photo"],
                                       on_click=lambda _: page.go("/edit_photo")),
                     # ✏️ Изменение описания
                     ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
                                       text=translations["ru"]["edit_bio_menu"]["changing_the_description"],
                                       on_click=lambda _: page.go("/edit_description")),
                     # 📝 Изменение имени
                     ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
                                       text=translations["ru"]["edit_bio_menu"]["name_change_n"],
                                       on_click=lambda _: page.go("/name_change")),
                     # 📝 Изменение фамилии
                     ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
                                       text=translations["ru"]["edit_bio_menu"]["name_change_f"],
                                       on_click=lambda _: page.go("/change_surname")),
                 ])]))


async def inviting_menu(page: ft.Page):
    """
    Меню инвайтинг

    :param page: Страница интерфейса Flet для отображения элементов управления.
    """
    page.views.append(
        ft.View("/inviting",
                [ft.AppBar(title=ft.Text(translations["ru"]["menu"]["main"]),
                           bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST),
                 ft.Text(spans=[ft.TextSpan(
                     translations["ru"]["inviting_menu"]["inviting"],
                     ft.TextStyle(
                         size=20, weight=ft.FontWeight.BOLD,
                         foreground=ft.Paint(
                             gradient=ft.PaintLinearGradient((0, 20), (150, 20), [ft.Colors.PINK,
                                                                                  ft.Colors.PURPLE])), ), ), ], ),
                 ft.Column([  # Добавляет все чекбоксы и кнопку на страницу (page) в виде колонок.
                     # 🚀 Инвайтинг
                     ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
                                       text=translations["ru"]["inviting_menu"]["inviting"],
                                       on_click=lambda _: page.go("/inviting_without_limits")),
                     # ⏰ Инвайтинг 1 раз в час
                     ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
                                       text=translations["ru"]["inviting_menu"]["invitation_1_time_per_hour"],
                                       on_click=lambda _: page.go("/inviting_1_time_per_hour")),
                     # 🕒 Инвайтинг в определенное время
                     ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
                                       text=translations["ru"]["inviting_menu"]["invitation_at_a_certain_time"],
                                       on_click=lambda _: page.go("/inviting_certain_time")),
                     # 📅 Инвайтинг каждый день
                     ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
                                       text=translations["ru"]["inviting_menu"]["inviting_every_day"],
                                       on_click=lambda _: page.go("/inviting_every_day")),
                 ])]))


async def working_with_contacts_menu(page: ft.Page):
    """
    Меню работа с контактами

    :param page: Страница интерфейса Flet для отображения элементов управления.
    """
    page.views.append(
        ft.View("/working_with_contacts",
                [ft.AppBar(title=ft.Text(translations["ru"]["menu"]["main"]),
                           bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST),
                 ft.Text(spans=[ft.TextSpan(
                     translations["ru"]["menu"]["contacts"],
                     ft.TextStyle(
                         size=20, weight=ft.FontWeight.BOLD,
                         foreground=ft.Paint(
                             gradient=ft.PaintLinearGradient((0, 20), (150, 20), [ft.Colors.PINK,
                                                                                  ft.Colors.PURPLE])), ), ), ], ),
                 ft.Column([  # Добавляет все чекбоксы и кнопку на страницу (page) в виде колонок.
                     # 📋 Формирование списка контактов
                     ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
                                       text=translations["ru"]["contacts_menu"]["creating_a_contact_list"],
                                       on_click=lambda _: page.go("/creating_contact_list")),
                     # 👥 Показать список контактов
                     ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
                                       text=translations["ru"]["contacts_menu"]["show_a_list_of_contacts"],
                                       on_click=lambda _: page.go("/show_list_contacts")),
                     # 🗑️ Удаление контактов
                     ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
                                       text=translations["ru"]["contacts_menu"]["deleting_contacts"],
                                       on_click=lambda _: page.go("/deleting_contacts")),
                     # ➕ Добавление контактов
                     ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
                                       text=translations["ru"]["contacts_menu"]["adding_contacts"],
                                       on_click=lambda _: page.go("/adding_contacts")),
                 ])]))


async def menu_parsing(page: ft.Page):
    """
    Парсинг меню

    :param page: Страница интерфейса Flet для отображения элементов управления.
    """
    page.views.append(
        ft.View("/parsing",
                [ft.AppBar(title=ft.Text(translations["ru"]["menu"]["main"]),
                           bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST),
                 ft.Text(spans=[ft.TextSpan(
                     translations["ru"]["menu"]["parsing"],
                     ft.TextStyle(
                         size=20, weight=ft.FontWeight.BOLD,
                         foreground=ft.Paint(
                             gradient=ft.PaintLinearGradient((0, 20), (150, 20), [ft.Colors.PINK,
                                                                                  ft.Colors.PURPLE])), ), ), ], ),
                 ft.Column([  # Добавляет все чекбоксы и кнопку на страницу (page) в виде колонок.
                     # 🔍 Парсинг одной группы / групп
                     ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
                                       text=translations["ru"]["parsing_menu"]["parse_single_or_multiple_groups"],
                                       on_click=lambda _: page.go("/parsing_single_groups")),
                     # 📂 Парсинг выбранной группы из подписанных пользователем
                     ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
                                       text=translations["ru"]["parsing_menu"]["parse_selected_user_subscribed_group"],
                                       on_click=lambda _: page.go("/parsing_selected_group_user_subscribed")),
                     # 👥 Парсинг активных участников группы
                     ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
                                       text=translations["ru"]["parsing_menu"]["parse_active_group_members"],
                                       on_click=lambda _: page.go("/parsing_active_group_members")),
                     # 📋 Импорт списка от ранее спарсенных данных
                     ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
                                       text=translations["ru"]["parsing_menu"]["importing_a_list_of_parsed_data"],
                                       on_click=lambda _: page.go("/importing_a_list_of_parsed_data")),
                     # 📑 Формирование списка чатов / каналов
                     ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
                                       text=translations["ru"]["menu_settings"]["forming_list_of_chats_channels"],
                                       on_click=lambda _: page.go("/forming_list_of_chats_channels")),
                 ])]))


async def reactions_menu(page: ft.Page):
    """
    Меню работа с реакциями

    :param page: Страница интерфейса Flet для отображения элементов управления.
    """
    page.views.append(
        ft.View("/working_with_reactions",
                [ft.AppBar(title=ft.Text(translations["ru"]["menu"]["main"]),
                           bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST),
                 ft.Text(spans=[ft.TextSpan(
                     translations["ru"]["menu"]["reactions"],
                     ft.TextStyle(
                         size=20, weight=ft.FontWeight.BOLD,
                         foreground=ft.Paint(
                             gradient=ft.PaintLinearGradient((0, 20), (150, 20), [ft.Colors.PINK,
                                                                                  ft.Colors.PURPLE])), ), ), ], ),
                 ft.Column([  # Добавляет все чекбоксы и кнопку на страницу (page) в виде колонок.
                     # 👍 Ставим реакции
                     ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
                                       text=translations["ru"]["reactions_menu"]["setting_reactions"],
                                       on_click=lambda _: page.go("/setting_reactions")),
                     # 🤖 Автоматическое выставление реакций
                     ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
                                       text=translations["ru"]["reactions_menu"]["automatic_setting_of_reactions"],
                                       on_click=lambda _: page.go("/automatic_setting_of_reactions")),
                 ])]))


async def viewing_posts_menu(page: ft.Page):
    """
    Меню работа с просмотрами

    :param page: Страница интерфейса Flet для отображения элементов управления.
    """
    page.views.append(
        ft.View("/viewing_posts_menu",
                [ft.AppBar(title=ft.Text(translations["ru"]["menu"]["main"]),
                           bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST),
                 ft.Text(spans=[ft.TextSpan(
                     translations["ru"]["reactions_menu"]["we_are_winding_up_post_views"],
                     ft.TextStyle(
                         size=20, weight=ft.FontWeight.BOLD,
                         foreground=ft.Paint(
                             gradient=ft.PaintLinearGradient((0, 20), (150, 20), [ft.Colors.PINK,
                                                                                  ft.Colors.PURPLE])), ), ), ], ),
                 ft.Column([  # Добавляет все чекбоксы и кнопку на страницу (page) в виде колонок.
                     # 👁️‍🗨️ Накручиваем просмотры постов
                     ft.ElevatedButton(width=line_width_button, height=BUTTON_HEIGHT,
                                       text=translations["ru"]["reactions_menu"]["we_are_winding_up_post_views"],
                                       on_click=lambda _: page.go("/we_are_winding_up_post_views")),
                 ])]))


async def subscribe_and_unsubscribe_menu(page: ft.Page):
    """
    Меню подписка и отписка

    :param page: Страница интерфейса Flet для отображения элементов управления.
    """
    page.views.append(
        ft.View("/subscribe_unsubscribe",
                [ft.AppBar(title=ft.Text(translations["ru"]["menu"]["main"]),
                           bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST),
                 ft.Text(spans=[ft.TextSpan(
                     translations["ru"]["menu"]["subscribe_unsubscribe"],
                     ft.TextStyle(
                         size=20, weight=ft.FontWeight.BOLD,
                         foreground=ft.Paint(
                             gradient=ft.PaintLinearGradient((0, 20), (150, 20), [ft.Colors.PINK,
                                                                                  ft.Colors.PURPLE])), ), ), ], ),
                 ft.Column([  # Добавляет все чекбоксы и кнопку на страницу (page) в виде колонок.
                     # 🔔 Подписка
                     ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
                                       text=translations["ru"]["subscribe_unsubscribe_menu"]["subscription"],
                                       on_click=lambda _: page.go("/subscription_all")),
                     # 🚫 Отписываемся
                     ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
                                       text=translations["ru"]["subscribe_unsubscribe_menu"]["unsubscribe"],
                                       on_click=lambda _: page.go("/unsubscribe_all")),
                 ])]))


async def account_connection_menu(page: ft.Page):
    """
    Меню подключения аккаунтов

    :param page: Страница интерфейса Flet для отображения элементов управления.
    """
    page.views.append(
        ft.View("/account_connection_menu",
                [ft.AppBar(title=ft.Text(translations["ru"]["menu"]["main"]),
                           bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST),
                 ft.Text(spans=[ft.TextSpan(
                     translations["ru"]["menu"]["account_connect"],
                     ft.TextStyle(
                         size=20,
                         weight=ft.FontWeight.BOLD,
                         foreground=ft.Paint(
                             gradient=ft.PaintLinearGradient((0, 20), (150, 20), [ft.Colors.PINK,
                                                                                  ft.Colors.PURPLE])), ), ), ], ),
                 ft.Column([  # Добавляет все чекбоксы и кнопку на страницу (page) в виде колонок.
                     # 📞 Подключение аккаунтов по номеру телефона
                     ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
                                       text=translations["ru"]["account_connect_menu"][
                                           "connecting_accounts_by_phone_number"],
                                       on_click=lambda _: page.go("/connecting_accounts_by_number")),
                     # 🔑 Подключение session аккаунтов
                     ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
                                       text=translations["ru"]["account_connect_menu"]["connecting_session_accounts"],
                                       on_click=lambda _: page.go("/connecting_accounts_by_session")),
                 ])]))


async def connecting_accounts_by_number_menu(page: ft.Page):
    """
    Меню подключения аккаунтов по номеру телефона

    :param page: Страница интерфейса Flet для отображения элементов управления.
    """
    page.views.append(
        ft.View("/connecting_accounts_by_number",
                [ft.AppBar(title=ft.Text(translations["ru"]["menu"]["main"]),
                           bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST),
                 ft.Text(spans=[ft.TextSpan(
                     translations["ru"]["account_connect_menu"]["connecting_accounts_by_phone_number"],
                     ft.TextStyle(
                         size=20,
                         weight=ft.FontWeight.BOLD,
                         foreground=ft.Paint(
                             gradient=ft.PaintLinearGradient((0, 20), (150, 20), [ft.Colors.PINK,
                                                                                  ft.Colors.PURPLE])), ), ), ], ),
                 ft.Column([  # Добавляет все чекбоксы и кнопку на страницу (page) в виде колонок.

                     ft.Row(
                         # 🤖 Для автоответчика
                         [ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT,
                                            text=translations["ru"]["account_connection_menu"][
                                                "for_the_answering_machine"],
                                            on_click=lambda _: page.go(
                                                "/account_connection_number_answering_machine")),
                          # 📝 Для редактирования BIO
                          ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT,
                                            text=translations["ru"]["account_connection_menu"]["to_edit_bio"],
                                            on_click=lambda _: page.go("/account_connection_number_bio"))]),
                     # 📞 Для работы с номерами
                     ft.Row([ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT,
                                               text=translations["ru"]["account_connection_menu"][
                                                   "to_work_with_numbers"],
                                               on_click=lambda _: page.go("/account_connection_number_contact")),
                             # 👥 Для создания групп
                             ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT,
                                               text=translations["ru"]["account_connection_menu"]["to_create_groups"],
                                               on_click=lambda _: page.go("/account_connection_number_creating"))]),
                     # 🔗 Для инвайтинга
                     ft.Row([ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT,
                                               text=translations["ru"]["account_connection_menu"]["for_inviting"],
                                               on_click=lambda _: page.go("/account_connection_number_inviting")),
                             # 📊 Для парсинга
                             ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT,
                                               text=translations["ru"]["account_connection_menu"]["for_parsing"],
                                               on_click=lambda _: page.go("/account_connection_number_parsing"))]),
                     # 🎭 Для работы с реакциями
                     ft.Row([ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT,
                                               text=translations["ru"]["account_connection_menu"][
                                                   "to_work_with_reactions"],
                                               on_click=lambda _: page.go("/account_connection_number_reactions")),
                             # 👍 Для проставления реакций
                             ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT,
                                               text=translations["ru"]["account_connection_menu"][
                                                   "for_marking_reactions"],
                                               on_click=lambda _: page.go(
                                                   "/account_connection_number_reactions_list"))]),
                     # ✉️ Для рассылки сообщений
                     ft.Row([ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT,
                                               text=translations["ru"]["account_connection_menu"]["to_send_messages"],
                                               on_click=lambda _: page.go("/account_connection_number_send_message")),
                             # 🔔 Для подписки
                             ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT,
                                               text=translations["ru"]["account_connection_menu"]["to_subscribe"],
                                               on_click=lambda _: page.go("/account_connection_number_subscription"))]),
                     # 🚫 Для отписки
                     ft.Row([ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT,
                                               text=translations["ru"]["account_connection_menu"]["to_unsubscribe"],
                                               on_click=lambda _: page.go("/account_connection_number_unsubscribe")),
                             # 📈 Для накрутки просмотров
                             ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT,
                                               text=translations["ru"]["account_connection_menu"]["to_boost_views"],
                                               on_click=lambda _: page.go("/account_connection_number_viewing"))]),

                 ])]))


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
