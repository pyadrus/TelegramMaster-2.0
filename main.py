# -*- coding: utf-8 -*-
import datetime

import flet as ft
from loguru import logger

from docs.app import run_quart
from system.account_actions.TGAccountBIO import AccountBIO
from system.account_actions.TGChek import TGChek
from system.account_actions.TGConnect import TGConnect
from system.account_actions.TGContact import TGContact
from system.account_actions.TGCreating import CreatingGroupsAndChats
from system.account_actions.TGInviting import InvitingToAGroup
from system.account_actions.TGInvitingScheduler import (launching_an_invite_once_an_hour,
                                                        launching_invite_every_day_certain_time, schedule_invite)
from system.account_actions.TGLimits import SettingLimits
from system.account_actions.TGParsing import ParsingGroupMembers
from system.account_actions.TGReactions import WorkingWithReactions
from system.account_actions.TGSendingMessages import SendTelegramMessages
from system.account_actions.TGSubUnsub import SubscribeUnsubscribeTelegram
from system.auxiliary_functions.auxiliary_functions import find_files, find_filess
from system.auxiliary_functions.config import (ConfigReader, height_button, small_button_width, line_width_button,
                                               program_name, program_version, date_of_program_change, window_width,
                                               window_height, window_resizable, path_parsing_folder,
                                               path_inviting_folder, path_subscription_folder, path_unsubscribe_folder,
                                               path_reactions_folder, path_contact_folder, path_creating_folder,
                                               path_send_message_folder, path_bio_folder)
from system.logging_in.logging_in import loging
from system.menu_gui.menu_gui import (inviting_menu, working_with_contacts_menu, message_distribution_menu,
                                      bio_editing_menu, settings_menu, menu_parsing, reactions_menu,
                                      subscribe_and_unsubscribe_menu, account_verification_menu,
                                      account_connection_menu, connecting_accounts_by_number_menu,
                                      connecting_accounts_by_session_menu)
from system.receiving_and_recording.receiving_and_recording import ReceivingAndRecording
from system.setting.setting import SettingPage, get_unique_filename, reaction_gui
from system.sqlite_working_tools.sqlite_working_tools import DatabaseHandler

logger.add("user_settings/log/log.log", rotation="2 MB", compression="zip")  # Логирование программы


async def show_notification(page: ft.Page, message: str):
    dlg = ft.AlertDialog(
        title=ft.Text(message),
        on_dismiss=lambda e: page.go("/"),  # Переход обратно после закрытия диалога
    )
    page.overlay.append(dlg)
    dlg.open = True
    page.update()


