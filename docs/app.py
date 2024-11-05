import asyncio
import webbrowser
from hypercorn.asyncio import serve
from hypercorn.config import Config
from loguru import logger
from quart import Quart, render_template
from watchfiles import awatch

from system.auxiliary_functions.config import program_name, program_version, date_of_program_change
from system.localization.localization import (parse_selected_user_subscribed_group, parse_single_or_multiple_groups,
                                              parse_active_group_members, clear_previously_parsed_data_list,
                                              parse_account_subscribed_groups_channels, inviting,
                                              invitation_1_time_per_hour, invitation_at_a_certain_time,
                                              inviting_every_day, importing_a_list_of_parsed_data, setting_reactions,
                                              we_are_winding_up_post_views, automatic_setting_of_reactions,
                                              sending_messages_via_chats,
                                              sending_messages_via_chats_with_answering_machine,
                                              sending_files_via_chats, sending_messages_files_via_chats,
                                              sending_personal_messages_with_limits,
                                              sending_files_to_personal_account_with_limits, choice_of_reactions,
                                              proxy_entry, changing_accounts, recording_api_id_api_hash,
                                              time_between_subscriptions, message_recording, link_entry, account_limits,
                                              message_limits, time_between_subscriptionss, creating_username_list,
                                              recording_the_time_between_messages,
                                              time_between_invites_sending_messages, recording_reaction_link,
                                              forming_list_of_chats_channels)

app = Quart(__name__, template_folder='templates')


@app.route('/')
async def index():
    """Главная страница документации"""
    logger.info("Запущена главная страница документации")
    return await render_template('index.html', program_name=program_name)  # Маршрут для главной страницы


@app.route('/menu')
async def menu():
    """Меню программы"""
    logger.info("Запущено меню программы")
    return await render_template('menu.html', program_version=program_version, update_date=date_of_program_change)


@app.route('/inviting')
async def inviting_page():
    """🚀 Инвайтинг"""
    logger.info("Запущена страница инвайтинга")
    return await render_template('inviting.html', program_name=program_name, inviting=inviting,
                                 invitation_1_time_per_hour=invitation_1_time_per_hour,
                                 invitation_at_a_certain_time=invitation_at_a_certain_time,
                                 inviting_every_day=inviting_every_day)


@app.route('/sending_messages')
async def sending_messages():
    """💬 Рассылка сообщений"""
    logger.info("Запущено страница рассылки сообщений")
    return await render_template('sending_messages.html', program_name=program_name,
                                 sending_messages_via_chats=sending_messages_via_chats,
                                 sending_messages_via_chats_with_answering_machine=sending_messages_via_chats_with_answering_machine,
                                 sending_files_via_chats=sending_files_via_chats,
                                 sending_messages_files_via_chats=sending_messages_files_via_chats,
                                 sending_personal_messages_with_limits=sending_personal_messages_with_limits,
                                 sending_files_to_personal_account_with_limits=sending_files_to_personal_account_with_limits)


@app.route('/editing_bio')
async def editing_bio():
    """Редактирование БИЛ"""
    logger.info("Запущена страница редактирования БИО")
    return await render_template('editing_bio.html', program_name=program_name)


@app.route('/working_with_contacts')
async def working_with_contacts():
    """Работа с контактами"""
    logger.info("Запущена страница работы с контактами")
    return await render_template('working_with_contacts.html', program_name=program_name)


@app.route('/settings')
async def settings():
    """⚙️ Настройки"""
    logger.info("Запущена страница настроек")
    return await render_template('settings.html', program_name=program_name,
                                 choice_of_reactions=choice_of_reactions,
                                 proxy_entry=proxy_entry,
                                 changing_accounts=changing_accounts,
                                 recording_api_id_api_hash=recording_api_id_api_hash,
                                 time_between_subscriptions=time_between_subscriptions,
                                 message_recording=message_recording,
                                 link_entry=link_entry,
                                 account_limits=account_limits,
                                 message_limits=message_limits,
                                 time_between_subscriptionss=time_between_subscriptionss,
                                 creating_username_list=creating_username_list,
                                 recording_the_time_between_messages=recording_the_time_between_messages,
                                 time_between_invites_sending_messages=time_between_invites_sending_messages,
                                 recording_reaction_link=recording_reaction_link,
                                 forming_list_of_chats_channels=forming_list_of_chats_channels,
                                 )


