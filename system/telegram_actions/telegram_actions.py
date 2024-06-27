# -*- coding: utf-8 -*-
import os
import os.path

from system.auxiliary_functions.global_variables import ConfigReader

configs_reader = ConfigReader()
api_id_data, api_hash_data = configs_reader.get_api_id_data_api_hash_data()


def working_with_accounts(account_folder, new_account_folder) -> None:
    """Работа с аккаунтами"""
    try:  # Переносим файлы в нужную папку
        os.replace(account_folder, new_account_folder)
    except FileNotFoundError:  # Если в папке нет нужной папки, то создаем ее
        os.makedirs(new_account_folder)
        os.replace(account_folder, new_account_folder)
