# -*- coding: utf-8 -*-
import flet as ft

from src.core.configs import BUTTON_HEIGHT, small_button_width, line_width_button, program_name
from src.core.localization import (inviting_ru, we_are_winding_up_post_views_ru, editing_bio,
                                   working_with_contacts_menu_ru, subscribe_unsubscribe,
                                   checking_accounts, connecting_accounts, working_with_reactions, parsing,
                                   settings, main_menu, creating_groups_chats, text_1, text_link_1, text_2, text_link_2,
                                   documentation, sending_personal_messages_with_limits_ru,
                                   sending_messages_via_chats_ru)


async def main_menu_program(page: ft.Page):
    """
    Главное меню программы

    :param page: Страница интерфейса Flet для отображения элементов управления.
    """
    page.views.append(
        ft.View("/", [ft.AppBar(title=ft.Text(main_menu),
                                bgcolor=ft.colors.SURFACE_VARIANT),
                      ft.Text(spans=[ft.TextSpan(
                          f"{program_name}",
                          ft.TextStyle(
                              size=40,
                              weight=ft.FontWeight.BOLD,
                              foreground=ft.Paint(
                                  gradient=ft.PaintLinearGradient((0, 20), (150, 20), [ft.colors.PINK,
                                                                                       ft.colors.PURPLE])), ), ), ], ),
                      ft.Text(disabled=False,
                              spans=[ft.TextSpan(text_1),
                                     ft.TextSpan(text_link_1,
                                                 ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE),
                                                 url=text_link_1, ), ], ),
                      ft.Text(disabled=False,
                              spans=[ft.TextSpan(text_2),
                                     ft.TextSpan(text_link_2,
                                                 ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE),
                                                 url=text_link_2, ), ], ),
                      ft.Column([  # Добавляет все чекбоксы и кнопку на страницу (page) в виде колонок.
                          ft.Row(
                              # 🚀 Инвайтинг
                              [ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT, text=inviting_ru,
                                                 on_click=lambda _: page.go("/inviting")),
                               # 📊 Парсинг
                               ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT, text=parsing,
                                                 on_click=lambda _: page.go("/parsing")), ]),
                          # 📇 Работа с контактами
                          ft.Row([ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT,
                                                    text=working_with_contacts_menu_ru,
                                                    on_click=lambda _: page.go("/working_with_contacts")),
                                  # 🔄 Подписка, отписка
                                  ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT,
                                                    text=subscribe_unsubscribe,
                                                    on_click=lambda _: page.go("/subscribe_unsubscribe")), ]),
                          # 🔐 Подключение аккаунтов
                          ft.Row([ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT,
                                                    text=connecting_accounts,
                                                    on_click=lambda _: page.go("/account_connection_menu")),
                                  # 📨 Отправка сообщений в личку
                                  ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT,
                                                    text=sending_personal_messages_with_limits_ru,
                                                    on_click=lambda _: page.go(
                                                        "/sending_files_to_personal_account_with_limits")), ]),
                          # ❤️ Работа с реакциями
                          ft.Row([ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT,
                                                    text=working_with_reactions,
                                                    on_click=lambda _: page.go("/working_with_reactions")),
                                  # 🔍 Проверка аккаунтов
                                  ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT,
                                                    text=checking_accounts,
                                                    on_click=lambda _: page.go("/account_verification_menu")), ]),
                          # 👥 Создание групп (чатов)
                          ft.Row([ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT,
                                                    text=creating_groups_chats,
                                                    on_click=lambda _: page.go("/creating_groups_and_chats_menu")),
                                  # ✏️ Редактирование_BIO
                                  ft.ElevatedButton(width=small_button_width, height=BUTTON_HEIGHT,
                                                    text=editing_bio,
                                                    on_click=lambda _: page.go("/bio_editing")), ]),

                          # 👁️‍🗨️ Накручиваем просмотры постов
                          ft.ElevatedButton(width=line_width_button, height=BUTTON_HEIGHT,
                                            text=we_are_winding_up_post_views_ru,
                                            on_click=lambda _: page.go("/viewing_posts_menu")),
                          # ⚙️ Настройки
                          ft.ElevatedButton(width=line_width_button, height=BUTTON_HEIGHT, text=settings,
                                            on_click=lambda _: page.go("/settings")),
                          # 📖 Документация
                          ft.ElevatedButton(width=line_width_button, height=BUTTON_HEIGHT, text=documentation,
                                            on_click=lambda _: page.go("/documentation")),
                          # 💬 Рассылка сообщений по чатам
                          ft.ElevatedButton(width=line_width_button, height=BUTTON_HEIGHT,
                                            text=sending_messages_via_chats_ru,
                                            on_click=lambda _: page.go("/sending_messages_files_via_chats")),

                      ]), ]))
