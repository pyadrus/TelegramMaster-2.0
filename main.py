import flet as ft
from loguru import logger
from telethon.errors import PeerFloodError, AuthKeyDuplicatedError, FloodWaitError, UserPrivacyRestrictedError, \
    UserChannelsTooMuchError, UserBannedInChannelError, ChatWriteForbiddenError, BotGroupsBlockedError, \
    UserNotMutualContactError, ChatAdminRequiredError, UserKickedError, ChannelPrivateError, UserIdInvalidError, \
    UsernameNotOccupiedError, UsernameInvalidError, InviteRequestSentError, TypeNotFoundError

from system.account_actions.checking_spam.account_verification import check_account_for_spam
# from system.account_actions.creating.account_registration import AccountRIO
from system.account_actions.creating.creating import creating_groups_and_chats
from system.account_actions.invitation.inviting_participants_telegram import INVITING_TO_A_GROUP
# from system.account_actions.invitation.inviting_participants_telegram import InvitingToAGroup
from system.account_actions.invitation.telegram_invite_scheduler import launching_an_invite_once_an_hour
from system.account_actions.invitation.telegram_invite_scheduler import launching_invite_every_day_certain_time
from system.account_actions.invitation.telegram_invite_scheduler import schedule_invite
from system.account_actions.parsing.parsing_account_groups_and_channels import parsing_groups_which_account_subscribed
from system.account_actions.parsing.parsing_group_members import delete_contact
from system.account_actions.parsing.parsing_group_members import inviting_contact
from system.account_actions.parsing.parsing_group_members import parsing_gui, parsing_of_active_participants
from system.account_actions.parsing.parsing_group_members import show_account_contact_list
from system.account_actions.parsing.parsing_group_members import we_record_phone_numbers_in_the_db
# from system.account_actions.reactions.reactions import WorkingWithReactions, viewing_posts, setting_reactions
from system.account_actions.sending_messages.chat_dialog_mes import mains
from system.account_actions.sending_messages.sending_messages_telegram import send_files_to_personal_chats
from system.account_actions.sending_messages.sending_messages_telegram import send_message_from_all_accounts
from system.account_actions.sending_messages.telegram_chat_dialog import sending_files_via_chats, \
    sending_messages_files_via_chats
from system.account_actions.sending_messages.telegram_chat_dialog import sending_messages_via_chats_times
from system.account_actions.subscription.subscription import subscription_all
from system.account_actions.unsubscribe.unsubscribe import unsubscribe_all
from system.auxiliary_functions.auxiliary_functions import find_files, record_and_interrupt, record_inviting_results
from system.auxiliary_functions.global_variables import ConfigReader
# from system.setting.setting import connecting_new_account, output_the_input_field_inviting
from system.setting.setting import output_the_input_field_inviting
from system.setting.setting import create_main_window
from system.setting.setting import creating_the_main_window_for_proxy_data_entry
from system.setting.setting import output_the_input_field
from system.setting.setting import reaction_gui
from system.setting.setting import record_device_type
from system.setting.setting import record_setting
from system.setting.setting import record_the_number_of_accounts
from system.setting.setting import recording_link_channel
from system.setting.setting import recording_text_for_sending_messages
from system.setting.setting import recording_the_time_to_launch_an_invite_every_day
from system.setting.setting import writing_api_id_api_hash
from system.setting.setting import writing_members
from system.sqlite_working_tools.sqlite_working_tools import DatabaseHandler

# from system.telegram_actions.account_verification import deleting_files_by_dictionary

logger.add("user_settings/log/log.log", rotation="1 MB", compression="zip")  # Логирование программы
# logger.add(sys.stderr, level="ERROR")

line_width = 580  # Ширина окна и ширина строки
program_version, date_of_program_change = "0.14.8", "04.06.2024"  # Версия программы, дата изменения


