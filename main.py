# -*- coding: utf-8 -*-
import asyncio
import datetime
import webbrowser

import flet as ft
from loguru import logger

from docs.app import run_quart, program_version, date_of_program_change
from system.account_actions.TGAccountBIO import AccountBIO
from system.account_actions.TGConnect import TGConnect
from system.account_actions.TGContact import TGContact
from system.account_actions.TGCreating import CreatingGroupsAndChats
from system.account_actions.TGInviting import InvitingToAGroup
from system.account_actions.TGInvitingScheduler import (launching_an_invite_once_an_hour,
                                                        launching_invite_every_day_certain_time, schedule_invite)
from system.account_actions.TGParsing import ParsingGroupMembers
from system.account_actions.TGReactions import WorkingWithReactions
from system.account_actions.TGSendingMessages import SendTelegramMessages
from system.account_actions.TGSubUnsub import SubscribeUnsubscribeTelegram
from system.auxiliary_functions.auxiliary_functions import find_files, find_folders
from system.auxiliary_functions.global_variables import ConfigReader
from system.menu_gui.menu_gui import (line_width, inviting_menu, working_with_contacts_menu, message_distribution_menu,
                                      bio_editing_menu, settings_menu, menu_parsing, reactions_menu,
                                      subscribe_and_unsubscribe_menu)
from system.setting.setting import SettingPage, get_unique_filename, reaction_gui
from system.sqlite_working_tools.sqlite_working_tools import DatabaseHandler

logger.add("user_settings/log/log.log", rotation="2 MB", compression="zip")  # Логирование программы


async def log_and_execute_with_args(task_name, execute_method, *args, **kwargs):
    start = datetime.datetime.now()  # фиксируем и выводим время старта работы кода
    logger.info(f'Время старта: {start}')
    logger.info(f"▶️ {task_name} начался")

    # Выполняем переданный метод с аргументами
    await execute_method(*args, **kwargs)

    logger.info(f"🔚 {task_name} завершен")
    finish = datetime.datetime.now()  # фиксируем и выводим время окончания работы кода
    logger.info(f'Время окончания: {finish}')
    logger.info(f'Время работы: {finish - start}')  # вычитаем время старта из времени окончания


async def log_and_parse(task_name, parse_method, page=None):
    """Отображение времени начала и завершения работы"""
    start = datetime.datetime.now()  # фиксируем и выводим время старта работы кода
    logger.info(f'Время старта: {start}')
    logger.info(f"▶️ {task_name} начался")

    if page:
        await parse_method(page)
    else:
        await parse_method()

    logger.info(f"🔚 {task_name} завершен")
    finish = datetime.datetime.now()  # фиксируем и выводим время окончания работы кода
    logger.info(f'Время окончания: {finish}')
    logger.info(f'Время работы: {finish - start}')  # вычитаем время старта из времени окончания


async def main():
    # Запускаем сервер Quart в фоновом режиме
    quart_task = asyncio.create_task(run_quart())

    page = ft.Page()  # код Flet
    telegram_master_main(page)

    await quart_task  # Ждём завершения задачи сервера Quart


def setup_page(page, program_version, date_of_program_change, line_width):
    page.title = f"TelegramMaster: {program_version} (Дата изменения {date_of_program_change})"
    page.window.width = line_width
    page.window.height = 550
    page.window.resizable = False
    logger.info(f"Program version: {program_version}. Date of change: {date_of_program_change}")


