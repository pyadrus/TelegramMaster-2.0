# -*- coding: utf-8 -*-
import flet as ft


async def show_notification(page: ft.Page, message: str):
    """
    Показывает пользователю всплывающее уведомление на странице Flet. Например об отсутствии аккаунтов, username или
    определенных настроек.

    :param page: Страница интерфейса Flet для отображения элементов управления.
    :param message: Текст уведомления.
    """
    # Переход обратно после закрытия диалога
    dlg = ft.AlertDialog(title=ft.Text(message))
    page.overlay.append(dlg)
    dlg.open = True
    page.update()