@app.route('/working_with_reactions')
async def working_with_reactions():
    """👍 Работа с реакциями"""
    logger.info("Запущена страница работы с реакциями")
    return await render_template('working_with_reactions.html', program_name=program_name,
                                 setting_reactions=setting_reactions,
                                 we_are_winding_up_post_views=we_are_winding_up_post_views,
                                 automatic_setting_of_reactions=automatic_setting_of_reactions)


@app.route('/parsing')
async def parsing():
    """🔍 Парсинг"""
    logger.info("Запущена страница парсинга")
    return await render_template('parsing.html', program_name=program_name,
                                 parse_single_or_multiple_groups=parse_single_or_multiple_groups,
                                 parse_selected_user_subscribed_group=parse_selected_user_subscribed_group,
                                 parse_active_group_members=parse_active_group_members,
                                 parse_account_subscribed_groups_channels=parse_account_subscribed_groups_channels,
                                 clear_previously_parsed_data_list=clear_previously_parsed_data_list,
                                 importing_a_list_of_parsed_data=importing_a_list_of_parsed_data)


@app.route('/subscribe_unsubscribe')
async def subscribe_unsubscribe():
    """Подписка, отписка"""
    logger.info("Запущена страница подписки, отписки")
    return await render_template('subscribe_unsubscribe.html', program_name=program_name)


@app.route('/connect_accounts')
async def connect_accounts():
    """Подключение аккаунтов"""
    logger.info("Запущена страница подключения аккаунтов")
    return await render_template('connect_accounts.html', program_name=program_name)


@app.route('/account_verification')
async def account_verification():
    """Проверка аккаунтов"""
    logger.info("Запущена страница проверки аккаунтов")
    return await render_template('account_verification.html', program_name=program_name)


@app.route('/creating_groups')
async def creating_groups():
    """Создание групп (чатов)"""
    logger.info("Запущена страница создания групп (чатов)")
    return await render_template('creating_groups.html', program_name=program_name)


@app.route('/launch_telegrammaster')
async def launch_telegrammaster():
    """Запуск TelegramMaster"""
    logger.info("Запущена страница документации, о запуске TelegramMaster 2.0")
    return await render_template('launch_telegrammaster.html', program_name=program_name)


@app.route('/working_with_errors_telegrammaster')
async def working_with_errors_telegrammaster():
    """Работа с ошибками TelegramMaster 2.0"""
    logger.info("Запущена страница документации, о работе с ошибками TelegramMaster 2.0")
    return await render_template('working_with_errors_telegrammaster.html', program_name=program_name)


@app.route('/install_python_update_pip')
async def install_python_update_pip():
    """Установка Python, обновление PIP"""
    logger.info("Запущена страница документации, о установке Python, обновлении PIP")
    return await render_template('install_python_update_pip.html', program_name=program_name)


@app.route('/preliminary_setting_of_program_installation_of_program_by_default')
async def preliminary_setting_of_program_installation_of_program_by_default():
    """Предварительная настройка программы"""
    logger.info("Запущена страница документации, о предварительной настройке программы, установке программы по умолчанию")
    return await render_template('preliminary_setting_of_program_installation_of_program_by_default.html',
                                 program_name=program_name)


@app.route('/registration_api_id_api_hash')
async def registration_api_id_api_hash():
    """Получение api и hash"""
    logger.info('Запущена страница, о получении api и hash')
    return await render_template('registration_api_id_api_hash.html', program_name=program_name)


@app.route('/telegram_limits')
async def telegram_limits():
    """Лимиты Telegram"""
    logger.info("Запущена страница документации, о лимитах Telegram")
    return await render_template('telegram_limits.html', program_name=program_name)


async def run_quart():
    try:
        config = Config()
        config.bind = ["127.0.0.1:8000"]
        logger.info("Запуск сервера Quart...")

        # Открытие браузера после запуска сервера
        webbrowser.open_new("http://127.0.0.1:8000")

        await serve(app, config)
    except Exception as error:
        logger.error(f"Ошибка при запуске сервера: {error}")


async def watch_for_changes():
    async for changes in awatch('./templates'):
        logger.info(f"Изменения обнаружены: {changes}")
        # Здесь можно перезапустить сервер или просто логировать изменения
        # В данном примере просто остановка программы для перезапуска вручную
        # Если хотите автоматический перезапуск сервера, можно использовать systemd или что-то подобное


async def main():
    # Запускаем сервер и отслеживание изменений параллельно
    server_task = asyncio.create_task(run_quart())
    watch_task = asyncio.create_task(watch_for_changes())
    await asyncio.gather(server_task, watch_task)


if __name__ == "__main__":
    asyncio.run(main())
