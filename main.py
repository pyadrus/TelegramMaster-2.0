# -*- coding: utf-8 -*-
import flet as ft
from loguru import logger

from system.account_actions.TGAccountBIO import AccountBIO
from system.account_actions.TGChecking import AccountVerification
from system.account_actions.TGConnect import TGConnect
from system.account_actions.TGContact import TGContact
from system.account_actions.TGCreating import CreatingGroupsAndChats
from system.account_actions.TGInviting import InvitingToAGroup
from system.account_actions.TGInvitingScheduler import launching_an_invite_once_an_hour, \
    launching_invite_every_day_certain_time, schedule_invite
from system.account_actions.TGParsing import ParsingGroupMembers
from system.account_actions.TGReactions import WorkingWithReactions
from system.account_actions.TGSendingMessages import SendTelegramMessages
from system.account_actions.TGSubUnsub import SubscribeUnsubscribeTelegram
from system.auxiliary_functions.auxiliary_functions import find_files
from system.auxiliary_functions.global_variables import ConfigReader
from system.setting.setting import SettingPage
from system.setting.setting import reaction_gui
from system.sqlite_working_tools.sqlite_working_tools import DatabaseHandler

logger.add("user_settings/log/log.log", rotation="1 MB", compression="zip")  # Логирование программы

line_width = 580  # Ширина окна и ширина строки
program_version, date_of_program_change = "2.0.5", "22.07.2024"  # Версия программы, дата изменения


