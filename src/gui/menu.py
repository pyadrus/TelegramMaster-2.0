# -*- coding: utf-8 -*-
import flet as ft

from src.core.configs import BUTTON_HEIGHT, small_button_width, BUTTON_WIDTH, line_width_button
from src.features.account.parsing.gui_elements import GUIProgram
from src.locales.translations_loader import translations


async def settings_menu(page: ft.Page):
    """
    Меню настройки

    :param page: Страница интерфейса Flet для отображения элементов управления.
    """
    page.views.append(
        ft.View("/settings",
                [await GUIProgram().key_app_bar(),
                 ft.Text(spans=[ft.TextSpan(translations["ru"]["menu"]["settings"],
                                            ft.TextStyle(size=20, weight=ft.FontWeight.BOLD, foreground=ft.Paint(
                                                gradient=ft.PaintLinearGradient((0, 20), (150, 20), [ft.Colors.PINK,
                                                                                                     ft.Colors.PURPLE]))))]),
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
                [await GUIProgram().key_app_bar(),
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


async def working_with_contacts_menu(page: ft.Page):
    """
    Меню работа с контактами

    :param page: Страница интерфейса Flet для отображения элементов управления.
    """
    page.views.append(
        ft.View("/working_with_contacts",
                [await GUIProgram().key_app_bar(),
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


async def reactions_menu(page: ft.Page):
    """
    Меню работа с реакциями

    :param page: Страница интерфейса Flet для отображения элементов управления.
    """
    page.views.append(
        ft.View("/working_with_reactions",
                [await GUIProgram().key_app_bar(),
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
                [await GUIProgram().key_app_bar(),
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
                [await GUIProgram().key_app_bar(),
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



