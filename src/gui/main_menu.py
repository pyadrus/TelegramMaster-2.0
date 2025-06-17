# -*- coding: utf-8 -*-
import flet as ft

from src.core.configs import BUTTON_HEIGHT, small_button_width, line_width_button, program_name, BUTTON_WIDTH
from src.locales.translations_loader import translations


async def main_menu_program(page: ft.Page):
    """
    Главное меню программы

    :param page: Страница интерфейса Flet для отображения элементов управления.
    """
    page.views.append(
        ft.View("/", [ft.AppBar(title=ft.Text(translations["ru"]["menu"]["main"]),
                                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST),
                      ft.Text(spans=[ft.TextSpan(
                          f"{program_name}",
                          ft.TextStyle(
                              size=40,
                              weight=ft.FontWeight.BOLD,
                              foreground=ft.Paint(
                                  gradient=ft.PaintLinearGradient((0, 20), (150, 20), [ft.Colors.PINK,
                                                                                       ft.Colors.PURPLE])), ), ), ], ),
                      ft.Text(disabled=False,
                              spans=[ft.TextSpan(translations["ru"]["main_menu_texts"]["text_1"]),
                                     ft.TextSpan(translations["ru"]["main_menu_texts"]["text_2"],
                                                 ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE),
                                                 url=translations["ru"]["main_menu_texts"]["text_2"], ), ], ),
                      ft.Text(disabled=False,
                              spans=[ft.TextSpan(translations["ru"]["main_menu_texts"]["text_2"]),
                                     ft.TextSpan(translations["ru"]["main_menu_texts"]["text_2"],
                                                 ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE),
                                                 url=translations["ru"]["main_menu_texts"]["text_2"], ), ], ),
                      ft.Column([  # Добавляет все чекбоксы и кнопку на страницу (page) в виде колонок.
                          ft.Row(
                              # 🚀 Инвайтинг
                              [ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT,
                                                 text=translations["ru"]["inviting_menu"]["inviting"],
                                                 on_click=lambda _: page.go("/inviting")),
                               # 📊 Парсинг
                               ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT,
                                                 text=translations["ru"]["menu"]["parsing"],
                                                 on_click=lambda _: page.go("/parsing")), ]),
                          # 📇 Работа с контактами
                          ft.Row([ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT,
                                                    text=translations["ru"]["menu"]["contacts"],
                                                    on_click=lambda _: page.go("/working_with_contacts")),
                                  # 🔄 Подписка, отписка
                                  ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT,
                                                    text=translations["ru"]["menu"]["subscribe_unsubscribe"],
                                                    on_click=lambda _: page.go("/subscribe_unsubscribe")), ]),
                          # 🔐 Подключение аккаунтов
                          ft.Row([ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT,
                                                    text=translations["ru"]["menu"]["account_connect"],
                                                    on_click=lambda _: page.go("/account_connection_menu")),
                                  # 📨 Отправка сообщений в личку
                                  ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT,
                                                    text=translations["ru"]["message_sending_menu"][
                                                        "sending_personal_messages_with_limits"],
                                                    on_click=lambda _: page.go(
                                                        "/sending_files_to_personal_account_with_limits")), ]),
                          # ❤️ Работа с реакциями
                          ft.Row([ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT,
                                                    text=translations["ru"]["menu"]["reactions"],
                                                    on_click=lambda _: page.go("/working_with_reactions")),
                                  # 🔍 Проверка аккаунтов
                                  ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT,
                                                    text=translations["ru"]["menu"]["account_check"],
                                                    on_click=lambda _: page.go("/account_verification_menu")), ]),
                          # 👥 Создание групп (чатов)
                          ft.Row([ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT,
                                                    text=translations["ru"]["menu"]["create_groups"],
                                                    on_click=lambda _: page.go("/creating_groups")),

                                  # ✏️ Редактирование_BIO
                                  ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT,
                                                    text=translations["ru"]["menu"]["edit_bio"],
                                                    on_click=lambda _: page.go("/bio_editing")), ]),

                          # 👁️‍🗨️ Накручиваем просмотры постов
                          ft.ElevatedButton(width=line_width_button, height=BUTTON_HEIGHT,
                                            text=translations["ru"]["reactions_menu"]["we_are_winding_up_post_views"],
                                            on_click=lambda _: page.go("/viewing_posts_menu")),
                          # ⚙️ Настройки
                          ft.ElevatedButton(width=line_width_button, height=BUTTON_HEIGHT,
                                            text=translations["ru"]["menu"]["settings"],
                                            on_click=lambda _: page.go("/settings")),
                          # 📖 Документация
                          ft.ElevatedButton(width=line_width_button, height=BUTTON_HEIGHT,
                                            text=translations["ru"]["menu"]["documentation"],
                                            on_click=lambda _: page.go("/documentation")),
                          # 💬 Рассылка сообщений по чатам
                          ft.ElevatedButton(width=line_width_button, height=BUTTON_HEIGHT,
                                            text=translations["ru"]["message_sending_menu"][
                                                "sending_messages_via_chats"],
                                            on_click=lambda _: page.go("/sending_messages_files_via_chats")),
                          # 📋 Импорт списка от ранее спарсенных данных
                          ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
                                            text=translations["ru"]["parsing_menu"]["importing_a_list_of_parsed_data"],
                                            on_click=lambda _: page.go("/importing_a_list_of_parsed_data")),
                      ]), ]))
