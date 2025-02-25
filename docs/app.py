# -*- coding: utf-8 -*-
import time
import webbrowser
from multiprocessing import Process

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from loguru import logger

# Импорт необходимых переменных и функций
from src.core.configs import program_name, program_version, date_of_program_change
from src.core.localization import (parse_selected_user_subscribed_group, parse_single_or_multiple_groups,
                                   parse_active_group_members, clear_previously_parsed_data_list,
                                   parse_account_subscribed_groups_channels, inviting_ru,
                                   invitation_1_time_per_hour_ru, invitation_at_a_certain_time_ru,
                                   inviting_every_day_ru, importing_a_list_of_parsed_data, setting_reactions,
                                   we_are_winding_up_post_views_ru, automatic_setting_of_reactions,
                                   sending_messages_via_chats_ru,
                                   sending_messages_files_via_chats_ru,
                                   sending_personal_messages_with_limits_ru,
                                   sending_files_to_personal_account_with_limits_ru, choice_of_reactions_ru,
                                   proxy_entry_ru, changing_accounts_ru, recording_api_id_api_hash_ru,
                                   time_between_subscriptions_ru, message_recording_ru, link_entry_ru,
                                   account_limits_ru, message_limits_ru, time_between_subscriptionss_ru,
                                   creating_username_list_ru, recording_the_time_between_messages_ru,
                                   time_between_invites_sending_messages_ru, recording_reaction_link_ru,
                                   forming_list_of_chats_channels_ru, changing_the_username,
                                   changing_the_photo, changing_the_description, name_change_n,
                                   name_change_f, creating_a_contact_list, show_a_list_of_contacts,
                                   deleting_contacts, adding_contacts, working_with_contacts_menu_ru,
                                   subscription, unsubscribe, connecting_accounts_by_phone_number,
                                   connecting_session_accounts, start_inviting_button)

app = FastAPI()

