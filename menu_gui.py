import flet as ft

from system.menu.app_banner import program_version, date_of_program_change
from system.setting.setting import recording_the_time_to_launch_an_invite_every_day, \
    recording_text_for_sending_messages, record_account_name_newsletter


def mainss(page: ft.Page):
    page.title = f"TelegramMaster: {program_version} (Дата изменения {date_of_program_change})"
    page.window_width = 520  # window's width is 200 px
    page.window_height = 650  # window's height is 200 px
    page.window_resizable = False  # window is not resizable

    # width - ширина,  # height - высота
    def route_change(route):
        page.views.clear()
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
                          ft.ElevatedButton(width=500, height=30, text="Инвайтинг",
                                            on_click=lambda _: page.go("/inviting")),
                          ft.ElevatedButton(width=500, height=30, text="Парсинг",
                                            on_click=lambda _: page.go("/parsing")),
                          ft.ElevatedButton(width=500, height=30, text="Работа с контактами",
                                            on_click=lambda _: page.go("/contacts")),
                          ft.ElevatedButton(width=500, height=30, text="Подписка, отписка",
                                            on_click=lambda _: page.go("/subscribe_unsubscribe")),
                          ft.ElevatedButton(width=500, height=30, text="Подключение аккаунтов",
                                            on_click=lambda _: page.go("/store")),
                          ft.ElevatedButton(width=500, height=30, text="Рассылка сообщений",
                                            on_click=lambda _: page.go("/sending_messages")),
                          ft.ElevatedButton(width=500, height=30, text="Работа с реакциями",
                                            on_click=lambda _: page.go("/reaction")),
                          ft.ElevatedButton(width=500, height=30, text="Настройки",
                                            on_click=lambda _: page.go("/settings")),
                          ft.ElevatedButton(width=500, height=30, text="Проверка аккаунтов",
                                            on_click=lambda _: page.go("/store")),
                          ft.ElevatedButton(width=500, height=30, text="Создание групп (чатов)",
                                            on_click=lambda _: page.go("/store")),
                          ft.ElevatedButton(width=500, height=30, text="Редактирование BIO",
                                            on_click=lambda _: page.go("/bio")),
                          ], ))
        if page.route == "/inviting":
            # db_handler = DatabaseHandler()  # Создаем объект для работы с БД
            page.views.append(
                ft.View("/inviting", [ft.AppBar(title=ft.Text("Главное меню"),
                                                bgcolor=ft.colors.SURFACE_VARIANT),
                                      ft.ElevatedButton(width=500, height=30, text=f"Инвайтинг без лимитов",
                                                        on_click=lambda _: page.go("/inviting_without_limits")),
                                      # ft.ElevatedButton(width=500, height=30, text=f"Инвайтинг без лимитов",
                                      #                   on_click=lambda _: invitation_from_all_accounts_program_body(
                                      #                       name_database_table="members", db_handler=db_handler)),
                                      # ft.ElevatedButton(width=500, height=30, text=f"Инвайтинг с лимитами",
                                      #                   on_click=lambda _: page.go("/")),
                                      # ft.ElevatedButton(width=500, height=30, text=f"Инвайтинг 1 раз в час",
                                      #                   on_click=lambda _: page.go("/")),
                                      # ft.ElevatedButton(width=500, height=30, text=f"Инвайтинг в определенное время",
                                      #                   on_click=lambda _: page.go("/")),
                                      # ft.ElevatedButton(width=500, height=30, text=f"Инвайтинг каждый день",
                                      #                   on_click=lambda _: page.go("/")),
                                      ft.ElevatedButton(width=500, height=30, text="В начальное меню",
                                                        on_click=lambda _: page.go("/")), ], ))
        elif page.route == "/inviting_without_limits":
            print("Инвайтинг без лимитов")


        elif page.route == "/parsing":
            page.views.append(
                ft.View("/parsing", [ft.AppBar(title=ft.Text("Главное меню"),
                                               bgcolor=ft.colors.SURFACE_VARIANT),
                                     ft.ElevatedButton(width=500, height=30, text=f"Parsing одной групп",
                                                       on_click=lambda _: page.go("/")),
                                     ft.ElevatedButton(width=500, height=30, text=f"Выбор группы из подписанных",
                                                       on_click=lambda _: page.go("/")),
                                     ft.ElevatedButton(width=500, height=30, text=f"Parsing активных участников",
                                                       on_click=lambda _: page.go("/")),
                                     ft.ElevatedButton(width=500, height=30,
                                                       text=f"Parsing списка: групп, каналов аккаунтов",
                                                       on_click=lambda _: page.go("/")),
                                     ft.ElevatedButton(width=500, height=30, text=f"Очистка parsing списка",
                                                       on_click=lambda _: page.go("/")),
                                     ft.ElevatedButton(width=500, height=30, text="Формирование списка",
                                                       on_click=lambda _: page.go("/")), ], ))
        elif page.route == "/contacts":
            page.views.append(
                ft.View("/contacts", [ft.AppBar(title=ft.Text("Главное меню"),
                                                bgcolor=ft.colors.SURFACE_VARIANT),
                                      ft.ElevatedButton(width=500, height=30, text=f"Формирование списка контактов",
                                                        on_click=lambda _: page.go("/")),
                                      ft.ElevatedButton(width=500, height=30, text=f"Показать список контактов",
                                                        on_click=lambda _: page.go("/")),
                                      ft.ElevatedButton(width=500, height=30, text=f"Удаление контактов",
                                                        on_click=lambda _: page.go("/")),
                                      ft.ElevatedButton(width=500, height=30, text=f"Добавление контактов",
                                                        on_click=lambda _: page.go("/")), ], ))
        elif page.route == "/subscribe_unsubscribe":
            page.views.append(
                ft.View("/subscribe_unsubscribe", [ft.AppBar(title=ft.Text("Главное меню"),
                                                             bgcolor=ft.colors.SURFACE_VARIANT),
                                                   ft.ElevatedButton(width=500, height=30,
                                                                     text=f"Формирование списка и подписка",
                                                                     on_click=lambda _: page.go("/")),
                                                   ft.ElevatedButton(width=500, height=30, text=f"Отписываемся",
                                                                     on_click=lambda _: page.go("/")), ], ))
        elif page.route == "/sending_messages":
            page.views.append(
                ft.View("/sending_messages", [ft.AppBar(title=ft.Text("Главное меню"),
                                                        bgcolor=ft.colors.SURFACE_VARIANT),
                                              ft.ElevatedButton(width=500, height=30,
                                                                text=f"Отправка сообщений в личку",
                                                                on_click=lambda _: page.go("/")),
                                              ft.ElevatedButton(width=500, height=30, text=f"Отправка файлов в личку",
                                                                on_click=lambda _: page.go("/")),
                                              ft.ElevatedButton(width=500, height=30,
                                                                text=f"Рассылка сообщений по чатам",
                                                                on_click=lambda _: page.go("/")),
                                              ft.ElevatedButton(width=500, height=30,
                                                                text=f"Рассылка сообщений по чатам, по времени",
                                                                on_click=lambda _: page.go("/")),
                                              ft.ElevatedButton(width=500, height=30, text=f"Рассылка файлов по чатам",
                                                                on_click=lambda _: page.go("/")),
                                              ft.ElevatedButton(width=500, height=30,
                                                                text="Рассылка сообщений + файлов по чатам",
                                                                on_click=lambda _: page.go("/")),
                                              ft.ElevatedButton(width=500, height=30, text=f"Формирование списка чатов",
                                                                on_click=lambda _: page.go("/")),
                                              ft.ElevatedButton(width=500, height=30,
                                                                text="Отправка сообщений в личку (с лимитами)",
                                                                on_click=lambda _: page.go("/")),
                                              ft.ElevatedButton(width=500, height=30,
                                                                text="Отправка файлов в личку (с лимитами)",
                                                                on_click=lambda _: page.go("/")), ], ))
        elif page.route == "/reaction":  # Работа с реакциями
            page.views.append(
                ft.View("/reaction", [ft.AppBar(title=ft.Text("Главное меню"),
                                                bgcolor=ft.colors.SURFACE_VARIANT),
                                      ft.ElevatedButton(width=500, height=30, text=f"Ставим реакцию на 1 пост",
                                                        on_click=lambda _: page.go("/")),
                                      ft.ElevatedButton(width=500, height=30, text="Накручиваем просмотры постов",
                                                        on_click=lambda _: page.go("/")), ], ))
        elif page.route == "/settings":  # Настройки
            page.views.append(
                ft.View("/settings", [ft.AppBar(title=ft.Text("Главное меню"),
                                                bgcolor=ft.colors.SURFACE_VARIANT),
                                      ft.ElevatedButton(width=500, height=30, text=f"Запись ссылки",
                                                        on_click=lambda _: page.go("/link_entry")),
                                      ft.ElevatedButton(width=500, height=30, text=f"Запись api_id, api_hash",
                                                        on_click=lambda _: page.go("/")),
                                      ft.ElevatedButton(width=500, height=30,
                                                        text=f"Время между Inviting, рассылка сообщений",
                                                        on_click=lambda _: page.go("/")),
                                      ft.ElevatedButton(width=500, height=30, text=f"Смена аккаунтов",
                                                        on_click=lambda _: page.go("/")),

                                      ft.ElevatedButton(width=500, height=30, text="✔️ Запись времени",
                                                        on_click=lambda _: page.go("/time_between_subscriptions")),
                                      ft.ElevatedButton(width=500, height=30, text="✔️  Запись сообщений",
                                                        on_click=lambda _: page.go("/message_recording")),
                                      ft.ElevatedButton(width=500, height=30, text="✔️ Запись имени аккаунта",
                                                        on_click=lambda _: page.go("/record_your_account_name")),

                                      ft.ElevatedButton(width=500, height=30, text="Смена типа устройства",
                                                        on_click=lambda _: page.go("/")),
                                      ft.ElevatedButton(width=500, height=30, text="Запись времени",
                                                        on_click=lambda _: page.go("/")),
                                      ft.ElevatedButton(width=500, height=30, text="Лимиты на сообщения",
                                                        on_click=lambda _: page.go("/")), ], ))
        elif page.route == "/link_entry":
            print("Запись ссылки")
        elif page.route == "/time_between_subscriptions":
            # ✔️ Запись времени
            recording_the_time_to_launch_an_invite_every_day(page)
        elif page.route == "/message_recording":
            # ✔️ Запись сообщений
            recording_text_for_sending_messages(page)
        elif page.route == "/record_your_account_name":
            # ✔️ Запись имени аккаунта
            record_account_name_newsletter(page)
        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)


# ft.app(target=mainss, view=ft.AppView.WEB_BROWSER)
ft.app(target=mainss)
