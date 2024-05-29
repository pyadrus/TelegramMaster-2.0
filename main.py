import flet as ft

from system.account_actions.creating.account_registration import AccountRIO
from system.account_actions.creating.creating import creating_groups_and_chats
from system.account_actions.parsing.parsing_group_members import parsing_gui
from system.menu.app_banner import program_version, date_of_program_change
from system.setting.setting import recording_the_time_to_launch_an_invite_every_day, \
    recording_text_for_sending_messages, create_main_window, \
    creating_the_main_window_for_proxy_data_entry, record_device_type, \
    writing_api_id_api_hash, record_setting, recording_link_channel, record_the_number_of_accounts, reaction_gui, \
    output_the_input_field, writing_members
from system.sqlite_working_tools.sqlite_working_tools import DatabaseHandler
# from system.telegram_actions.account_verification import deleting_files_by_dictionary
# from loguru import logger

# logger.add("user_settings/log/log.log", rotation="1 MB", compression="zip")  # Логирование программы

line_width = 580  # Ширина окна и ширина строки
# db_handler = DatabaseHandler()
# deleting_files_by_dictionary(db_handler)


def mainss(page: ft.Page):
    page.title = f"TelegramMaster: {program_version} (Дата изменения {date_of_program_change})"
    page.window_width = line_width  # window's ширина is 200 px
    page.window_height = 700  # window's высота is 200 px
    page.window_resizable = False  # window is not resizable

    # width - ширина,  # height - высота
    def route_change(route):
        page.views.clear()
        page.views.append(
            ft.View("/", [ft.AppBar(title=ft.Text("Главное меню"),
                                    bgcolor=ft.colors.SURFACE_VARIANT),
                          ft.Text(spans=[ft.TextSpan(
                              "TelegramMaster",
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

                          ft.ElevatedButton(width=line_width, height=30, text="Парсинг",
                                            on_click=lambda _: page.go("/parsing")),

                          ft.ElevatedButton(width=line_width, height=30, text="Создание групп (чатов)",
                                            on_click=lambda _: page.go("/creating_groups")),

                          ft.ElevatedButton(width=line_width, height=30, text="Создание групп (чатов)",
                                            on_click=lambda _: page.go("/creating_groups")),

                          ft.ElevatedButton(width=line_width, height=30, text="Редактирование BIO",
                                            on_click=lambda _: page.go("/bio_editing")),

                          ft.ElevatedButton(width=line_width, height=30, text="Настройки",
                                            on_click=lambda _: page.go("/settings")),
                          ], ))

        if page.route == "/parsing":  # Парсинг
            parsing_gui(page)
        elif page.route == "/creating_groups":  # Создание групп (чатов)
            db_handler = DatabaseHandler()
            records: list = db_handler.open_and_read_data("config")
            creating_groups_and_chats(page, records, db_handler)

        elif page.route == "/bio_editing":  # Настройки
            page.views.append(
                ft.View("/bio_editing",
                        [ft.AppBar(title=ft.Text("Главное меню"),
                                   bgcolor=ft.colors.SURFACE_VARIANT),
                         ft.Column([  # Добавляет все чекбоксы и кнопку на страницу (page) в виде колонок.
                             ft.ElevatedButton(width=line_width, height=30,
                                               text="Изменение username",
                                               on_click=lambda _: page.go("/changing_username")),
                             ft.ElevatedButton(width=line_width, height=30,
                                               text="Изменение фото",
                                               on_click=lambda _: page.go("/edit_photo")),
                             ft.ElevatedButton(width=line_width, height=30,
                                               text="Изменение описания",
                                               on_click=lambda _: page.go("/edit_description")),
                             ft.ElevatedButton(width=line_width, height=30,
                                               text="Изменение имени",
                                               on_click=lambda _: page.go("/name_change")),
                             ft.ElevatedButton(width=line_width, height=30,
                                               text="Изменение фамилии",
                                               on_click=lambda _: page.go("/change_surname")),
                         ])]))

        elif page.route == "/edit_description":  # ✔️ Изменение описания
            aaa = AccountRIO(DatabaseHandler())  # Передаем db_handler как аргумент
            aaa.change_bio_profile_gui(page, DatabaseHandler())
        elif page.route == "/name_change":  # ✔️ Изменение имени
            aaa = AccountRIO(DatabaseHandler())  # Передаем db_handler как аргумент
            aaa.change_name_profile_gui(page, DatabaseHandler())
        elif page.route == "/change_surname":  # ✔️ Изменение фамилии
            aaa = AccountRIO(DatabaseHandler())  # Передаем db_handler как аргумент
            aaa.change_last_name_profile_gui(page, DatabaseHandler())
        elif page.route == "/edit_photo":  # ✔️ Изменение фото
            aaa = AccountRIO(DatabaseHandler())  # Передаем db_handler как аргумент
            aaa.change_photo_profile(DatabaseHandler())
        elif page.route == "/changing_username":  # ✔️ Изменение username
            aaa = AccountRIO(DatabaseHandler())  # Передаем db_handler как аргумент
            aaa.change_username_profile_gui(page, DatabaseHandler())

        elif page.route == "/settings":  # Настройки
            page.views.append(
                ft.View("/settings",
                        [ft.AppBar(title=ft.Text("Главное меню"),
                                   bgcolor=ft.colors.SURFACE_VARIANT),
                         ft.Column([  # Добавляет все чекбоксы и кнопку на страницу (page) в виде колонок.
                             ft.ElevatedButton(width=line_width, height=30,
                                               text="✔️ Запись количества аккаунтов для реакций",
                                               on_click=lambda _: page.go("/recording_number_accounts_reactions")),

                             ft.Row([ft.ElevatedButton(width=270, height=30, text="✔️ Выбор реакций",
                                                       on_click=lambda _: page.go("/choice_of_reactions")),
                                     ft.ElevatedButton(width=270, height=30, text="✔️ Запись proxy",
                                                       on_click=lambda _: page.go("/proxy_entry"))]),

                             ft.ElevatedButton(width=line_width, height=30,
                                               text="✔️ Запись времени между сообщениями",
                                               on_click=lambda _: page.go("/recording_the_time_between_messages")),
                             ft.ElevatedButton(width=line_width, height=30,
                                               text="✔️ Время между инвайтингом, рассылка сообщений",
                                               on_click=lambda _: page.go("/time_between_invites_sending_messages")),

                             ft.Row([ft.ElevatedButton(width=270, height=30, text="✔️ Смена аккаунтов",
                                                       on_click=lambda _: page.go("/changing_accounts")),
                                     ft.ElevatedButton(width=270, height=30, text="✔️ Запись api_id, api_hash",
                                                       on_click=lambda _: page.go("/recording_api_id_api_hash"))]),

                             ft.Row([ft.ElevatedButton(width=270, height=30, text="✔️ Запись времени",
                                                       on_click=lambda _: page.go("/time_between_subscriptions")),
                                     ft.ElevatedButton(width=270, height=30, text="✔️  Запись сообщений",
                                                       on_click=lambda _: page.go("/message_recording"))]),

                             ft.Row([ft.ElevatedButton(width=270, height=30, text="✔️ Запись имени аккаунта",
                                                       on_click=lambda _: page.go("/record_your_account_name")),
                                     ft.ElevatedButton(width=270, height=30, text="✔️ Время между подпиской",
                                                       on_click=lambda _: page.go("/time_between_subscriptionss"))]),

                             ft.ElevatedButton(width=line_width, height=30, text="✔️ Запись ссылки для реакций",
                                               on_click=lambda _: page.go("/recording_reaction_link")),
                             ft.ElevatedButton(width=line_width, height=30,
                                               text="✔️ Формирование списка чатов / каналов",
                                               on_click=lambda _: page.go("/forming_list_of_chats_channels")),
                             ft.ElevatedButton(width=line_width, height=30,
                                               text="✔️ Формирование списка username",
                                               on_click=lambda _: page.go("/creating_username_list")),

                             ft.Row([ft.ElevatedButton(width=270, height=30, text="✔️ Запись ссылки",
                                                       on_click=lambda _: page.go("/link_entry")),
                                     ft.ElevatedButton(width=270, height=30, text="✔️ Лимиты на аккаунт",
                                                       on_click=lambda _: page.go("/account_limits"))]),

                             ft.Row([ft.ElevatedButton(width=270, height=30, text="✔️ Лимиты на сообщения",
                                                       on_click=lambda _: page.go("/message_limits")),
                                     ft.ElevatedButton(width=270, height=30, text="✔️ Смена типа устройства",
                                                       on_click=lambda _: page.go("/changing_device_type"))]),

                         ])]))
        elif page.route == "/creating_username_list":  # ✔️ Формирование списка username
            writing_members(page, DatabaseHandler())
        elif page.route == "/recording_api_id_api_hash":  # ✔️ Запись api_id, api_hash
            writing_api_id_api_hash(page)
        elif page.route == "/changing_device_type":  # ✔️ Смена типа устройства
            record_device_type(page)
        elif page.route == "/message_limits":  # ✔️ Лимиты на сообщения
            record_setting(page, "message_limits", "Введите лимит на сообщения")
        elif page.route == "/account_limits":  # ✔️ Лимиты на аккаунт
            record_setting(page, "account_limits", "Введите лимит на аккаунт")
        elif page.route == "/link_entry":  # ✔️ Запись ссылки
            record_setting(page, "link_to_the_group", "Введите ссылку на группу")
        elif page.route == "/forming_list_of_chats_channels":  # ✔️ Формирование списка чатов / каналов
            output_the_input_field(page, DatabaseHandler())
        elif page.route == "/recording_reaction_link":  # ✔️ Запись ссылки для реакций
            recording_link_channel(page)
        elif page.route == "/recording_number_accounts_reactions":  # ✔️ Запись количества аккаунтов для реакций
            record_the_number_of_accounts(page)
        elif page.route == "/choice_of_reactions":  # ✔️ Выбор реакций
            reaction_gui(page)
        elif page.route == "/proxy_entry":  # ✔️ Запись времени между сообщениями
            creating_the_main_window_for_proxy_data_entry(page, DatabaseHandler())
        elif page.route == "/recording_the_time_between_messages":  # ✔️ Запись времени между сообщениями
            create_main_window(page, variable="time_sending_messages")
        elif page.route == "/time_between_invites_sending_messages":  # ✔️ Время между инвайтингом, рассылка сообщений
            create_main_window(page, variable="time_inviting")
        elif page.route == "/changing_accounts":  # ✔️ Смена аккаунтов
            create_main_window(page, variable="time_changing_accounts")
        elif page.route == "/time_between_subscriptions":  # ✔️ Запись времени
            recording_the_time_to_launch_an_invite_every_day(page)
        elif page.route == "/message_recording":  # ✔️ Запись сообщений
            recording_text_for_sending_messages(page)
        elif page.route == "/record_your_account_name":  # ✔️ Запись имени аккаунта
            record_setting(page, "account_name_newsletter", "Введите название аккаунта для отправки сообщений по чатам")
        elif page.route == "/time_between_subscriptionss":  # ✔️ Время между подпиской
            create_main_window(page, variable="time_subscription")
        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)


ft.app(target=mainss)