def mainss(page: ft.Page):
    page.title = f"TelegramMaster: {program_version} (Дата изменения {date_of_program_change})"
    page.window_width = line_width  # window's ширина is 200 px
    page.window_height = 700  # window's высота is 200 px
    page.window_resizable = False  # window is not resizable

    # width - ширина,  # height - высота
    async def route_change(route):
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
                          ft.ElevatedButton(width=line_width, height=30, text="Редактирование BIO",
                                            on_click=lambda _: page.go("/bio_editing")),
                          ft.ElevatedButton(width=line_width, height=30, text="Настройки",
                                            on_click=lambda _: page.go("/settings")),
                          ], ))

        if page.route == "/inviting":  # Инвайтинг
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

            logger.info(f"Запуск инвайтинга без лимитов")
            inviting_to_a_group = INVITING_TO_A_GROUP()

            """Очистка базы данных"""
            await inviting_to_a_group.cleaning_the_database_from_accounts()

            """Сканирование каталога с аккаунтами"""
            records = await inviting_to_a_group.scanning_the_folder_with_accounts_for_telegram_accounts()
            logger.info(f"{records}")
            for entities in records:
                logger.info(f"{entities[0]}")
                await inviting_to_a_group.write_account_data_to_the_database(entities)

            """Проверка аккаунтов"""
            accounts = await inviting_to_a_group.getting_accounts_from_the_database_for_inviting()
            for account in accounts:
                logger.info(f"{account[0]}")
                proxy = await inviting_to_a_group.reading_proxies_from_the_database()
                await inviting_to_a_group.account_verification_for_inviting(account[0], proxy)

            """Инвайтинг"""
            accounts = await inviting_to_a_group.reading_the_list_of_accounts_from_the_database()
            for account in accounts:
                logger.info(f"{account[0]}")

                """Получение ссылки для инвайтинга"""
                links_inviting = await inviting_to_a_group.getting_an_invitation_link_from_the_database()
                for link in links_inviting:
                    logger.info(f"{link[0]}")
                    proxy = await inviting_to_a_group.reading_proxies_from_the_database()
                    client = await inviting_to_a_group.connecting_to_telegram_for_inviting(account[0], proxy)
                    await client.connect()

                    """Подписка на группу для инвайтинга"""
                    await inviting_to_a_group.subscription_to_group_for_inviting(client, link)

                    """Получение списка usernames"""
                    number_usernames = await inviting_to_a_group.getting_a_list_of_usernames_from_the_database()
                    for username in number_usernames:
                        logger.info(f"Пользователь username:{username[0]}")

                        """Инвайтинг в группу по полученному списку"""
                        config_reader = ConfigReader()
                        time_inviting = config_reader.get_time_inviting()
                        time_inviting_1 = time_inviting[0]
                        time_inviting_2 = time_inviting[1]
                        try:
                            await inviting_to_a_group.inviting_to_a_group_according_to_the_received_list(client, link,
                                                                                                         username)

                        except PeerFloodError:
                            logger.error(f"Попытка приглашения {username} в группу {link[0]}. Настройки "
                                         f"конфиденциальности {username} не позволяют вам inviting")
                            record_and_interrupt(time_inviting_1, time_inviting_2)
                            break  # Прерываем работу и меняем аккаунт
                        except AuthKeyDuplicatedError:
                            record_and_interrupt(time_inviting_1, time_inviting_2)
                            break  # Прерываем работу и меняем аккаунт
                        except FloodWaitError as error:
                            logger.error(f'{error}')
                            record_and_interrupt(time_inviting_1, time_inviting_2)
                            break  # Прерываем работу и меняем аккаунт
                        except UserPrivacyRestrictedError:
                            logger.error(
                                f"Попытка приглашения {username} в группу {link[0]}. Настройки конфиденциальности "
                                f"{username} не позволяют вам inviting")
                            await record_inviting_results(time_inviting_1, time_inviting_2, username)
                        except UserChannelsTooMuchError:
                            logger.error(
                                f"Попытка приглашения {username} в группу {link[0]}. Превышен лимит у user каналов / "
                                f"супергрупп.")
                            await record_inviting_results(time_inviting_1, time_inviting_2, username)
                            continue
                        except UserBannedInChannelError:
                            record_and_interrupt(time_inviting_1, time_inviting_2)
                            break  # Прерываем работу и меняем аккаунт
                        except ChatWriteForbiddenError:
                            logger.error(
                                f"Попытка приглашения {username} в группу {link[0]}. Настройки в чате не дают добавлять "
                                f"людей в чат, возможно стоит бот админ и нужно подписаться на другие проекты")
                            await record_inviting_results(time_inviting_1, time_inviting_2, username)
                            break  # Прерываем работу и меняем аккаунт
                        except BotGroupsBlockedError:
                            logger.error(
                                f"Попытка приглашения {username} в группу {link[0]}. Вы не можете добавить бота в группу.")
                            await record_inviting_results(time_inviting_1, time_inviting_2, username)
                        except UserNotMutualContactError:
                            logger.error(
                                f"Попытка приглашения {username} в группу {link[0]}. User не является взаимным контактом.")
                            await record_inviting_results(time_inviting_1, time_inviting_2, username)
                        except ChatAdminRequiredError:
                            logger.error(
                                f"Попытка приглашения {username} в группу {link[0]}. Требуются права администратора.")
                            await record_inviting_results(time_inviting_1, time_inviting_2, username)
                        except UserKickedError:
                            logger.error(
                                f"Попытка приглашения {username} в группу {link[0]}. Пользователь был удален ранее из "
                                f"супергруппы.")
                            await record_inviting_results(time_inviting_1, time_inviting_2, username)
                        except ChannelPrivateError:
                            record_and_interrupt(time_inviting_1, time_inviting_2)
                            break  # Прерываем работу и меняем аккаунт
                        except (UserIdInvalidError, UsernameNotOccupiedError, ValueError, UsernameInvalidError):
                            await record_inviting_results(time_inviting_1, time_inviting_2, username)
                            logger.error(
                                f"Попытка приглашения {username} в группу {link[0]}. Не корректное имя {username}")
                            break  # Прерываем работу и меняем аккаунт
                        except (TypeError, UnboundLocalError):
                            logger.error(f"Попытка приглашения {username} в группу {link[0]}")
                            continue  # Записываем ошибку в software_database.db и продолжаем работу
                        except InviteRequestSentError:
                            logger.error(f"Попытка приглашения {username} в группу {link[0]}. Доступ к функциям группы "
                                         f"станет возможен после утверждения заявки администратором на {link[0]}")
                            await record_inviting_results(time_inviting_1, time_inviting_2, username)
                            break  # Прерываем работу и меняем аккаунт
                        except TypeNotFoundError:
                            record_and_interrupt(time_inviting_1, time_inviting_2)
                            break  # Прерываем работу и меняем аккаунт
                        except KeyboardInterrupt:  # Закрытие окна программы
                            client.disconnect()  # Разрываем соединение telegram
                            logger.info("[!] Скрипт остановлен!")
                        except Exception as error:
                            logger.error(f'{error}')  # Прерываем работу и меняем аккаунт
                            logger.info(f'Спим 5 секунд')
                            # time.sleep(5)
                        else:
                            logger.info(f"[+] Участник {username} добавлен, если не состоит в чате {link[0]}")
                            await record_inviting_results(time_inviting_1, time_inviting_2, username)

                    await inviting_to_a_group.unsubscribing_from_group_for_inviting(client, link)
            logger.info("[!] Инвайтинг окончен!")

        elif page.route == "/inviting_with_limits":  # Инвайтинг с лимитами
            pass
        elif page.route == "/inviting_1_time_per_hour":  # Инвайтинг 1 раз в час
            launching_an_invite_once_an_hour()
        elif page.route == "/inviting_certain_time":  # Инвайтинг в определенное время
            schedule_invite()
        elif page.route == "/inviting_every_day":  # Инвайтинг каждый день
            launching_invite_every_day_certain_time()

        elif page.route == "/checking_accounts":  # Проверка аккаунтов
            await check_account_for_spam()

        elif page.route == "/subscribe_unsubscribe":  # подписка, отписка
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
            await subscription_all(DatabaseHandler())
        elif page.route == "/unsubscribe_all":  # Отписываемся
            await unsubscribe_all()

        elif page.route == "/working_with_reactions":  # Работа с реакциями
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
        # elif page.route == "/setting_reactions":  # Ставим реакции
        #     reaction_worker = WorkingWithReactions(DatabaseHandler())  # Создаем экземпляр класса WorkingWithReactions
        #     await reaction_worker.users_choice_of_reaction()  # Вызываем метод для выбора реакции и установки её на сообщение
        # elif page.route == "/we_are_winding_up_post_views":  # Накручиваем просмотры постов
        #     viewing_posts(DatabaseHandler())
        # elif page.route == "/automatic_setting_of_reactions":  # Автоматическое выставление реакций
        #     await setting_reactions(DatabaseHandler())  # Автоматическое выставление реакций

        elif page.route == "/subscribe_unsubscribe":  # подписка, отписка
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
            await subscription_all(DatabaseHandler())
        elif page.route == "/unsubscribe_all":  # Отписываемся
            await unsubscribe_all()

        elif page.route == "/working_with_reactions":  # Работа с реакциями
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
        # elif page.route == "/setting_reactions":  # Ставим реакции
        #     reaction_worker = WorkingWithReactions(DatabaseHandler())  # Создаем экземпляр класса WorkingWithReactions
        #     await reaction_worker.users_choice_of_reaction()  # Вызываем метод для выбора реакции и установки её на сообщение
        # elif page.route == "/we_are_winding_up_post_views":  # Накручиваем просмотры постов
        #     viewing_posts(DatabaseHandler())
        # elif page.route == "/automatic_setting_of_reactions":  # Автоматическое выставление реакций
        #     await setting_reactions(DatabaseHandler())  # Автоматическое выставление реакций

        elif page.route == "/parsing":  # Парсинг
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
            parsing_gui(page)
        elif page.route == "/parsing_selected_group_user_subscribed":  # Парсинг выбранной группы из подписанных пользователем
            # await choosing_a_group_from_the_subscribed_ones_for_parsing(page, lv, db_handler)
            pass
        elif page.route == "/parsing_active_group_members":  # Парсинг активных участников группы
            chat_input = input("[+] Введите ссылку на чат с которого будем собирать активных: ")
            limit_active_user = input("[+] Введите количество сообщений которые будем parsing: ")
            await parsing_of_active_participants(chat_input, int(limit_active_user))
        elif page.route == "/parsing_groups_channels_account_subscribed":  # Парсинг групп / каналов на которые подписан аккаунт
            parsing_groups_which_account_subscribed(DatabaseHandler())
        elif page.route == "/clearing_list_previously_saved_data":  # Очистка списка от ранее спарсенных данных
            db_handler = DatabaseHandler()
            await db_handler.cleaning_db(name_database_table="members")

        elif page.route == "/working_with_contacts":  # Работа с контактами
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
            we_record_phone_numbers_in_the_db(DatabaseHandler())
        elif page.route == "/show_list_contacts":  # Показать список контактов
            show_account_contact_list(DatabaseHandler())
        elif page.route == "/deleting_contacts":  # Удаление контактов
            delete_contact(DatabaseHandler())
        elif page.route == "/adding_contacts":  # Добавление контактов
            inviting_contact(DatabaseHandler())

        # elif page.route == "/connecting_accounts":  # Подключение новых аккаунтов, методом ввода нового номера телефона
        #     await connecting_new_account()

        elif page.route == "/creating_groups":  # Создание групп (чатов)
            async def creating_groups():
                db_handler = DatabaseHandler()
                records: list = await db_handler.open_and_read_data("config")
                creating_groups_and_chats(page, records, db_handler)

            await creating_groups()

        elif page.route == "/sending_messages":  # Настройки
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
        elif page.route == "/sending_messages_personal_account":  # ✔️ Отправка сообщений в личку
            await send_message_from_all_accounts(limits=None)
        elif page.route == "/sending_files_personal_account":  # ✔️ Отправка файлов в личку
            await send_files_to_personal_chats(limits=None)
        elif page.route == "/sending_messages_via_chats":  # ✔️ Рассылка сообщений по чатам
            entities = find_files(directory_path="user_settings/message", extension="json")
            logger.info(entities)
            await sending_messages_via_chats_times(entities)
        elif page.route == "/sending_messages_via_chats_with_answering_machine":  # ✔️ Рассылка сообщений по чатам с автоответчиком
            mains(DatabaseHandler())
        elif page.route == "/sending_files_via_chats":  # ✔️ Рассылка файлов по чатам
            await sending_files_via_chats(DatabaseHandler())
        elif page.route == "/sending_messages_files_via_chats":  # ✔️ Рассылка сообщений + файлов по чатам
            await sending_messages_files_via_chats()
        elif page.route == "/sending_personal_messages_with_limits":  # ✔️ Отправка сообщений в личку (с лимитами)
            config_reader = ConfigReader()
            limits_message = config_reader.get_message_limits()
            await send_message_from_all_accounts(limits=limits_message)
        elif page.route == "/sending_files_to_personal_account_with_limits":  # ✔️ Отправка файлов в личку (с лимитами)
            config_reader = ConfigReader()
            limits_message = config_reader.get_message_limits()
            await send_files_to_personal_chats(limits=limits_message)

        elif page.route == "/bio_editing":  # Настройки
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

        # elif page.route == "/edit_description":  # ✔️ Изменение описания
        #     aaa = AccountRIO(DatabaseHandler())  # Передаем db_handler как аргумент
        #     aaa.change_bio_profile_gui(page, DatabaseHandler())
        # elif page.route == "/name_change":  # ✔️ Изменение имени
        #     aaa = AccountRIO(DatabaseHandler())  # Передаем db_handler как аргумент
        #     aaa.change_name_profile_gui(page, DatabaseHandler())
        # elif page.route == "/change_surname":  # ✔️ Изменение фамилии
        #     aaa = AccountRIO(DatabaseHandler())  # Передаем db_handler как аргумент
        #     aaa.change_last_name_profile_gui(page, DatabaseHandler())
        # elif page.route == "/edit_photo":  # ✔️ Изменение фото
        #     aaa = AccountRIO(DatabaseHandler())  # Передаем db_handler как аргумент
        #     await aaa.change_photo_profile(DatabaseHandler())
        # elif page.route == "/changing_username":  # ✔️ Изменение username
        #     aaa = AccountRIO(DatabaseHandler())  # Передаем db_handler как аргумент
        #     aaa.change_username_profile_gui(page, DatabaseHandler())

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
            output_the_input_field_inviting(page, DatabaseHandler())
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