# Указываем путь к статическим файлам
app.mount("/static", StaticFiles(directory="docs/static"), name="static")
templates = Jinja2Templates(directory="docs/templates")  # Указываем директорию с шаблонами.


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Главная страница документации"""
    logger.info("Запущена главная страница документации")
    try:
        return templates.TemplateResponse("index.html", {"request": request, "program_name": program_name})
    except Exception as e:
        logger.exception(f"Error rendering the template: {e}")
        return {"error": "Failed to render template"}


@app.get("/menu", response_class=HTMLResponse)
async def menu(request: Request):
    """Меню программы"""
    logger.info("Запущено меню программы")
    return templates.TemplateResponse("menu.html", {"request": request, "program_version": program_version,
                                                    "update_date": date_of_program_change})


@app.get("/inviting", response_class=HTMLResponse)
async def inviting_page(request: Request):
    """🚀 Инвайтинг"""
    logger.info("Запущена страница инвайтинга")
    return templates.TemplateResponse("inviting.html", {"request": request, "program_name": program_name,
                                                        "inviting_ru": inviting_ru,
                                                        "invitation_1_time_per_hour_ru": invitation_1_time_per_hour_ru,
                                                        "invitation_at_a_certain_time_ru": invitation_at_a_certain_time_ru,
                                                        "inviting_every_day_ru": inviting_every_day_ru})


@app.get("/inviting/inviting_with_limits_in_telegram_master", response_class=HTMLResponse)
async def inviting_with_limits_in_telegram_master(request: Request):
    """🚀 Инвайтинг"""
    logger.info("Запущена страница 🚀 Инвайтинг")
    return templates.TemplateResponse("inviting/inviting_with_limits_in_telegram_master.html",
                                      {
                                          "request": request, "program_name": program_name,
                                          "inviting_ru": inviting_ru,
                                          "invitation_1_time_per_hour_ru": invitation_1_time_per_hour_ru,
                                          "invitation_at_a_certain_time": invitation_at_a_certain_time_ru,
                                          "inviting_every_day_ru": inviting_every_day_ru,
                                          "start_inviting_button": start_inviting_button,
                                      })


@app.get("/inviting/inviting_1_time_per_hour", response_class=HTMLResponse)
async def inviting_1_time_per_hour(request: Request):
    """⏰ Инвайтинг 1 раз в час"""
    logger.info("Запущена страница 🚀 Инвайтинг")
    return templates.TemplateResponse("inviting/inviting_1_time_per_hour.html",
                                      {
                                          "request": request, "program_name": program_name,
                                          "inviting_ru": inviting_ru,
                                          "invitation_1_time_per_hour_ru": invitation_1_time_per_hour_ru,
                                          "start_inviting_button": start_inviting_button,
                                      })


@app.get("/inviting/inviting_at_a_certain_time", response_class=HTMLResponse)
async def inviting_at_a_certain_time(request: Request):
    """🕒 Инвайтинг в определенное время"""
    logger.info("Запущена страница 🚀 Инвайтинг")
    return templates.TemplateResponse("inviting/inviting_at_a_certain_time.html",
                                      {"request": request, "program_name": program_name,
                                       "inviting": inviting_ru,
                                       "invitation_at_a_certain_time_ru": invitation_at_a_certain_time_ru,
                                       "time_between_subscriptions_ru": time_between_subscriptions_ru,
                                       "start_inviting_button": start_inviting_button,
                                       })


@app.get("/inviting/inviting_every_day", response_class=HTMLResponse)
async def inviting_every_day(request: Request):
    """📅 Инвайтинг каждый день"""
    logger.info("Запущена страница 🚀 Инвайтинг")
    return templates.TemplateResponse("inviting/inviting_every_day.html",
                                      {"request": request, "program_name": program_name,
                                       "inviting_ru": inviting_ru,
                                       "inviting_every_day_ru": inviting_every_day_ru,
                                       "time_between_subscriptions_ru": time_between_subscriptions_ru,
                                       "start_inviting_button": start_inviting_button,
                                       })


# Рассылка сообщений по чатам, в личку

@app.get('/sending_messages', response_class=HTMLResponse)
async def sending_messages(request: Request):
    """💬 Рассылка сообщений"""
    logger.info("Запущено страница рассылки сообщений")
    return templates.TemplateResponse('sending_messages.html', {"request": request, "program_name": program_name,
                                                                "sending_messages_via_chats_ru": sending_messages_via_chats_ru,
                                                                "sending_messages_files_via_chats_ru": sending_messages_files_via_chats_ru,
                                                                "sending_personal_messages_with_limits_ru": sending_personal_messages_with_limits_ru,
                                                                "sending_files_to_personal_account_with_limits_ru": sending_files_to_personal_account_with_limits_ru
                                                                })

# Рассылка сообщений в личку

@app.get('/sending_messages/sending_personal_messages_with_limits', response_class=HTMLResponse)
async def sending_personal_messages_with_limits(request: Request):
    """📨 Отправка сообщений в личку"""
    logger.info("Запущена страница 📨 Отправка сообщений в личку")
    return templates.TemplateResponse('sending_messages/sending_personal_messages_with_limits.html',
                                      {"request": request, "program_name": program_name,
                                       "sending_personal_messages_with_limits_ru": sending_personal_messages_with_limits_ru,
                                       })


@app.get('/sending_messages/sending_files_to_personal_account_with_limits', response_class=HTMLResponse)
async def sending_files_to_personal_account_with_limits(request: Request):
    """📁 Отправка файлов в личку"""
    logger.info("Запущена страница 📁 Отправка файлов в личку")
    return templates.TemplateResponse('sending_messages/sending_files_to_personal_account_with_limits.html',
                                      {"request": request, "program_name": program_name,
                                       "sending_files_to_personal_account_with_limits_ru": sending_files_to_personal_account_with_limits_ru,
                                       })

# Рассылка сообщений по чатам


@app.get('/sending_messages/sending_messages_via_chats', response_class=HTMLResponse)
async def sending_messages_via_chats(request: Request):
    """💬 Рассылка сообщений по чатам"""
    logger.info("Запущена страница 💬 Рассылка сообщений по чатам")
    return templates.TemplateResponse('sending_messages/sending_messages_via_chats.html',
                                      {"request": request, "program_name": program_name,
                                       "sending_messages_via_chats_ru": sending_messages_via_chats_ru,
                                       })


@app.get('/editing_bio', response_class=HTMLResponse)
async def editing_bio(request: Request):
    """Редактирование BIO"""
    logger.info("Запущена страница редактирования БИО")
    return templates.TemplateResponse('editing_bio.html', {"request": request, "program_name": program_name,
                                                           "changing_the_username": changing_the_username,
                                                           "changing_the_photo": changing_the_photo,
                                                           "changing_the_description": changing_the_description,
                                                           "name_change_n": name_change_n,
                                                           "name_change_f": name_change_f,
                                                           })


@app.get('/working_with_contacts', response_class=HTMLResponse)
async def working_with_contacts(request: Request):
    """Работа с контактами"""
    logger.info("Запущена страница работы с контактами")
    return templates.TemplateResponse('working_with_contacts.html', {"request": request, "program_name": program_name,
                                                                     "creating_a_contact_list": creating_a_contact_list,
                                                                     "show_a_list_of_contacts": show_a_list_of_contacts,
                                                                     "deleting_contacts": deleting_contacts,
                                                                     "adding_contacts": adding_contacts,
                                                                     "working_with_contacts_menu_ru": working_with_contacts_menu_ru,
                                                                     })


# Настройки
@app.get('/settings', response_class=HTMLResponse)
async def settings(request: Request):
    """⚙️ Настройки"""
    logger.info("Запущена страница настроек")
    return templates.TemplateResponse('settings.html', {"request": request, "program_name": program_name,
                                                        "choice_of_reactions_ru": choice_of_reactions_ru,
                                                        "proxy_entry_ru": proxy_entry_ru,
                                                        "changing_accounts_ru": changing_accounts_ru,
                                                        "recording_api_id_api_hash_ru": recording_api_id_api_hash_ru,
                                                        "time_between_subscriptions_ru": time_between_subscriptions_ru,
                                                        "message_recording_ru": message_recording_ru,
                                                        "link_entry_ru": link_entry_ru,
                                                        "account_limits_ru": account_limits_ru,
                                                        "message_limits_ru": message_limits_ru,
                                                        "time_between_subscriptionss_ru": time_between_subscriptionss_ru,
                                                        "creating_username_list_ru": creating_username_list_ru,
                                                        "recording_the_time_between_messages_ru": recording_the_time_between_messages_ru,
                                                        "time_between_invites_sending_messages_ru": time_between_invites_sending_messages_ru,
                                                        "recording_reaction_link_ru": recording_reaction_link_ru,
                                                        "forming_list_of_chats_channels_ru": forming_list_of_chats_channels_ru,
                                                        })


@app.get('/settings/choice_of_reactions', response_class=HTMLResponse)
async def choice_of_reactions(request: Request):
    """👍 Выбор реакций"""
    logger.info("Запущена страница выбора реакции")
    return templates.TemplateResponse('settings/choice_of_reactions.html', {
        "request": request,
        "program_name": program_name,
        "choice_of_reactions_ru": choice_of_reactions_ru,
    })


@app.get('/settings/proxy_entry', response_class=HTMLResponse)
async def proxy_entry(request: Request):
    """🔐 Запись proxy"""
    logger.info("Запущена страница выбора реакции")
    return templates.TemplateResponse('settings/proxy_entry.html', {
        "request": request,
        "program_name": program_name,
        "proxy_entry_ru": proxy_entry_ru,
    })


@app.get('/settings/changing_accounts', response_class=HTMLResponse)
async def changing_accounts(request: Request):
    """🔄 Смена аккаунтов"""
    logger.info("Запущена страница 🔄 Смена аккаунтов")
    return templates.TemplateResponse('settings/changing_accounts.html', {
        "request": request,
        "program_name": program_name,
        "changing_accounts_ru": changing_accounts_ru,
    })


@app.get('/settings/recording_api_id_api_hash', response_class=HTMLResponse)
async def recording_api_id_api_hash(request: Request):
    """📝 Запись api_id, api_hash"""
    logger.info("Запущена страница записи api_id api_hash")
    return templates.TemplateResponse('settings/recording_api_id_api_hash.html', {
        "request": request,
        "program_name": program_name,
        "recording_api_id_api_hash_ru": recording_api_id_api_hash_ru,
    })


@app.get('/settings/time_between_subscriptions', response_class=HTMLResponse)
async def time_between_subscriptions(request: Request):
    """⏰ Запись времени"""
    logger.info("Запущена страница ⏰ Запись времени")
    return templates.TemplateResponse('settings/time_between_subscriptions.html', {
        "request": request,
        "program_name": program_name,
        "time_between_subscriptions_ru": time_between_subscriptions_ru,

    })


@app.get('/settings/message_recording', response_class=HTMLResponse)
async def message_recording(request: Request):
    """✉️ Запись сообщений"""
    logger.info("Запущена страница ✉️ Запись сообщений")
    return templates.TemplateResponse('settings/message_recording.html', {
        "request": request,
        "program_name": program_name,
        "message_recording_ru": message_recording_ru,
    })


@app.get('/settings/link_entry', response_class=HTMLResponse)
async def link_entry(request: Request):
    """🔗 Запись ссылки для инвайтинга"""
    logger.info("Запущена страница 🔗 Запись ссылки для инвайтинга")
    return templates.TemplateResponse('settings/link_entry.html', {
        "request": request,
        "program_name": program_name,
        "link_entry_ru": link_entry_ru,
    })


@app.get('/settings/account_limits', response_class=HTMLResponse)
async def account_limits(request: Request):
    """📊 Лимиты на аккаунт"""
    logger.info("Запущена страница 📊 Лимиты на аккаунт")
    return templates.TemplateResponse('settings/account_limits.html', {
        "request": request,
        "program_name": program_name,
        "account_limits_ru": account_limits_ru,
    })


@app.get('/settings/message_limits', response_class=HTMLResponse)
async def message_limits(request: Request):
    """📨 Лимиты на сообщения"""
    logger.info("Запущена страница 📨 Лимиты на сообщения")
    return templates.TemplateResponse('settings/message_limits.html', {
        "request": request,
        "program_name": program_name,
        "message_limits_ru": message_limits_ru,
    })


@app.get('/settings/time_between_subscriptionss', response_class=HTMLResponse)
async def time_between_subscriptionss(request: Request):
    """⏳ Время между подпиской"""
    logger.info("Запущена страница ⏳ Время между подпиской")
    return templates.TemplateResponse('settings/time_between_subscriptionss.html', {
        "request": request,
        "program_name": program_name,
        "time_between_subscriptionss_ru": time_between_subscriptionss_ru,
    })


@app.get('/settings/creating_username_list', response_class=HTMLResponse)
async def creating_username_list(request: Request):
    """📋 Формирование списка username"""
    logger.info("Запущена страница 📋 Формирование списка username")
    return templates.TemplateResponse('settings/creating_username_list.html', {
        "request": request,
        "program_name": program_name,
        "creating_username_list_ru": creating_username_list_ru,
    })


@app.get('/settings/recording_the_time_between_messages', response_class=HTMLResponse)
async def recording_the_time_between_messages(request: Request):
    """⏱️ Запись времени между сообщениями"""
    logger.info("Запущена страница ⏱️ Запись времени между сообщениями")
    return templates.TemplateResponse('settings/recording_the_time_between_messages.html', {
        "request": request,
        "program_name": program_name,
        "recording_the_time_between_messages_ru": recording_the_time_between_messages_ru,
    })


@app.get('/settings/time_between_invites_sending_messages', response_class=HTMLResponse)
async def time_between_invites_sending_messages(request: Request):
    """🕒 Время между инвайтингом, рассылка сообщений"""
    logger.info("Запущена страница 🕒 Время между инвайтингом, рассылка сообщений")
    return templates.TemplateResponse('settings/time_between_invites_sending_messages.html', {
        "request": request,
        "program_name": program_name,
        "time_between_invites_sending_messages_ru": time_between_invites_sending_messages_ru,
    })


@app.get('/settings/recording_reaction_link', response_class=HTMLResponse)
async def recording_reaction_link(request: Request):
    """🔗 Запись ссылки для реакций"""
    logger.info("Запущена страница 🔗 Запись ссылки для реакций")
    return templates.TemplateResponse('settings/recording_reaction_link.html', {
        "request": request,
        "program_name": program_name,
        "recording_reaction_link_ru": recording_reaction_link_ru,
    })


@app.get('/settings/forming_list_of_chats_channels', response_class=HTMLResponse)
async def forming_list_of_chats_channels(request: Request):
    """📑 Формирование списка чатов / каналов"""
    logger.info("Запущена страница 📑 Формирование списка чатов / каналов")
    return templates.TemplateResponse('settings/forming_list_of_chats_channels.html', {
        "request": request,
        "program_name": program_name,
        "forming_list_of_chats_channels_ru": forming_list_of_chats_channels_ru,
    })


# Работа с реакциями

@app.get('/working_with_reactions', response_class=HTMLResponse)
async def working_with_reactions(request: Request):
    """👍 Работа с реакциями"""
    logger.info("Запущена страница работы с реакциями")
    return templates.TemplateResponse('working_with_reactions.html',
                                      {"request": request, "program_name": program_name,
                                       "setting_reactions": setting_reactions,
                                       "we_are_winding_up_post_views_ru": we_are_winding_up_post_views_ru,
                                       "automatic_setting_of_reactions": automatic_setting_of_reactions})


@app.get('/we_are_winding_up_post_views', response_class=HTMLResponse)
async def we_are_winding_up_post_views(request: Request):
    """👁️‍🗨️ Накручиваем просмотры постов"""
    logger.info("Запущена страница '👁️‍🗨️ Накручиваем просмотры постов' ")
    return templates.TemplateResponse('we_are_winding_up_post_views.html',
                                      {"request": request, "program_name": program_name,
                                       "setting_reactions": setting_reactions,
                                       "we_are_winding_up_post_views_ru": we_are_winding_up_post_views_ru,
                                       "automatic_setting_of_reactions": automatic_setting_of_reactions,
                                       "forming_list_of_chats_channels_ru": forming_list_of_chats_channels_ru,
                                       })


@app.get('/parsing', response_class=HTMLResponse)
async def parsing(request: Request):
    """🔍 Парсинг"""
    logger.info("Запущена страница парсинга")
    return templates.TemplateResponse('parsing.html', {"request": request, "program_name": program_name,
                                                       "parse_single_or_multiple_groups": parse_single_or_multiple_groups,
                                                       "parse_selected_user_subscribed_group": parse_selected_user_subscribed_group,
                                                       "parse_active_group_members": parse_active_group_members,
                                                       "parse_account_subscribed_groups_channels": parse_account_subscribed_groups_channels,
                                                       "clear_previously_parsed_data_list": clear_previously_parsed_data_list,
                                                       "importing_a_list_of_parsed_data": importing_a_list_of_parsed_data})


@app.get('/subscribe_unsubscribe', response_class=HTMLResponse)
async def subscribe_unsubscribe(request: Request):
    """Подписка, отписка"""
    logger.info("Запущена страница подписки, отписки")
    return templates.TemplateResponse('subscribe_unsubscribe.html',
                                      {"request": request, "program_name": program_name, "subscription": subscription,
                                       "unsubscribe": unsubscribe})


@app.get('/connect_accounts', response_class=HTMLResponse)
async def connect_accounts(request: Request):
    """Подключение аккаунтов"""
    logger.info("Запущена страница подключения аккаунтов")
    return templates.TemplateResponse('connect_accounts.html',
                                      {"request": request, "program_name": program_name,
                                       "connecting_accounts_by_phone_number": connecting_accounts_by_phone_number,
                                       "connecting_session_accounts": connecting_session_accounts})


@app.get('/account_verification', response_class=HTMLResponse)
async def account_verification(request: Request):
    """Проверка аккаунтов"""
    logger.info("Запущена страница проверки аккаунтов")
    return templates.TemplateResponse('account_verification.html',
                                      {"request": request, "program_name": program_name})


@app.get('/creating_groups', response_class=HTMLResponse)
async def creating_groups(request: Request):
    """Создание групп (чатов)"""
    logger.info("Запущена страница создания групп (чатов)")
    return templates.TemplateResponse('creating_groups.html',
                                      {"request": request, "program_name": program_name})


@app.get('/launch_telegrammaster', response_class=HTMLResponse)
async def launch_telegrammaster(request: Request):
    """Запуск TelegramMaster"""
    logger.info("Запущена страница документации, о запуске TelegramMaster 2.0")
    return templates.TemplateResponse('launch_telegrammaster.html',
                                      {"request": request, "program_name": program_name})


@app.get('/working_with_errors_telegrammaster', response_class=HTMLResponse)
async def working_with_errors_telegrammaster(request: Request):
    """Работа с ошибками TelegramMaster 2.0"""
    logger.info("Запущена страница документации, о работе с ошибками TelegramMaster 2.0")
    return templates.TemplateResponse('working_with_errors_telegrammaster.html',
                                      {"request": request, "program_name": program_name})


@app.get('/install_python_update_pip', response_class=HTMLResponse)
async def install_python_update_pip(request: Request):
    """Установка Python, обновление PIP"""
    logger.info("Запущена страница документации, о установке Python, обновлении PIP")
    return templates.TemplateResponse('install_python_update_pip.html',
                                      {"request": request, "program_name": program_name})


@app.get('/preliminary_setting_of_program_installation_of_program_by_default', response_class=HTMLResponse)
async def preliminary_setting_of_program_installation_of_program_by_default(request: Request):
    """Предварительная настройка программы"""
    logger.info(
        "Запущена страница документации, о предварительной настройке программы, установке программы по умолчанию")
    return templates.TemplateResponse(
        'preliminary_setting_of_program_installation_of_program_by_default.html',
        {"request": request, "program_name": program_name})


@app.get('/registration_api_id_api_hash', response_class=HTMLResponse)
async def registration_api_id_api_hash(request: Request):
    """Получение api и hash"""
    logger.info('Запущена страница, о получении api и hash')
    return templates.TemplateResponse('registration_api_id_api_hash.html',
                                      {"request": request, "program_name": program_name})


@app.get('/telegram_limits', response_class=HTMLResponse)
async def telegram_limits(request: Request):
    """Лимиты Telegram"""
    logger.info("Запущена страница документации, о лимитах Telegram")
    return templates.TemplateResponse('telegram_limits.html',
                                      {"request": request, "program_name": program_name})


def run_uvicorn():
    """Запуск Uvicorn в отдельном процессе."""
    logger.info("Запуск сервера FastAPI...")
    uvicorn.run("docs.app:app", host="127.0.0.1", port=8000, reload=True)


def start_app():
    try:
        server_process = Process(target=run_uvicorn)
        server_process.start()
        time.sleep(10)
        # Открытие браузера после задержки, чтобы сервер успел запуститься.

        webbrowser.open("http://127.0.0.1:8000")

        server_process.join()  # Ждем завершения процесса
    except Exception as error:
        logger.error(f"Ошибка при отслеживании изменений: {error}")