def mainss(page: ft.Page):
    page.title = f"TelegramMaster: {program_version} (Дата изменения {date_of_program_change})"
    page.window_width = line_width  # window's ширина is 200 px
    page.window_height = 700  # window's высота is 200 px
    page.window_resizable = False  # window is not resizable

    # width - ширина,  # height - высота
    async def route_change(route):
        page.views.clear()

        # Меню "Главное меню"

        page.views.append(
            ft.View("/", [ft.AppBar(title=ft.Text("Главное меню"),
                                    bgcolor=ft.colors.SURFACE_VARIANT),
                          ft.Text(spans=[ft.TextSpan(
                              "TelegramMaster 2.0",
                              ft.TextStyle(
                                  size=40,
                                  weight=ft.FontWeight.BOLD,
                                  foreground=ft.Paint(
                                      gradient=ft.PaintLinearGradient((0, 20), (150, 20), [ft.colors.PINK,
                                                                                           ft.colors.PURPLE])), ), ), ], ),
                          ft.Text(disabled=False,
                                  spans=[ft.TextSpan("Аккаунт  Telegram: "),
                                         ft.TextSpan("https://t.me/PyAdminRU",
                                                     ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE),
                                                     url="https://t.me/PyAdminRU", ), ], ),
                          ft.Text(disabled=False,
                                  spans=[ft.TextSpan("Канал Telegram: "),
                                         ft.TextSpan("https://t.me/master_tg_d",
                                                     ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE),
                                                     url="https://t.me/master_tg_d", ), ], ),
                          ft.ElevatedButton(width=line_width, height=30, text="Инвайтинг",
                                            on_click=lambda _: page.go("/inviting")),
                          ft.ElevatedButton(width=line_width, height=30, text="Парсинг",
                                            on_click=lambda _: page.go("/parsing")),
                          ft.ElevatedButton(width=line_width, height=30, text="Работа с контактами",
                                            on_click=lambda _: page.go("/working_with_contacts")),
                          ft.ElevatedButton(width=line_width, height=30, text="Подписка, отписка",
                                            on_click=lambda _: page.go("/subscribe_unsubscribe")),
                          ft.ElevatedButton(width=line_width, height=30, text="Подключение аккаунтов",
                                            on_click=lambda _: page.go("/connecting_accounts")),
                          ft.ElevatedButton(width=line_width, height=30, text="Рассылка сообщений",
                                            on_click=lambda _: page.go("/sending_messages")),
                          ft.ElevatedButton(width=line_width, height=30, text="Работа с реакциями",
                                            on_click=lambda _: page.go("/working_with_reactions")),
                          ft.ElevatedButton(width=line_width, height=30, text="Проверка аккаунтов",
                                            on_click=lambda _: page.go("/checking_accounts")),
                          ft.ElevatedButton(width=line_width, height=30, text="Создание групп (чатов)",
                                            on_click=lambda _: page.go("/creating_groups")),
                          ft.ElevatedButton(width=line_width, height=30, text="Редактирование_BIO",
                                            on_click=lambda _: page.go("/bio_editing")),
                          ft.ElevatedButton(width=line_width, height=30, text="Настройки",
                                            on_click=lambda _: page.go("/settings")),
                          ], ))

        if page.route == "/inviting":  # Меню "Инвайтинг"
            page.views.append(
                ft.View("/inviting",
                        [ft.AppBar(title=ft.Text("Главное меню"),
                                   bgcolor=ft.colors.SURFACE_VARIANT),
                         ft.Column([  # Добавляет все чекбоксы и кнопку на страницу (page) в виде колонок.
                             ft.ElevatedButton(width=line_width, height=30, text="Инвайтинг без лимитов",
                                               on_click=lambda _: page.go("/inviting_without_limits")),
                             ft.ElevatedButton(width=line_width, height=30, text="Инвайтинг с лимитами",
                                               on_click=lambda _: page.go("/inviting_with_limits")),
                             ft.ElevatedButton(width=line_width, height=30, text="Инвайтинг 1 раз в час",
                                               on_click=lambda _: page.go("/inviting_1_time_per_hour")),
                             ft.ElevatedButton(width=line_width, height=30, text="Инвайтинг в определенное время",
                                               on_click=lambda _: page.go("/inviting_certain_time")),
                             ft.ElevatedButton(width=line_width, height=30, text="Инвайтинг каждый день",
                                               on_click=lambda _: page.go("/inviting_every_day")),
                         ])]))
        elif page.route == "/inviting_without_limits":  # Инвайтинг без лимитов
            await InvitingToAGroup().inviting_without_limits(account_limits=None)  # Вызываем метод для инвайтинга
        elif page.route == "/inviting_with_limits":  # Инвайтинг с лимитами
            config_reader = ConfigReader()
            account_limits = config_reader.get_limits()
            await InvitingToAGroup().inviting_without_limits(
                account_limits=account_limits)  # Вызываем метод для инвайтинга
        elif page.route == "/inviting_1_time_per_hour":  # Инвайтинг 1 раз в час
            launching_an_invite_once_an_hour()
        elif page.route == "/inviting_certain_time":  # Инвайтинг в определенное время
            schedule_invite()
        elif page.route == "/inviting_every_day":  # Инвайтинг каждый день
            launching_invite_every_day_certain_time()
        elif page.route == "/checking_accounts":  # Проверка аккаунтов
            await AccountVerification().check_account_for_spam()

        elif page.route == "/subscribe_unsubscribe":  # Меню "Подписка и отписка"
            page.views.append(
                ft.View("/subscribe_unsubscribe",
                        [ft.AppBar(title=ft.Text("Главное меню"),
                                   bgcolor=ft.colors.SURFACE_VARIANT),
                         ft.Column([  # Добавляет все чекбоксы и кнопку на страницу (page) в виде колонок.
                             ft.ElevatedButton(width=line_width, height=30, text="Подписка",
                                               on_click=lambda _: page.go("/subscription_all")),
                             ft.ElevatedButton(width=line_width, height=30, text="Отписываемся",
                                               on_click=lambda _: page.go("/unsubscribe_all")),
                         ])]))
        elif page.route == "/subscription_all":  # Подписка
            await SubscribeUnsubscribeTelegram().subscribe_telegram()
        elif page.route == "/unsubscribe_all":  # Отписываемся
            await SubscribeUnsubscribeTelegram().unsubscribe_all()

        elif page.route == "/working_with_reactions":  # Меню "Работа с реакциями"
            page.views.append(
                ft.View("/working_with_reactions",
                        [ft.AppBar(title=ft.Text("Главное меню"),
                                   bgcolor=ft.colors.SURFACE_VARIANT),
                         ft.Column([  # Добавляет все чекбоксы и кнопку на страницу (page) в виде колонок.
                             ft.ElevatedButton(width=line_width, height=30, text="Ставим реакции",
                                               on_click=lambda _: page.go("/setting_reactions")),
                             ft.ElevatedButton(width=line_width, height=30, text="Накручиваем просмотры постов",
                                               on_click=lambda _: page.go("/we_are_winding_up_post_views")),
                             ft.ElevatedButton(width=line_width, height=30, text="Автоматическое выставление реакций",
                                               on_click=lambda _: page.go("/automatic_setting_of_reactions")),
                         ])]))
        elif page.route == "/setting_reactions":  # Ставим реакции
            await WorkingWithReactions().send_reaction_request()  # Вызываем метод для выбора реакции и установки её на сообщение
        elif page.route == "/we_are_winding_up_post_views":  # Накручиваем просмотры постов
            await WorkingWithReactions().viewing_posts()
        elif page.route == "/automatic_setting_of_reactions":  # Автоматическое выставление реакций
            await WorkingWithReactions().setting_reactions()  # Автоматическое выставление реакций

        elif page.route == "/parsing":  # Меню "Парсинг"
            page.views.append(
                ft.View("/parsing",
                        [ft.AppBar(title=ft.Text("Главное меню"),
                                   bgcolor=ft.colors.SURFACE_VARIANT),
                         ft.Column([  # Добавляет все чекбоксы и кнопку на страницу (page) в виде колонок.
                             ft.ElevatedButton(width=line_width, height=30,
                                               text="Парсинг одной группы / групп",
                                               on_click=lambda _: page.go("/parsing_single_groups")),
                             ft.ElevatedButton(width=line_width, height=30,
                                               text="Парсинг выбранной группы из подписанных пользователем",
                                               on_click=lambda _: page.go("/parsing_selected_group_user_subscribed")),
                             ft.ElevatedButton(width=line_width, height=30,
                                               text="Парсинг активных участников группы",
                                               on_click=lambda _: page.go("/parsing_active_group_members")),
                             ft.ElevatedButton(width=line_width, height=30,
                                               text="Парсинг групп / каналов на которые подписан аккаунт",
                                               on_click=lambda _: page.go(
                                                   "/parsing_groups_channels_account_subscribed")),
                             ft.ElevatedButton(width=line_width, height=30,
                                               text="Очистка списка от ранее спарсенных данных",
                                               on_click=lambda _: page.go("/clearing_list_previously_saved_data")),
                         ])]))

        elif page.route == "/parsing_single_groups":  # Парсинг одной группы / групп
            await ParsingGroupMembers().parse_groups()
        elif page.route == "/parsing_selected_group_user_subscribed":  # Парсинг выбранной группы из подписанных пользователем
            await ParsingGroupMembers().choose_group_for_parsing()
        elif page.route == "/parsing_active_group_members":  # Парсинг активных участников группы
            chat_input = input(f"{logger.info('[+] Введите ссылку на чат с которого будем собирать активных: ')}")
            limit_active_user = input(f"{logger.info('[+] Введите количество сообщений которые будем parsing: ')}")
            await ParsingGroupMembers().parse_active_users(chat_input, int(limit_active_user))
        elif page.route == "/parsing_groups_channels_account_subscribed":  # Парсинг групп / каналов на которые подписан аккаунт
            await ParsingGroupMembers().parse_subscribed_groups()
        elif page.route == "/clearing_list_previously_saved_data":  # Очистка списка от ранее спарсенных данных
            await DatabaseHandler().cleaning_db(name_database_table="members")

        elif page.route == "/working_with_contacts":  # Меню "Работа с контактами"
            page.views.append(
                ft.View("/working_with_contacts",
                        [ft.AppBar(title=ft.Text("Главное меню"),
                                   bgcolor=ft.colors.SURFACE_VARIANT),
                         ft.Column([  # Добавляет все чекбоксы и кнопку на страницу (page) в виде колонок.
                             ft.ElevatedButton(width=line_width, height=30, text="Формирование списка контактов",
                                               on_click=lambda _: page.go("/creating_contact_list")),
                             ft.ElevatedButton(width=line_width, height=30, text="Показать список контактов",
                                               on_click=lambda _: page.go("/show_list_contacts")),
                             ft.ElevatedButton(width=line_width, height=30, text="Удаление контактов",
                                               on_click=lambda _: page.go("/deleting_contacts")),
                             ft.ElevatedButton(width=line_width, height=30, text="Добавление контактов",
                                               on_click=lambda _: page.go("/adding_contacts")),
                         ])]))
        elif page.route == "/creating_contact_list":  # Формирование списка контактов
            await DatabaseHandler().open_and_read_data("contact")  # Удаление списка с контактами
            SettingPage().output_the_input_field(page, "Введите список номеров телефонов", "contact",
                                                 "contact", "/working_with_contacts", "contact")
        elif page.route == "/show_list_contacts":  # Показать список контактов
            await TGContact().show_account_contact_list()
        elif page.route == "/deleting_contacts":  # Удаление контактов
            await TGContact().delete_contact()
        elif page.route == "/adding_contacts":  # Добавление контактов
            await TGContact().inviting_contact()
        elif page.route == "/connecting_accounts":  # Подключение новых аккаунтов, методом ввода нового номера телефона
            TG_Connect = TGConnect()
            await TG_Connect.telegram_connect()
        elif page.route == "/creating_groups":  # Создание групп (чатов)
            await CreatingGroupsAndChats().creating_groups_and_chats()

        elif page.route == "/sending_messages":  # Меню "Рассылка сообщений"
            page.views.append(
                ft.View("/sending_messages",
                        [ft.AppBar(title=ft.Text("Главное меню"),
                                   bgcolor=ft.colors.SURFACE_VARIANT),
                         ft.Column([  # Добавляет все чекбоксы и кнопку на страницу (page) в виде колонок.
                             ft.ElevatedButton(width=line_width, height=30, text="Отправка сообщений в личку",
                                               on_click=lambda _: page.go("/sending_messages_personal_account")),
                             ft.ElevatedButton(width=line_width, height=30, text="Отправка файлов в личку",
                                               on_click=lambda _: page.go("/sending_files_personal_account")),
                             ft.ElevatedButton(width=line_width, height=30, text="Рассылка сообщений по чатам",
                                               on_click=lambda _: page.go("/sending_messages_via_chats")),
                             ft.ElevatedButton(width=line_width, height=30,
                                               text="Рассылка сообщений по чатам с автоответчиком",
                                               on_click=lambda _: page.go(
                                                   "/sending_messages_via_chats_with_answering_machine")),
                             ft.ElevatedButton(width=line_width, height=30, text="Рассылка файлов по чатам",
                                               on_click=lambda _: page.go("/sending_files_via_chats")),
                             ft.ElevatedButton(width=line_width, height=30, text="Рассылка сообщений + файлов по чатам",
                                               on_click=lambda _: page.go("/sending_messages_files_via_chats")),
                             ft.ElevatedButton(width=line_width, height=30,
                                               text="Отправка сообщений в личку (с лимитами)",
                                               on_click=lambda _: page.go("/sending_personal_messages_with_limits")),
                             ft.ElevatedButton(width=line_width, height=30, text="Отправка файлов в личку (с лимитами)",
                                               on_click=lambda _: page.go(
                                                   "/sending_files_to_personal_account_with_limits")),
                         ])]))
        elif page.route == "/sending_messages_personal_account":  # Отправка сообщений в личку
            logger.info(f"Лимит на аккаунт (без ограничений)")
            await SendTelegramMessages().send_message_from_all_accounts(account_limits=None)
        elif page.route == "/sending_files_personal_account":  # Отправка файлов в личку
            logger.info(f"Лимит на аккаунт (без ограничений)")
            await SendTelegramMessages().send_files_to_personal_chats(account_limits=None)
        elif page.route == "/sending_messages_via_chats":  # Рассылка сообщений по чатам
            entities = find_files(directory_path="user_settings/message", extension="json")
            logger.info(entities)
            await SendTelegramMessages().sending_messages_via_chats_times()
        elif page.route == "/sending_messages_via_chats_with_answering_machine":  # Рассылка сообщений по чатам с автоответчиком
            await SendTelegramMessages().answering_machine()
        elif page.route == "/sending_files_via_chats":  # Рассылка файлов по чатам
            await SendTelegramMessages().sending_files_via_chats()
        elif page.route == "/sending_messages_files_via_chats":  # Рассылка сообщений + файлов по чатам
            await SendTelegramMessages().sending_messages_files_via_chats()
        elif page.route == "/sending_personal_messages_with_limits":  # Отправка сообщений в личку (с лимитами)
            account_limits = ConfigReader().get_limits()
            await SendTelegramMessages().send_message_from_all_accounts(account_limits=account_limits)
        elif page.route == "/sending_files_to_personal_account_with_limits":  # Отправка файлов в личку (с лимитами)
            account_limits = ConfigReader().get_limits()
            await SendTelegramMessages().send_files_to_personal_chats(account_limits=account_limits)

        elif page.route == "/bio_editing":  # Меню "Редактирование_BIO"
            page.views.append(
                ft.View("/bio_editing",
                        [ft.AppBar(title=ft.Text("Главное меню"),
                                   bgcolor=ft.colors.SURFACE_VARIANT),
                         ft.Column([  # Добавляет все чекбоксы и кнопку на страницу (page) в виде колонок.
                             ft.ElevatedButton(width=line_width, height=30, text="Изменение username",
                                               on_click=lambda _: page.go("/changing_username")),
                             ft.ElevatedButton(width=line_width, height=30, text="Изменение фото",
                                               on_click=lambda _: page.go("/edit_photo")),
                             ft.ElevatedButton(width=line_width, height=30, text="Изменение описания",
                                               on_click=lambda _: page.go("/edit_description")),
                             ft.ElevatedButton(width=line_width, height=30, text="Изменение имени",
                                               on_click=lambda _: page.go("/name_change")),
                             ft.ElevatedButton(width=line_width, height=30, text="Изменение фамилии",
                                               on_click=lambda _: page.go("/change_surname")),
                         ])]))

        elif page.route == "/edit_description":  # Изменение описания
            await AccountBIO().change_bio_profile_gui(page)
        elif page.route == "/name_change":  # Изменение имени
            await AccountBIO().change_name_profile_gui(page)
        elif page.route == "/change_surname":  # Изменение фамилии
            await AccountBIO().change_last_name_profile_gui(page)
        elif page.route == "/edit_photo":  # Изменение фото
            await AccountBIO().change_photo_profile()
        elif page.route == "/changing_username":  # Изменение username
            await AccountBIO().change_username_profile_gui(page)

        elif page.route == "/settings":  # Меню "Настройки TelegramMaster"
            page.views.append(
                ft.View("/settings",
                        [ft.AppBar(title=ft.Text("Главное меню"),
                                   bgcolor=ft.colors.SURFACE_VARIANT),
                         ft.Column([  # Добавляет все чекбоксы и кнопку на страницу (page) в виде колонок.
                             ft.Row([ft.ElevatedButton(width=270, height=30, text="Выбор реакций",
                                                       on_click=lambda _: page.go("/choice_of_reactions")),
                                     ft.ElevatedButton(width=270, height=30, text="Запись proxy",
                                                       on_click=lambda _: page.go("/proxy_entry"))]),
                             ft.Row([ft.ElevatedButton(width=270, height=30, text="Смена аккаунтов",
                                                       on_click=lambda _: page.go("/changing_accounts")),
                                     ft.ElevatedButton(width=270, height=30, text="Запись api_id, api_hash",
                                                       on_click=lambda _: page.go("/recording_api_id_api_hash"))]),
                             ft.Row([ft.ElevatedButton(width=270, height=30, text="Запись времени",
                                                       on_click=lambda _: page.go("/time_between_subscriptions")),
                                     ft.ElevatedButton(width=270, height=30, text="Запись сообщений",
                                                       on_click=lambda _: page.go("/message_recording"))]),
                             ft.Row([ft.ElevatedButton(width=270, height=30, text="Запись ссылки для инвайтинга",
                                                       on_click=lambda _: page.go("/link_entry")),
                                     ft.ElevatedButton(width=270, height=30, text="Лимиты на аккаунт",
                                                       on_click=lambda _: page.go("/account_limits"))]),
                             ft.Row([ft.ElevatedButton(width=270, height=30, text="Лимиты на сообщения",
                                                       on_click=lambda _: page.go("/message_limits")),
                                     ft.ElevatedButton(width=270, height=30, text="Смена типа устройства",
                                                       on_click=lambda _: page.go("/changing_device_type"))]),
                             ft.ElevatedButton(width=line_width, height=30, text="Формирование списка username",
                                               on_click=lambda _: page.go("/creating_username_list")),
                             ft.ElevatedButton(width=line_width, height=30, text="Время между подпиской",
                                               on_click=lambda _: page.go("/time_between_subscriptionss")),
                             ft.ElevatedButton(width=line_width, height=30, text="Запись времени между сообщениями",
                                               on_click=lambda _: page.go("/recording_the_time_between_messages")),
                             ft.ElevatedButton(width=line_width, height=30,
                                               text="Время между инвайтингом, рассылка сообщений",
                                               on_click=lambda _: page.go("/time_between_invites_sending_messages")),
                             ft.ElevatedButton(width=line_width, height=30, text="Запись ссылки для реакций",
                                               on_click=lambda _: page.go("/recording_reaction_link")),
                             ft.ElevatedButton(width=line_width, height=30, text="Формирование списка чатов / каналов",
                                               on_click=lambda _: page.go("/forming_list_of_chats_channels")),
                         ])]))

        elif page.route == "/recording_api_id_api_hash":  # Запись api_id, api_hash
            SettingPage().writing_api_id_api_hash(page)
        elif page.route == "/changing_device_type":  # Смена типа устройства
            SettingPage().record_device_type(page)
        elif page.route == "/message_limits":  # Лимиты на сообщения
            SettingPage().record_setting(page, "message_limits", "Введите лимит на сообщения")
        elif page.route == "/account_limits":  # Лимиты на аккаунт
            SettingPage().record_setting(page, "account_limits", "Введите лимит на аккаунт")
        elif page.route == "/creating_username_list":  # Формирование списка username
            SettingPage().output_the_input_field(page, "Введите список username", "members",
                                                 "username, id, access_hash, first_name, last_name, user_phone, online_at, photos_id, user_premium",
                                                 "/settings", "members (username)")
        elif page.route == "/forming_list_of_chats_channels":  # Формирование списка чатов / каналов
            await DatabaseHandler().open_and_read_data("writing_group_links")  # Удаление списка с контактами
            SettingPage().output_the_input_field(page, "Введите список ссылок на группы", "writing_group_links",
                                                 "writing_group_links", "/settings", "writing_group_links")
        elif page.route == "/link_entry":  # Запись ссылки для инвайтинга
            await DatabaseHandler().cleaning_db("links_inviting")  # Удаление списка с группами
            SettingPage().output_the_input_field(page, "Введите ссылку на группу для инвайтинга", "links_inviting",
                                                 "links_inviting", "/settings", "links_inviting")
        elif page.route == "/proxy_entry":  # Запись времени между сообщениями
            SettingPage().creating_the_main_window_for_proxy_data_entry(page)
        elif page.route == "/message_recording":  # Запись сообщений
            SettingPage().recording_text_for_sending_messages(page)
        elif page.route == "/recording_reaction_link":  # Запись ссылки для реакций
            SettingPage().recording_link_channel(page)
        elif page.route == "/choice_of_reactions":  # Выбор реакций
            reaction_gui(page)
        elif page.route == "/recording_the_time_between_messages":  # Запись времени между сообщениями
            SettingPage().create_main_window(page, variable="time_sending_messages")
        elif page.route == "/time_between_invites_sending_messages":  # Время между инвайтингом, рассылка сообщений
            SettingPage().create_main_window(page, variable="time_inviting")
        elif page.route == "/changing_accounts":  # Смена аккаунтов
            SettingPage().create_main_window(page, variable="time_changing_accounts")
        elif page.route == "/time_between_subscriptions":  # Запись времени
            SettingPage().recording_the_time_to_launch_an_invite_every_day(page)
        elif page.route == "/time_between_subscriptionss":  # Время между подпиской
            SettingPage().create_main_window(page, variable="time_subscription")
        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)


ft.app(target=mainss)