def main(page: ft.Page):
    page.title = f"{program_name}: {program_version} (Дата изменения {date_of_program_change})"
    page.window.width = window_width  # Ширина окна
    page.window.height = window_height  # Высота окна
    page.window.resizable = window_resizable  # Разрешение изменения размера окна
    logger.info(f"Program version: {program_version}. Date of change: {date_of_program_change}")



    async def route_change(route):

        await loging()

        page.views.clear()
        # Меню "Главное меню"
        page.views.append(
            ft.View("/", [ft.AppBar(title=ft.Text("Главное меню"),
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
                              ft.Row(
                                  [ft.ElevatedButton(width=small_button_width, height=height_button, text="🚀 Инвайтинг",
                                                     on_click=lambda _: page.go("/inviting")),
                                   ft.ElevatedButton(width=small_button_width, height=height_button, text="📊 Парсинг",
                                                     on_click=lambda _: page.go("/parsing")), ]),
                              ft.Row([ft.ElevatedButton(width=small_button_width, height=height_button,
                                                        text="📇 Работа с контактами",
                                                        on_click=lambda _: page.go("/working_with_contacts")),
                                      ft.ElevatedButton(width=small_button_width, height=height_button,
                                                        text="🔄 Подписка, отписка",
                                                        on_click=lambda _: page.go("/subscribe_unsubscribe")), ]),
                              ft.Row([ft.ElevatedButton(width=small_button_width, height=height_button,
                                                        text="🔐 Подключение аккаунтов",
                                                        on_click=lambda _: page.go("/account_connection_menu")),
                                      ft.ElevatedButton(width=small_button_width, height=height_button,
                                                        text="📤 Рассылка сообщений",
                                                        on_click=lambda _: page.go("/sending_messages")), ]),
                              ft.Row([ft.ElevatedButton(width=small_button_width, height=height_button,
                                                        text="❤️ Работа с реакциями",
                                                        on_click=lambda _: page.go("/working_with_reactions")),
                                      ft.ElevatedButton(width=small_button_width, height=height_button,
                                                        text="🔍 Проверка аккаунтов",
                                                        on_click=lambda _: page.go("/account_verification_menu")), ]),
                              ft.Row([ft.ElevatedButton(width=small_button_width, height=height_button,
                                                        text="👥 Создание групп (чатов)",
                                                        on_click=lambda _: page.go("/creating_groups")),
                                      ft.ElevatedButton(width=small_button_width, height=height_button,
                                                        text="✏️ Редактирование_BIO",
                                                        on_click=lambda _: page.go("/bio_editing")), ]),
                              ft.ElevatedButton(width=line_width_button, height=height_button, text="⚙️ Настройки",
                                                on_click=lambda _: page.go("/settings")),
                              ft.ElevatedButton(width=line_width_button, height=height_button, text="📖 Документация",
                                                on_click=lambda _: page.go("/documentation")),
                          ]), ]))
        # ______________________________________________________________________________________________________________
        if page.route == "/inviting":  # Меню "Инвайтинг"
            await inviting_menu(page)
        elif page.route == "/inviting_without_limits":  # Инвайтинг
            try:
                logger.info("⛔ Проверка наличия аккаунта в папке с аккаунтами")
                if not find_filess(directory_path=path_inviting_folder, extension='session'):
                    logger.error('⛔ Нет аккаунта в папке inviting')
                    await show_notification(page, "⛔ Нет аккаунта в папке inviting")
                    return None
                if len(await SettingLimits().get_usernames_with_limits(table_name="members",
                                                                       account_limits=ConfigReader().get_limits())) == 0:
                    logger.error('⛔ В таблице members нет пользователей для инвайтинга')
                    await show_notification(page, "⛔ В таблице members нет пользователей для инвайтинга")
                    return None
                else:
                    start = datetime.datetime.now()  # фиксируем и выводим время старта работы кода
                    logger.info('Время старта: ' + str(start))
                    logger.info("▶️ Начало Инвайтинга")
                    await InvitingToAGroup().inviting_without_limits(account_limits=ConfigReader().get_limits())
                    logger.info("🔚 Конец Инвайтинга")
                    finish = datetime.datetime.now()  # фиксируем и выводим время окончания работы кода
                    logger.info('Время окончания: ' + str(finish))
                    logger.info('Время работы: ' + str(finish - start))  # вычитаем время старта из времени окончания
            except Exception as e:
                logger.exception(f"Ошибка: {e}")
        elif page.route == "/inviting_1_time_per_hour":  # Инвайтинг 1 раз в час
            try:
                logger.info("⛔ Проверка наличия аккаунта в папке с аккаунтами")
                if not find_filess(directory_path=path_inviting_folder, extension='session'):
                    logger.error('⛔ Нет аккаунта в папке inviting')
                    await show_notification(page, "⛔ Нет аккаунта в папке inviting")
                    return None
                if len(await SettingLimits().get_usernames_with_limits(table_name="members",
                                                                       account_limits=ConfigReader().get_limits())) == 0:
                    logger.error('⛔ В таблице members нет пользователей для инвайтинга')
                    await show_notification(page, "⛔ В таблице members нет пользователей для инвайтинга")
                    return None
                else:
                    start = datetime.datetime.now()  # фиксируем и выводим время старта работы кода
                    logger.info('Время старта: ' + str(start))
                    logger.info("▶️ Начало Инвайтинга")
                    launching_an_invite_once_an_hour()
                    logger.info("🔚 Конец Инвайтинга")
                    finish = datetime.datetime.now()  # фиксируем и выводим время окончания работы кода
                    logger.info('Время окончания: ' + str(finish))
                    logger.info('Время работы: ' + str(finish - start))  # вычитаем время старта из времени окончания
            except Exception as e:
                logger.exception(f"Ошибка: {e}")
        elif page.route == "/inviting_certain_time":  # Инвайтинг в определенное время
            try:
                logger.info("⛔ Проверка наличия аккаунта в папке с аккаунтами")
                if not find_filess(directory_path=path_inviting_folder, extension='session'):
                    logger.error('⛔ Нет аккаунта в папке inviting')
                    await show_notification(page, "⛔ Нет аккаунта в папке inviting")
                    return None
                if len(await SettingLimits().get_usernames_with_limits(table_name="members",
                                                                       account_limits=ConfigReader().get_limits())) == 0:
                    logger.error('⛔ В таблице members нет пользователей для инвайтинга')
                    await show_notification(page, "⛔ В таблице members нет пользователей для инвайтинга")
                    return None
                else:
                    start = datetime.datetime.now()  # фиксируем и выводим время старта работы кода
                    logger.info('Время старта: ' + str(start))
                    logger.info("▶️ Начало Инвайтинга")
                    schedule_invite()
                    logger.info("🔚 Конец Инвайтинга")
                    finish = datetime.datetime.now()  # фиксируем и выводим время окончания работы кода
                    logger.info('Время окончания: ' + str(finish))
                    logger.info('Время работы: ' + str(finish - start))  # вычитаем время старта из времени окончания
            except Exception as e:
                logger.exception(f"Ошибка: {e}")
        elif page.route == "/inviting_every_day":  # Инвайтинг каждый день
            try:
                logger.info("⛔ Проверка наличия аккаунта в папке с аккаунтами")
                if not find_filess(directory_path=path_inviting_folder, extension='session'):
                    logger.error('⛔ Нет аккаунта в папке inviting')
                    await show_notification(page, "⛔ Нет аккаунта в папке inviting")
                    return None
                if len(await SettingLimits().get_usernames_with_limits(table_name="members",
                                                                       account_limits=ConfigReader().get_limits())) == 0:
                    logger.error('⛔ В таблице members нет пользователей для инвайтинга')
                    await show_notification(page, "⛔ В таблице members нет пользователей для инвайтинга")
                    return None
                else:
                    start = datetime.datetime.now()  # фиксируем и выводим время старта работы кода
                    logger.info('Время старта: ' + str(start))
                    logger.info("▶️ Начало Инвайтинга")
                    launching_invite_every_day_certain_time()
                    logger.info("🔚 Конец Инвайтинга")
                    finish = datetime.datetime.now()  # фиксируем и выводим время окончания работы кода
                    logger.info('Время окончания: ' + str(finish))
                    logger.info('Время работы: ' + str(finish - start))  # вычитаем время старта из времени окончания
            except Exception as e:
                logger.exception(f"Ошибка: {e}")
        # ______________________________________________________________________________________________________________
        elif page.route == "/account_verification_menu":  # Меню "Проверка аккаунтов"
            await account_verification_menu(page)
        elif page.route == "/validation_check":  # Проверка на валидность
            await TGChek().validation_check()
        elif page.route == "/checking_for_spam_bots":  # Проверка через спам бот
            await TGChek().checking_for_spam_bots()
        elif page.route == "/renaming_accounts":  # Переименование аккаунтов
            await TGChek().renaming_accounts()
        elif page.route == "/full_verification":  # Полная проверка
            await TGChek().full_verification()
        # ______________________________________________________________________________________________________________
        elif page.route == "/subscribe_unsubscribe":  # Меню "Подписка и отписка"
            await subscribe_and_unsubscribe_menu(page)
        elif page.route == "/subscription_all":  # Подписка
            try:
                logger.info("⛔ Проверка наличия аккаунта в папке с аккаунтами")
                if not find_filess(directory_path=path_subscription_folder, extension='session'):
                    logger.error('⛔ Нет аккаунта в папке subscription')
                    await show_notification(page, "⛔ Нет аккаунта в папке subscription")
                    return None
                else:
                    start = datetime.datetime.now()  # фиксируем и выводим время старта работы кода
                    logger.info('Время старта: ' + str(start))
                    logger.info("▶️ Начало Подписки")
                    await SubscribeUnsubscribeTelegram().subscribe_telegram()
                    logger.info("🔚 Конец Подписки")
                    finish = datetime.datetime.now()  # фиксируем и выводим время окончания работы кода
                    logger.info('Время окончания: ' + str(finish))
                    logger.info('Время работы: ' + str(finish - start))  # вычитаем время старта из времени окончания
            except Exception as e:
                logger.exception(f"Ошибка: {e}")
        elif page.route == "/unsubscribe_all":  # Отписываемся
            try:
                logger.info("⛔ Проверка наличия аккаунта в папке с аккаунтами")
                if not find_filess(directory_path=path_unsubscribe_folder, extension='session'):
                    logger.error('⛔ Нет аккаунта в папке unsubscribe')
                    await show_notification(page, "⛔ Нет аккаунта в папке unsubscribe")
                    return None
                else:
                    start = datetime.datetime.now()  # фиксируем и выводим время старта работы кода
                    logger.info('Время старта: ' + str(start))
                    logger.info("▶️ Начало Отписка")
                    await SubscribeUnsubscribeTelegram().unsubscribe_all()
                    logger.info("🔚 Конец Отписки")
                    finish = datetime.datetime.now()  # фиксируем и выводим время окончания работы кода
                    logger.info('Время окончания: ' + str(finish))
                    logger.info('Время работы: ' + str(finish - start))  # вычитаем время старта из времени окончания
            except Exception as e:
                logger.exception(f"Ошибка: {e}")
        # ______________________________________________________________________________________________________________
        elif page.route == "/working_with_reactions":  # Меню "Работа с реакциями"
            await reactions_menu(page)
        elif page.route == "/setting_reactions":  # Ставим реакции
            try:
                logger.info("⛔ Проверка наличия аккаунта в папке с аккаунтами")
                if not find_filess(directory_path=path_reactions_folder, extension='session'):
                    logger.error('⛔ Нет аккаунта в папке reactions')
                    await show_notification(page, "⛔ Нет аккаунта в папке reactions")
                    return None
                else:
                    start = datetime.datetime.now()  # фиксируем и выводим время старта работы кода
                    logger.info('Время старта: ' + str(start))
                    logger.info("▶️ Начало Проставления реакций")
                    await WorkingWithReactions().send_reaction_request(page)
                    logger.info("🔚 Конец Проставления реакций")
                    finish = datetime.datetime.now()  # фиксируем и выводим время окончания работы кода
                    logger.info('Время окончания: ' + str(finish))
                    logger.info('Время работы: ' + str(finish - start))  # вычитаем время старта из времени окончания
            except Exception as e:
                logger.exception(f"Ошибка: {e}")
        elif page.route == "/we_are_winding_up_post_views":  # Накручиваем просмотры постов
            try:
                logger.info("⛔ Проверка наличия аккаунта в папке с аккаунтами")
                if not find_filess(directory_path=path_reactions_folder, extension='session'):
                    logger.error('⛔ Нет аккаунта в папке reactions')
                    await show_notification(page, "⛔ Нет аккаунта в папке reactions")
                    return None
                else:
                    start = datetime.datetime.now()  # фиксируем и выводим время старта работы кода
                    logger.info('Время старта: ' + str(start))
                    logger.info("▶️ Начало Накрутки просмотров постов")
                    await WorkingWithReactions().viewing_posts()
                    logger.info("🔚 Конец Накрутки просмотров постов")
                    finish = datetime.datetime.now()  # фиксируем и выводим время окончания работы кода
                    logger.info('Время окончания: ' + str(finish))
                    logger.info('Время работы: ' + str(finish - start))  # вычитаем время старта из времени окончания
            except Exception as e:
                logger.exception(f"Ошибка: {e}")
        elif page.route == "/automatic_setting_of_reactions":  # Автоматическое выставление реакций
            try:
                logger.info("⛔ Проверка наличия аккаунта в папке с аккаунтами")
                if not find_filess(directory_path=path_reactions_folder, extension='session'):
                    logger.error('⛔ Нет аккаунта в папке reactions')
                    await show_notification(page, "⛔ Нет аккаунта в папке reactions")
                    return None
                else:
                    start = datetime.datetime.now()  # фиксируем и выводим время старта работы кода
                    logger.info('Время старта: ' + str(start))
                    logger.info("▶️ Начало Автоматического выставления реакций")
                    await WorkingWithReactions().setting_reactions()
                    logger.info("🔚 Конец Автоматического выставления реакций")
                    finish = datetime.datetime.now()  # фиксируем и выводим время окончания работы кода
                    logger.info('Время окончания: ' + str(finish))
                    logger.info('Время работы: ' + str(finish - start))  # вычитаем время старта из времени окончания
            except Exception as e:
                logger.exception(f"Ошибка: {e}")
        # ______________________________________________________________________________________________________________
        elif page.route == "/parsing":  # Меню "Парсинг"
            await menu_parsing(page)
        elif page.route == "/parsing_single_groups":
            try:
                logger.info("⛔ Проверка наличия аккаунта в папке с аккаунтами")
                if not find_filess(directory_path=path_parsing_folder, extension='session'):
                    logger.error('⛔ Нет аккаунта в папке parsing')
                    await show_notification(page, "⛔ Нет аккаунта в папке parsing")
                    return None
                else:
                    start = datetime.datetime.now()  # фиксируем и выводим время старта работы кода
                    logger.info('Время старта: ' + str(start))
                    logger.info("▶️ Начало парсинга")
                    await ParsingGroupMembers().parse_groups()
                    logger.info("🔚 Конец парсинга")
                    finish = datetime.datetime.now()  # фиксируем и выводим время окончания работы кода
                    logger.info('Время окончания: ' + str(finish))
                    logger.info('Время работы: ' + str(finish - start))  # вычитаем время старта из времени окончания
            except Exception as e:
                logger.exception(f"Ошибка: {e}")




        elif page.route == "/parsing_selected_group_user_subscribed":  # Парсинг выбранной группы
            try:
                logger.info("⛔ Проверка наличия аккаунта в папке с аккаунтами")
                if not find_filess(directory_path=path_parsing_folder, extension='session'):
                    logger.error('⛔ Нет аккаунта в папке parsing')
                    await show_notification(page, "⛔ Нет аккаунта в папке parsing")
                    return None
                else:
                    start = datetime.datetime.now()  # фиксируем и выводим время старта работы кода
                    logger.info('Время старта: ' + str(start))
                    logger.info("▶️ Начало парсинга")
                    await ParsingGroupMembers().choose_and_parse_group(page)
                    logger.info("🔚 Конец парсинга")
                    finish = datetime.datetime.now()  # фиксируем и выводим время окончания работы кода
                    logger.info('Время окончания: ' + str(finish))
                    logger.info('Время работы: ' + str(finish - start))  # вычитаем время старта из времени окончания
            except Exception as e:
                logger.exception(f"Ошибка: {e}")




        elif page.route == "/parsing_active_group_members":  # Парсинг активных участников группы
            try:
                logger.info("⛔ Проверка наличия аккаунта в папке с аккаунтами")
                if not find_filess(directory_path=path_parsing_folder, extension='session'):
                    logger.error('⛔ Нет аккаунта в папке parsing')
                    await show_notification(page, "⛔ Нет аккаунта в папке parsing")
                    return None
                else:
                    start = datetime.datetime.now()  # фиксируем и выводим время старта работы кода
                    logger.info('Время старта: ' + str(start))
                    logger.info("▶️ Начало парсинга")
                    await ParsingGroupMembers().entering_data_for_parsing_active(page)
                    logger.info("🔚 Конец парсинга")
                    finish = datetime.datetime.now()  # фиксируем и выводим время окончания работы кода
                    logger.info('Время окончания: ' + str(finish))
                    logger.info('Время работы: ' + str(finish - start))  # вычитаем время старта из времени окончания
            except Exception as e:
                logger.exception(f"Ошибка: {e}")



        elif page.route == "/parsing_groups_channels_account_subscribed":  # Парсинг групп / каналов аккаунта
            try:
                logger.info("⛔ Проверка наличия аккаунта в папке с аккаунтами")
                if not find_filess(directory_path=path_parsing_folder, extension='session'):
                    logger.error('⛔ Нет аккаунта в папке parsing')
                    await show_notification(page, "⛔ Нет аккаунта в папке parsing")
                    return None
                else:
                    start = datetime.datetime.now()  # фиксируем и выводим время старта работы кода
                    logger.info('Время старта: ' + str(start))
                    logger.info("▶️ Начало парсинга")
                    await ParsingGroupMembers().parse_subscribed_groups()
                    logger.info("🔚 Конец парсинга")
                    finish = datetime.datetime.now()  # фиксируем и выводим время окончания работы кода
                    logger.info('Время окончания: ' + str(finish))
                    logger.info('Время работы: ' + str(finish - start))  # вычитаем время старта из времени окончания
            except Exception as e:
                logger.exception(f"Ошибка: {e}")



        elif page.route == "/clearing_list_previously_saved_data":  # Очистка списка от ранее спарсенных данных
            await DatabaseHandler().cleaning_db("members")


        elif page.route == "/importing_a_list_of_parsed_data":  # 📋 Импорт списка от ранее спарсенных данных
            await ReceivingAndRecording().write_data_to_excel(file_name="user_settings/parsed_chat_participants.xlsx")
        # ______________________________________________________________________________________________________________
        elif page.route == "/working_with_contacts":  # Меню "Работа с контактами"
            await working_with_contacts_menu(page)
        elif page.route == "/creating_contact_list":  # Формирование списка контактов
            try:
                logger.info("⛔ Проверка наличия аккаунта в папке с аккаунтами")
                if not find_filess(directory_path=path_contact_folder, extension='session'):
                    logger.error('⛔ Нет аккаунта в папке contact')
                    await show_notification(page, "⛔ Нет аккаунта в папке contact")
                    return None
                else:
                    start = datetime.datetime.now()  # фиксируем и выводим время старта работы кода
                    logger.info('Время старта: ' + str(start))
                    logger.info("▶️ Начало Формирования списка контактов")
                    await DatabaseHandler().open_and_read_data("contact")  # Удаление списка с контактами
                    SettingPage().output_the_input_field(page, "Введите список номеров телефонов", "contact",
                                                         "contact", "/working_with_contacts", "contact")
                    logger.info("🔚 Конец Формирования списка контактов")
                    finish = datetime.datetime.now()  # фиксируем и выводим время окончания работы кода
                    logger.info('Время окончания: ' + str(finish))
                    logger.info('Время работы: ' + str(finish - start))  # вычитаем время старта из времени окончания
            except Exception as e:
                logger.exception(f"Ошибка: {e}")
        elif page.route == "/show_list_contacts":  # Показать список контактов
            try:
                logger.info("⛔ Проверка наличия аккаунта в папке с аккаунтами")
                if not find_filess(directory_path=path_contact_folder, extension='session'):
                    logger.error('⛔ Нет аккаунта в папке contact')
                    await show_notification(page, "⛔ Нет аккаунта в папке contact")
                    return None
                else:
                    start = datetime.datetime.now()  # фиксируем и выводим время старта работы кода
                    logger.info('Время старта: ' + str(start))
                    logger.info("▶️ Начало Показа списка контактов")
                    await TGContact().show_account_contact_list()
                    logger.info("🔚 Конец Показа списка контактов")
                    finish = datetime.datetime.now()  # фиксируем и выводим время окончания работы кода
                    logger.info('Время окончания: ' + str(finish))
                    logger.info('Время работы: ' + str(finish - start))  # вычитаем время старта из времени окончания
            except Exception as e:
                logger.exception(f"Ошибка: {e}")
        elif page.route == "/deleting_contacts":  # Удаление контактов
            try:
                logger.info("⛔ Проверка наличия аккаунта в папке с аккаунтами")
                if not find_filess(directory_path=path_contact_folder, extension='session'):
                    logger.error('⛔ Нет аккаунта в папке contact')
                    await show_notification(page, "⛔ Нет аккаунта в папке contact")
                    return None
                else:
                    start = datetime.datetime.now()  # фиксируем и выводим время старта работы кода
                    logger.info('Время старта: ' + str(start))
                    logger.info("▶️ Начало Удаления контактов")
                    await TGContact().delete_contact()
                    logger.info("🔚 Конец Удаления контактов")
                    finish = datetime.datetime.now()  # фиксируем и выводим время окончания работы кода
                    logger.info('Время окончания: ' + str(finish))
                    logger.info('Время работы: ' + str(finish - start))  # вычитаем время старта из времени окончания
            except Exception as e:
                logger.exception(f"Ошибка: {e}")
        elif page.route == "/adding_contacts":  # Добавление контактов
            try:
                logger.info("⛔ Проверка наличия аккаунта в папке с аккаунтами")
                if not find_filess(directory_path=path_contact_folder, extension='session'):
                    logger.error('⛔ Нет аккаунта в папке contact')
                    await show_notification(page, "⛔ Нет аккаунта в папке contact")
                    return None
                else:
                    start = datetime.datetime.now()  # фиксируем и выводим время старта работы кода
                    logger.info('Время старта: ' + str(start))
                    logger.info("▶️ Начало Добавления контактов")
                    await TGContact().inviting_contact()
                    logger.info("🔚 Конец Добавления контактов")
                    finish = datetime.datetime.now()  # фиксируем и выводим время окончания работы кода
                    logger.info('Время окончания: ' + str(finish))
                    logger.info('Время работы: ' + str(finish - start))  # вычитаем время старта из времени окончания
            except Exception as e:
                logger.exception(f"Ошибка: {e}")
        # ______________________________________________________________________________________________________________
        elif page.route == "/account_connection_menu":  # Подключение аккаунтов 'меню'.
            await account_connection_menu(page)
        # _______________________________________________________________________________________________________________
        elif page.route == "/connecting_accounts_by_number":  # Подключение аккаунтов по номеру телефона 'Меню'
            await connecting_accounts_by_number_menu(page)
        elif page.route == "/account_connection_number_answering_machine":  # Для автоответчика
            await TGConnect().connecting_number_accounts(page, 'answering_machine', 'автоответчика')
        elif page.route == "/account_connection_number_bio":  # Для редактирования BIO
            await TGConnect().connecting_number_accounts(page, 'bio', 'редактирования BIO')
        elif page.route == "/account_connection_number_contact":  # Для работы с номерами
            await TGConnect().connecting_number_accounts(page, 'contact', 'работы с номерами')
        elif page.route == "/account_connection_number_creating":  # Для создания групп
            await TGConnect().connecting_number_accounts(page, 'creating', 'создания групп')
        elif page.route == "/account_connection_number_inviting":  # Для инвайтинга
            await TGConnect().connecting_number_accounts(page, 'inviting', 'инвайтинга')
        elif page.route == "/account_connection_number_parsing":  # Для парсинга
            await TGConnect().connecting_number_accounts(page, 'parsing', 'парсинга')
        elif page.route == "/account_connection_number_reactions":  # Для работы с реакциями
            await TGConnect().connecting_number_accounts(page, 'reactions', 'работы с реакциями')
        elif page.route == "/account_connection_number_reactions_list":  # Для проставления реакций
            await TGConnect().connecting_number_accounts(page, 'reactions_list', 'проставления реакций')
        elif page.route == "/account_connection_number_send_message":  # Для рассылки сообщений
            await TGConnect().connecting_number_accounts(page, 'send_message', 'рассылки сообщений')
        elif page.route == "/account_connection_number_subscription":  # Для подписки
            await TGConnect().connecting_number_accounts(page, 'subscription', 'подписки')
        elif page.route == "/account_connection_number_unsubscribe":  # Для отписки
            await TGConnect().connecting_number_accounts(page, 'unsubscribe', 'отписки')
        elif page.route == "/account_connection_number_viewing":  # Для накрутки просмотров
            await TGConnect().connecting_number_accounts(page, 'viewing', 'накрутки просмотров')
        # _______________________________________________________________________________________________________________
        elif page.route == "/connecting_accounts_by_session":  # Подключение session аккаунтов 'Меню'
            await connecting_accounts_by_session_menu(page)
        elif page.route == "/account_connection_session_answering_machine":  # Для автоответчика (session)
            await TGConnect().connecting_session_accounts(page, 'answering_machine', 'автоответчика')
        elif page.route == "/account_connection_session_bio":  # Для редактирования BIO (session)
            await TGConnect().connecting_session_accounts(page, 'bio', 'редактирования BIO')
        elif page.route == "/account_connection_session_contact":  # Для работы с номерами (session)
            await TGConnect().connecting_session_accounts(page, 'contact', 'работы с номерами')
        elif page.route == "/account_connection_session_creating":  # Для создания групп (session)
            await TGConnect().connecting_session_accounts(page, 'creating', 'создания групп')
        elif page.route == "/account_connection_session_inviting":  # Для инвайтинга (session)
            await TGConnect().connecting_session_accounts(page, 'inviting', 'инвайтинга')
        elif page.route == "/account_connection_session_parsing":  # Для парсинга (session)
            await TGConnect().connecting_session_accounts(page, 'parsing', 'парсинга')
        elif page.route == "/account_connection_session_reactions":  # Для работы с реакциями (session)
            await TGConnect().connecting_session_accounts(page, 'reactions', 'работы с реакциями')
        elif page.route == "/account_connection_session_reactions_list":  # Для проставления реакций (session)
            await TGConnect().connecting_session_accounts(page, 'reactions_list', 'проставления реакций')
        elif page.route == "/account_connection_session_send_message":  # Для рассылки сообщений (session)
            await TGConnect().connecting_session_accounts(page, 'send_message', 'рассылки сообщений')
        elif page.route == "/account_connection_session_subscription":  # Для подписки (session)
            await TGConnect().connecting_session_accounts(page, 'subscription', 'подписки')
        elif page.route == "/account_connection_session_unsubscribe":  # Для отписки (session)
            await TGConnect().connecting_session_accounts(page, 'unsubscribe', 'отписки')
        elif page.route == "/account_connection_session_viewing":  # Для накрутки просмотров (session)
            await TGConnect().connecting_session_accounts(page, 'viewing', 'накрутки просмотров')
        # _______________________________________________________________________________________________________________
        elif page.route == "/creating_groups":  # Создание групп (чатов)
            try:
                logger.info("⛔ Проверка наличия аккаунта в папке с аккаунтами")
                if not find_filess(directory_path=path_creating_folder, extension='session'):
                    logger.error('⛔ Нет аккаунта в папке creating')
                    await show_notification(page, "⛔ Нет аккаунта в папке creating")
                    return None
                else:
                    start = datetime.datetime.now()  # фиксируем и выводим время старта работы кода
                    logger.info('Время старта: ' + str(start))
                    logger.info("▶️ Начало Создания групп (чатов)")
                    await CreatingGroupsAndChats().creating_groups_and_chats()
                    logger.info("🔚 Конец Создания групп (чатов)")
                    finish = datetime.datetime.now()  # фиксируем и выводим время окончания работы кода
                    logger.info('Время окончания: ' + str(finish))
                    logger.info('Время работы: ' + str(finish - start))  # вычитаем время старта из времени окончания
            except Exception as e:
                logger.exception(f"Ошибка: {e}")
        # _______________________________________________________________________________________________________________
        elif page.route == "/sending_messages":  # Меню "Рассылка сообщений"
            await message_distribution_menu(page)
        elif page.route == "/sending_messages_via_chats":  # Рассылка сообщений по чатам
            try:
                logger.info("⛔ Проверка наличия аккаунта в папке с аккаунтами")
                if not find_filess(directory_path=path_send_message_folder, extension='session'):
                    logger.error('⛔ Нет аккаунта в папке parsing')
                    await show_notification(page, "Нет аккаунта в папке send_message")
                    return None
                logger.info("⛔ Проверка папки с сообщениями на наличие заготовленных сообщений")
                if not find_filess(directory_path="user_settings/message", extension='json'):
                    logger.error('⛔ Нет заготовленных сообщений в папке message')
                    await show_notification(page, "⛔ Нет заготовленных сообщений в папке message")
                    return None
                else:
                    start = datetime.datetime.now()  # фиксируем и выводим время старта работы кода
                    logger.info('Время старта: ' + str(start))
                    logger.info("▶️ Начало Рассылки сообщений по чатам")
                    entities = find_files(directory_path="user_settings/message", extension="json")
                    logger.info(entities)
                    await SendTelegramMessages().sending_messages_via_chats_times()
                    logger.info("🔚 Конец Рассылки сообщений по чатам")
                    finish = datetime.datetime.now()  # фиксируем и выводим время окончания работы кода
                    logger.info('Время окончания: ' + str(finish))
                    logger.info('Время работы: ' + str(finish - start))  # вычитаем время старта из времени окончания
            except Exception as e:
                logger.exception(f"Ошибка: {e}")
        elif page.route == "/sending_messages_via_chats_with_answering_machine":  # Рассылка сообщений по чатам с автоответчиком
            try:
                logger.info("⛔ Проверка наличия аккаунта в папке с аккаунтами")
                if not find_filess(directory_path=path_send_message_folder, extension='session'):
                    logger.error('⛔ Нет аккаунта в папке parsing')
                    await show_notification(page, "⛔ Нет аккаунта в папке send_message")
                    return None
                logger.info("⛔ Проверка папки с сообщениями на наличие заготовленных сообщений")
                if not find_filess(directory_path="user_settings/message", extension='json'):
                    logger.error('⛔ Нет заготовленных сообщений в папке message')
                    await show_notification(page, "⛔ Нет заготовленных сообщений в папке message")
                    return None
                logger.info("⛔ Проверка папки с сообщениями для автоответчика")
                if not find_filess(directory_path="user_settings/answering_machine", extension='json'):
                    logger.error('⛔ Нет заготовленных сообщений для автоответчика в папке answering_machine')
                    await show_notification(page,
                                            "⛔ Нет заготовленных сообщений для автоответчика в папке answering_machine")
                    return None
                else:
                    start = datetime.datetime.now()  # фиксируем и выводим время старта работы кода
                    logger.info('Время старта: ' + str(start))
                    logger.info("▶️ Начало Рассылки сообщений по чатам с автоответчиком")
                    await SendTelegramMessages().answering_machine()
                    logger.info("🔚 Конец Рассылки сообщений по чатам с автоответчиком")
                    finish = datetime.datetime.now()  # фиксируем и выводим время окончания работы кода
                    logger.info('Время окончания: ' + str(finish))
                    logger.info('Время работы: ' + str(finish - start))  # вычитаем время старта из времени окончания
            except Exception as e:
                logger.exception(f"Ошибка: {e}")
        elif page.route == "/sending_files_via_chats":  # Рассылка файлов по чатам
            try:
                logger.info("⛔ Проверка наличия аккаунта в папке с аккаунтами")
                if not find_filess(directory_path=path_send_message_folder, extension='session'):
                    logger.error('⛔ Нет аккаунта в папке parsing')
                    await show_notification(page, "⛔ Нет аккаунта в папке send_message")
                    return None
                else:
                    start = datetime.datetime.now()  # фиксируем и выводим время старта работы кода
                    logger.info('Время старта: ' + str(start))
                    logger.info("▶️ Начало Рассылки файлов по чатам")
                    await SendTelegramMessages().sending_files_via_chats()
                    logger.info("🔚 Конец Рассылки файлов по чатам")
                    finish = datetime.datetime.now()  # фиксируем и выводим время окончания работы кода
                    logger.info('Время окончания: ' + str(finish))
                    logger.info('Время работы: ' + str(finish - start))  # вычитаем время старта из времени окончания
            except Exception as e:
                logger.exception(f"Ошибка: {e}")
        elif page.route == "/sending_messages_files_via_chats":  # Рассылка сообщений + файлов по чатам
            try:
                logger.info("⛔ Проверка наличия аккаунта в папке с аккаунтами")
                if not find_filess(directory_path=path_send_message_folder, extension='session'):
                    logger.error('⛔ Нет аккаунта в папке parsing')
                    await show_notification(page, "⛔ Нет аккаунта в папке send_message")
                    return None
                logger.info("⛔ Проверка папки с сообщениями на наличие заготовленных сообщений")
                if not find_filess(directory_path="user_settings/message", extension='json'):
                    logger.error('⛔ Нет заготовленных сообщений в папке message')
                    await show_notification(page, "⛔ Нет заготовленных сообщений в папке message")
                    return None
                else:
                    start = datetime.datetime.now()  # фиксируем и выводим время старта работы кода
                    logger.info('Время старта: ' + str(start))
                    logger.info("▶️ Начало отправки сообщений + файлов по чатам")
                    await SendTelegramMessages().sending_messages_files_via_chats()
                    logger.info("🔚 Конец отправки сообщений + файлов по чатам")
                    finish = datetime.datetime.now()  # фиксируем и выводим время окончания работы кода
                    logger.info('Время окончания: ' + str(finish))
                    logger.info('Время работы: ' + str(finish - start))  # вычитаем время старта из времени окончания
            except Exception as e:
                logger.exception(f"Ошибка: {e}")
        elif page.route == "/sending_personal_messages_with_limits":  # Отправка сообщений в личку (с лимитами)
            try:
                logger.info("⛔ Проверка наличия аккаунта в папке с аккаунтами")
                if not find_filess(directory_path=path_send_message_folder, extension='session'):
                    logger.error('⛔ Нет аккаунта в папке parsing')
                    await show_notification(page, "⛔ Нет аккаунта в папке send_message")
                    return None

                logger.info("⛔ Проверка папки с сообщениями на наличие заготовленных сообщений")
                if not find_filess(directory_path="user_settings/message", extension='json'):
                    logger.error('⛔ Нет заготовленных сообщений в папке message')
                    await show_notification(page, "⛔ Нет заготовленных сообщений в папке message")
                    return None
                else:
                    start = datetime.datetime.now()  # фиксируем и выводим время старта работы кода
                    logger.info('Время старта: ' + str(start))
                    logger.info("▶️ Начало отправки сообщений в личку")
                    await SendTelegramMessages().send_message_from_all_accounts(
                        account_limits=ConfigReader().get_limits())
                    logger.info("🔚 Конец отправки сообщений в личку")
                    finish = datetime.datetime.now()  # фиксируем и выводим время окончания работы кода
                    logger.info('Время окончания: ' + str(finish))
                    logger.info('Время работы: ' + str(finish - start))  # вычитаем время старта из времени окончания
            except Exception as e:
                logger.exception(f"Ошибка: {e}")
        elif page.route == "/sending_files_to_personal_account_with_limits":  # Отправка файлов в личку (с лимитами)
            try:
                logger.info("⛔ Проверка наличия аккаунта в папке с аккаунтами")
                if not find_filess(directory_path=path_send_message_folder, extension='session'):
                    logger.error('⛔ Нет аккаунта в папке parsing')
                    await show_notification(page, "⛔ Нет аккаунта в папке send_message")
                    return None
                else:
                    start = datetime.datetime.now()  # фиксируем и выводим время старта работы кода
                    logger.info('Время старта: ' + str(start))
                    logger.info("▶️ Начало отправки файлов в личку")
                    await SendTelegramMessages().send_files_to_personal_chats(
                        account_limits=ConfigReader().get_limits())
                    logger.info("🔚 Конец отправки файлов в личку")
                    finish = datetime.datetime.now()  # фиксируем и выводим время окончания работы кода
                    logger.info('Время окончания: ' + str(finish))
                    logger.info('Время работы: ' + str(finish - start))  # вычитаем время старта из времени окончания
            except Exception as e:
                logger.exception(f"Ошибка: {e}")
        # ______________________________________________________________________________________________________________
        elif page.route == "/bio_editing":  # Меню "Редактирование_BIO"
            await bio_editing_menu(page)
        elif page.route == "/edit_description":  # Изменение описания
            try:
                logger.info("⛔ Проверка наличия аккаунта в папке с аккаунтами")
                if not find_filess(directory_path=path_bio_folder, extension='session'):
                    logger.error('⛔ Нет аккаунта в папке parsing')
                    await show_notification(page, "⛔ Нет аккаунта в папке bio")
                    return None
                else:
                    start = datetime.datetime.now()  # фиксируем и выводим время старта работы кода
                    logger.info('Время старта: ' + str(start))
                    logger.info("▶️ Начало Изменения описания")
                    await AccountBIO().change_bio_profile_gui(page)
                    logger.info("🔚 Конец Изменения описания")
                    finish = datetime.datetime.now()  # фиксируем и выводим время окончания работы кода
                    logger.info('Время окончания: ' + str(finish))
                    logger.info('Время работы: ' + str(finish - start))  # вычитаем время старта из времени окончания
            except Exception as e:
                logger.exception(f"Ошибка: {e}")
        elif page.route == "/name_change":  # Изменение имени
            try:
                logger.info("⛔ Проверка наличия аккаунта в папке с аккаунтами")
                if not find_filess(directory_path=path_bio_folder, extension='session'):
                    logger.error('⛔ Нет аккаунта в папке parsing')
                    await show_notification(page, "⛔ Нет аккаунта в папке bio")
                    return None
                else:
                    start = datetime.datetime.now()  # фиксируем и выводим время старта работы кода
                    logger.info('Время старта: ' + str(start))
                    logger.info("▶️ Начало Изменения имени")
                    await AccountBIO().change_name_profile_gui(page)
                    logger.info("🔚 Конец Изменения имени")
                    finish = datetime.datetime.now()  # фиксируем и выводим время окончания работы кода
                    logger.info('Время окончания: ' + str(finish))
                    logger.info('Время работы: ' + str(finish - start))  # вычитаем время старта из времени окончания
            except Exception as e:
                logger.exception(f"Ошибка: {e}")
        elif page.route == "/change_surname":  # Изменение фамилии
            try:
                logger.info("⛔ Проверка наличия аккаунта в папке с аккаунтами")
                if not find_filess(directory_path=path_bio_folder, extension='session'):
                    logger.error('⛔ Нет аккаунта в папке parsing')
                    await show_notification(page, "⛔ Нет аккаунта в папке bio")
                    return None
                else:
                    start = datetime.datetime.now()  # фиксируем и выводим время старта работы кода
                    logger.info('Время старта: ' + str(start))
                    logger.info("▶️ Начало Изменения фамилии")
                    await AccountBIO().change_last_name_profile_gui(page)
                    logger.info("🔚 Конец Изменения фамилии")
                    finish = datetime.datetime.now()  # фиксируем и выводим время окончания работы кода
                    logger.info('Время окончания: ' + str(finish))
                    logger.info('Время работы: ' + str(finish - start))  # вычитаем время старта из времени окончания
            except Exception as e:
                logger.exception(f"Ошибка: {e}")
        elif page.route == "/edit_photo":  # Изменение фото
            try:
                logger.info("⛔ Проверка наличия аккаунта в папке с аккаунтами")
                if not find_filess(directory_path=path_bio_folder, extension='session'):
                    logger.error('⛔ Нет аккаунта в папке parsing')
                    await show_notification(page, "⛔ Нет аккаунта в папке bio")
                    return None
                else:
                    start = datetime.datetime.now()  # фиксируем и выводим время старта работы кода
                    logger.info('Время старта: ' + str(start))
                    logger.info("▶️ Начало Изменения фото")
                    await AccountBIO().change_photo_profile()
                    logger.info("🔚 Конец Изменения фото")
                    finish = datetime.datetime.now()  # фиксируем и выводим время окончания работы кода
                    logger.info('Время окончания: ' + str(finish))
                    logger.info('Время работы: ' + str(finish - start))  # вычитаем время старта из времени окончания
            except Exception as e:
                logger.exception(f"Ошибка: {e}")
        elif page.route == "/changing_username":  # Изменение username
            try:
                logger.info("⛔ Проверка наличия аккаунта в папке с аккаунтами")
                if not find_filess(directory_path=path_bio_folder, extension='session'):
                    logger.error('⛔ Нет аккаунта в папке parsing')
                    await show_notification(page, "⛔ Нет аккаунта в папке bio")
                    return None
                else:
                    start = datetime.datetime.now()  # фиксируем и выводим время старта работы кода
                    logger.info('Время старта: ' + str(start))
                    logger.info("▶️ Начало Изменения username")
                    await AccountBIO().change_username_profile_gui(page)
                    logger.info("🔚 Конец Изменения username")
                    finish = datetime.datetime.now()  # фиксируем и выводим время окончания работы кода
                    logger.info('Время окончания: ' + str(finish))
                    logger.info('Время работы: ' + str(finish - start))  # вычитаем время старта из времени окончания
            except Exception as e:
                logger.exception(f"Ошибка: {e}")
        # ______________________________________________________________________________________________________________
        elif page.route == "/settings":  # Меню "Настройки TelegramMaster"
            await settings_menu(page)
        elif page.route == "/recording_api_id_api_hash":  # Запись api_id, api_hash
            await SettingPage().writing_api_id_api_hash(page)
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
        elif page.route == "/proxy_entry":  # Запись proxy
            await SettingPage().creating_the_main_window_for_proxy_data_entry(page)
        elif page.route == "/message_recording":  # Запись сообщений
            SettingPage().recording_text_for_sending_messages(page, "Введите текст для сообщения",
                                                              get_unique_filename(
                                                                  base_filename='user_settings/message/message'))
        elif page.route == "/recording_reaction_link":  # Запись ссылки для реакций
            SettingPage().recording_text_for_sending_messages(page, "Введите текст сообщения",
                                                              'user_settings/reactions/link_channel.json')
        elif page.route == "/choice_of_reactions":  # Выбор реакций
            await reaction_gui(page)
        elif page.route == "/recording_the_time_between_messages":  # Запись времени между сообщениями
            SettingPage().create_main_window(page, variable="time_sending_messages")
        elif page.route == "/time_between_invites_sending_messages":  # Время между инвайтингом, рассылка сообщений
            SettingPage().create_main_window(page, variable="time_inviting")
        elif page.route == "/changing_accounts":  # Смена аккаунтов
            SettingPage().create_main_window(page, variable="time_changing_accounts")
        elif page.route == "/time_between_subscriptions":
            await SettingPage().recording_the_time_to_launch_an_invite_every_day(page)
        elif page.route == "/time_between_subscriptionss":  # Время между подпиской
            SettingPage().create_main_window(page, variable="time_subscription")
        elif page.route == "/documentation":  # Открытие документации
            await run_quart()
        elif page.route == "/errors":
            # Пустая страница с уведомлением
            page.views.append(ft.View("/errors", []))

        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)


ft.app(target=main)
