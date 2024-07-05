# -*- coding: utf-8 -*-
from telethon.errors import YouBlockedUserError
from telethon.sync import TelegramClient  # Не удалять, так как используется кодом

from system.account_actions.TGConnect import TGConnect
from system.auxiliary_functions.auxiliary_functions import find_files

from system.telegram_actions.telegram_actions import working_with_accounts
from thefuzz import fuzz

from loguru import logger


class AccountVerificationSPAM:

    def __init__(self):
        self.tg_connect = TGConnect()

    async def check_account_for_spam(self) -> None:
        """Проверка аккаунта на спам через @SpamBot"""
        # Открываем базу данных для работы с аккаунтами user_settings/software_database.db
        entities = find_files(directory_path="user_settings/accounts", extension='session')
        for file in entities:
            client = await self.tg_connect.connect_to_telegram(file, directory_path="user_settings/accounts")
            try:
                await client.send_message('SpamBot', '/start')  # Находим спам бот, и вводим команду /start
                message_bot = await client.get_messages('SpamBot')
                for message in message_bot:
                    logger.info(f"{file} {message.message}")

                    similarity_ratio_ru: int = fuzz.ratio(f"{message.message}",
                                                          "Очень жаль, что Вы с этим столкнулись. К сожалению, "
                                                          "иногда наша антиспам-система излишне сурово реагирует на "
                                                          "некоторые действия. Если Вы считаете, что Ваш аккаунт "
                                                          "ограничен по ошибке, пожалуйста, сообщите об этом нашим "
                                                          "модераторам. Пока действуют ограничения, Вы не сможете "
                                                          "писать тем, кто не сохранил Ваш номер в список контактов, "
                                                          "а также приглашать таких пользователей в группы или каналы. "
                                                          "Если пользователь написал Вам первым, Вы сможете ответить, "
                                                          "несмотря на ограничения.")
                    logger.exception(similarity_ratio_ru)
                    if similarity_ratio_ru >= 97:
                        logger.info('Аккаунт в бане')
                        await client.disconnect()  # Отключаемся от аккаунта, что бы session файл не был занят другим процессом
                        logger.error(f"""Проверка аккаунтов через SpamBot. {file[0]}: {message.message}""")
                        # Перенос Telegram аккаунта в папку banned, если Telegram аккаунт в бане
                        working_with_accounts(account_folder=f"user_settings/accounts/{file[0]}.session",
                                              new_account_folder=f"user_settings/accounts/banned/{file[0]}.session")
                    similarity_ratio_en: int = fuzz.ratio(f"{message.message}",
                                                          "I’m very sorry that you had to contact me. Unfortunately, "
                                                          "some account_actions can trigger a harsh response from our "
                                                          "anti-spam systems. If you think your account was limited by "
                                                          "mistake, you can submit a complaint to our moderators. While "
                                                          "the account is limited, you will not be able to send messages "
                                                          "to people who do not have your number in their phone contacts "
                                                          "or add them to groups and channels. Of course, when people "
                                                          "contact you first, you can always reply to them.")
                    logger.exception(similarity_ratio_en)
                    if similarity_ratio_en >= 97:
                        logger.info('Аккаунт в бане')
                        await client.disconnect()  # Отключаемся от аккаунта, что бы session файл не был занят другим процессом
                        logger.error(f"""Проверка аккаунтов через SpamBot. {file[0]}: {message.message}""")
                        # Перенос Telegram аккаунта в папку banned, если Telegram аккаунт в бане
                        logger.info(file[0])
                        working_with_accounts(account_folder=f"user_settings/accounts/{file[0]}.session",
                                              new_account_folder=f"user_settings/accounts/banned/{file[0]}.session")
                    logger.error(f"""Проверка аккаунтов через SpamBot. {file[0]}: {message.message}""")

            except YouBlockedUserError:
                continue  # Записываем ошибку в software_database.db и продолжаем работу