def telegram_master_main(page: ft.Page):
    setup_page(page, program_version, date_of_program_change, line_width)

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
                                  spans=[ft.TextSpan('Аккаунт  Telegram: '),
                                         ft.TextSpan("https://t.me/PyAdminRU",
                                                     ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE),
                                                     url="https://t.me/PyAdminRU", ), ], ),
                          ft.Text(disabled=False,
                                  spans=[ft.TextSpan("Канал Telegram: "),
                                         ft.TextSpan("https://t.me/master_tg_d",
                                                     ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE),
                                                     url="https://t.me/master_tg_d", ), ], ),
                          ft.Column([  # Добавляет все чекбоксы и кнопку на страницу (page) в виде колонок.
                              ft.Row([ft.ElevatedButton(width=270, height=30, text="Инвайтинг",
                                                        on_click=lambda _: page.go("/inviting")),
                                      ft.ElevatedButton(width=270, height=30, text="Парсинг",
                                                        on_click=lambda _: page.go("/parsing")), ]),
                              ft.Row([ft.ElevatedButton(width=270, height=30, text="Работа с контактами",
                                                        on_click=lambda _: page.go("/working_with_contacts")),
                                      ft.ElevatedButton(width=270, height=30, text="Подписка, отписка",
                                                        on_click=lambda _: page.go("/subscribe_unsubscribe")), ]),
                              ft.Row([ft.ElevatedButton(width=270, height=30, text="Подключение аккаунтов",
                                                        on_click=lambda _: page.go("/connecting_accounts")),
                                      ft.ElevatedButton(width=270, height=30, text="Рассылка сообщений",
                                                        on_click=lambda _: page.go("/sending_messages")), ]),
                              ft.Row([ft.ElevatedButton(width=270, height=30, text="Работа с реакциями",
                                                        on_click=lambda _: page.go("/working_with_reactions")),
                                      ft.ElevatedButton(width=270, height=30, text="Проверка аккаунтов",
                                                        on_click=lambda _: page.go("/checking_accounts")), ]),
                              ft.Row([ft.ElevatedButton(width=270, height=30, text="Создание групп (чатов)",
                                                        on_click=lambda _: page.go("/creating_groups")),
                                      ft.ElevatedButton(width=270, height=30, text="Редактирование_BIO",
                                                        on_click=lambda _: page.go("/bio_editing")), ]),
                              ft.ElevatedButton(width=line_width, height=30, text="Настройки",
                                                on_click=lambda _: page.go("/settings")),
                              ft.ElevatedButton(width=line_width, height=30, text="Документация",
                                                on_click=lambda _: page.go("/documentation")),
                          ]), ]))
        if page.route == "/inviting":  # Меню "Инвайтинг"
            await inviting_menu(page)
        elif page.route == "/inviting_without_limits":  # Инвайтинг
            await log_and_execute_with_args(
                "Инвайтинг", InvitingToAGroup().inviting_without_limits, account_limits=ConfigReader().get_limits())
        elif page.route == "/inviting_1_time_per_hour":
            await log_and_parse("Инвайтинг 1 раз в час", launching_an_invite_once_an_hour)
        elif page.route == "/inviting_certain_time":
            await log_and_parse("Инвайтинг в определенное время", schedule_invite)
        elif page.route == "/inviting_every_day":
            await log_and_parse("Инвайтинг каждый день", launching_invite_every_day_certain_time)
        elif page.route == "/checking_accounts":  # Проверка аккаунтов

            start = datetime.datetime.now()  # фиксируем и выводим время старта работы кода
            logger.info('Время старта: ' + str(start))
            logger.info("▶️ Проверка аккаунтов началась")

            await TGConnect().verify_all_accounts(account_directory="user_settings/accounts",
                                                  extension="session")  # Вызываем метод для проверки аккаунтов
            folders = find_folders(directory_path="user_settings/accounts")
            for folder in folders:
                logger.info(f'Проверка аккаунтов из папки 📁 {folder} через спам бот')
                if folder == "invalid_account":
                    logger.info(f"⛔ Пропускаем папку 📁: {folder}")
                    continue  # Продолжаем цикл, пропуская эту итерацию
                else:
                    await TGConnect().verify_all_accounts(account_directory=f"user_settings/accounts/{folder}",
                                                          extension="session")
                    await TGConnect().check_for_spam(folder)
            logger.info("🔚 Проверка аккаунтов завершена")
            finish = datetime.datetime.now()  # фиксируем и выводим время окончания работы кода
            logger.info('Время окончания: ' + str(finish))
            logger.info('Время работы: ' + str(finish - start))  # вычитаем время старта из времени окончания

        elif page.route == "/subscribe_unsubscribe":  # Меню "Подписка и отписка"
            await subscribe_and_unsubscribe_menu(page)
        elif page.route == "/subscription_all":
            await log_and_parse("Подписка", SubscribeUnsubscribeTelegram().subscribe_telegram)
        elif page.route == "/unsubscribe_all":
            await log_and_parse("Отписываемся", SubscribeUnsubscribeTelegram().unsubscribe_all)
        elif page.route == "/working_with_reactions":  # Меню "Работа с реакциями"
            await reactions_menu(page)
        elif page.route == "/setting_reactions":
            await log_and_parse("Ставим реакции", WorkingWithReactions().send_reaction_request, page)
        elif page.route == "/we_are_winding_up_post_views":
            await log_and_parse("Накручиваем просмотры постов", WorkingWithReactions().viewing_posts)
        elif page.route == "/automatic_setting_of_reactions":
            await log_and_parse("Автоматическое выставление реакций", WorkingWithReactions().setting_reactions)
        elif page.route == "/parsing":  # Меню "Парсинг"
            await menu_parsing(page)
        elif page.route == "/parsing_single_groups":

            await log_and_parse("Парсинг одной группы / групп", ParsingGroupMembers().parse_groups)

        elif page.route == "/parsing_selected_group_user_subscribed":
            await log_and_parse("Парсинг выбранной группы", ParsingGroupMembers().choose_and_parse_group, page)
        elif page.route == "/parsing_active_group_members":
            await log_and_parse("Парсинг активных участников группы",
                                ParsingGroupMembers().entering_data_for_parsing_active, page)
        elif page.route == "/parsing_groups_channels_account_subscribed":
            await log_and_parse("Парсинг групп / каналов аккаунта", ParsingGroupMembers().parse_subscribed_groups)
        elif page.route == "/clearing_list_previously_saved_data":
            await log_and_parse("Очистка списка от ранее спарсенных данных", DatabaseHandler().cleaning_db, "members")
        elif page.route == "/working_with_contacts":  # Меню "Работа с контактами"
            await working_with_contacts_menu(page)
        elif page.route == "/creating_contact_list":  # Формирование списка контактов
            await DatabaseHandler().open_and_read_data("contact")  # Удаление списка с контактами
            SettingPage().output_the_input_field(page, "Введите список номеров телефонов", "contact",
                                                 "contact", "/working_with_contacts", "contact")
        elif page.route == "/show_list_contacts":
            await log_and_parse("Показать список контактов", TGContact().show_account_contact_list)
        elif page.route == "/deleting_contacts":
            await log_and_parse("Удаление контактов", TGContact().delete_contact)
        elif page.route == "/adding_contacts":
            await log_and_parse("Добавление контактов", TGContact().inviting_contact)
        elif page.route == "/connecting_accounts":
            await log_and_parse("Подключение новых аккаунтов, методом ввода нового номера телефона",
                                TGConnect().start_telegram_session, page)
        elif page.route == "/creating_groups":
            await log_and_parse("Создание групп (чатов)", CreatingGroupsAndChats().creating_groups_and_chats)
        elif page.route == "/sending_messages":  # Меню "Рассылка сообщений"
            await message_distribution_menu(page)
        elif page.route == "/sending_messages_via_chats":  # Рассылка сообщений по чатам
            entities = find_files(directory_path="user_settings/message", extension="json")
            logger.info(entities)
            await SendTelegramMessages().sending_messages_via_chats_times()
        elif page.route == "/sending_messages_via_chats_with_answering_machine":
            await log_and_parse("Рассылка сообщений по чатам с автоответчиком",
                                SendTelegramMessages().answering_machine)
        elif page.route == "/sending_files_via_chats":
            await log_and_parse("Рассылка файлов по чатам", SendTelegramMessages().sending_files_via_chats)
        elif page.route == "/sending_messages_files_via_chats":
            await log_and_parse("Рассылка сообщений + файлов по чатам",
                                SendTelegramMessages().sending_messages_files_via_chats)

        elif page.route == "/sending_personal_messages_with_limits":  # Отправка сообщений в личку (с лимитами)
            await SendTelegramMessages().send_message_from_all_accounts(account_limits=ConfigReader().get_limits())

        elif page.route == "/sending_files_to_personal_account_with_limits":  # Отправка файлов в личку (с лимитами)
            await SendTelegramMessages().send_files_to_personal_chats(account_limits=ConfigReader().get_limits())
        elif page.route == "/bio_editing":  # Меню "Редактирование_BIO"
            await bio_editing_menu(page)
        elif page.route == "/edit_description":
            await log_and_parse("Изменение описания", AccountBIO().change_bio_profile_gui, page)
        elif page.route == "/name_change":
            await log_and_parse("Изменение имени", AccountBIO().change_name_profile_gui, page)
        elif page.route == "/change_surname":
            await log_and_parse("Изменение фамилии", AccountBIO().change_last_name_profile_gui, page)
        elif page.route == "/edit_photo":
            await log_and_parse("Изменение фото", AccountBIO().change_photo_profile)
        elif page.route == "/changing_username":
            await log_and_parse("Изменение username", AccountBIO().change_username_profile_gui, page)
        elif page.route == "/settings":  # Меню "Настройки TelegramMaster"
            await settings_menu(page)
        elif page.route == "/recording_api_id_api_hash":
            await log_and_parse("Запись api_id, api_hash", SettingPage().writing_api_id_api_hash, page)
        elif page.route == "/message_limits":  # Лимиты на сообщения
            SettingPage().record_setting(page, "message_limits", "Введите лимит на сообщения")
        elif page.route == "/account_limits":  # Лимиты на аккаунт
            SettingPage().record_setting(page, "account_limits", "Введите лимит на аккаунт")
        elif page.route == "/creating_username_list":  # Формирование списка username
            SettingPage().output_the_input_field(page, "Введите список username", "members",
                                                 "username, id, access_hash, first_name, last_name, "
                                                 "user_phone, online_at, photos_id, user_premium",
                                                 "/settings", "members (username)")
        elif page.route == "/forming_list_of_chats_channels":  # Формирование списка чатов / каналов
            SettingPage().output_the_input_field(page, "Введите список ссылок на группы", "writing_group_links",
                                                 "writing_group_links", "/settings", "writing_group_links")
        elif page.route == "/link_entry":  # Запись ссылки для инвайтинга
            await DatabaseHandler().cleaning_db("links_inviting")  # Удаление списка с группами
            SettingPage().output_the_input_field(page, "Введите ссылку на группу для инвайтинга", "links_inviting",
                                                 "links_inviting", "/settings", "links_inviting")
        elif page.route == "/proxy_entry":
            await log_and_parse("Запись proxy",
                                SettingPage().creating_the_main_window_for_proxy_data_entry, page)
        elif page.route == "/message_recording":  # Запись сообщений

            SettingPage().recording_text_for_sending_messages(page, "Введите текст для сообщения",
                                                              get_unique_filename(
                                                                  base_filename='user_settings/message/message'))

        elif page.route == "/recording_reaction_link":  # Запись ссылки для реакций
            SettingPage().recording_text_for_sending_messages(page, "Введите текст сообщения",
                                                              'user_settings/reactions/link_channel.json')
        elif page.route == "/choice_of_reactions":
            await log_and_parse("Выбор реакций", reaction_gui, page)
        elif page.route == "/recording_the_time_between_messages":  # Запись времени между сообщениями
            SettingPage().create_main_window(page, variable="time_sending_messages")
        elif page.route == "/time_between_invites_sending_messages":  # Время между инвайтингом, рассылка сообщений
            SettingPage().create_main_window(page, variable="time_inviting")
        elif page.route == "/changing_accounts":  # Смена аккаунтов
            SettingPage().create_main_window(page, variable="time_changing_accounts")
        elif page.route == "/time_between_subscriptions":  # TODO проверить на повторное использование
            await log_and_parse("Запись времени", SettingPage().recording_the_time_to_launch_an_invite_every_day, page)
        elif page.route == "/time_between_subscriptionss":  # Время между подпиской
            SettingPage().create_main_window(page, variable="time_subscription")
        elif page.route == "/documentation":  # Открытие документации
            webbrowser.open_new("http://127.0.0.1:8000")
            await run_quart()

        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)


ft.app(target=telegram_master_main)

if __name__ == "__main__":
    asyncio.run(main())
