from notifypy import Notify
from notifypy.exceptions import UnsupportedPlatform
from rich import print

# Библиотека для работы с уведомлениями на разных платформах https://github.com/ms7m/notify-py


def app_notifications(notification_text) -> None:
    """Выводим уведомление, если операционная система windows 7, то выводим уведомление в консоль"""
    try:
        notification = Notify()
        notification.title = "Telegram_BOT_SMM"
        notification.icon = "system/ico/custom.ico"
        notification.application_name = "Telegram_BOT_SMM"
        notification.message = f"{notification_text}"
        notification.send()
    except UnsupportedPlatform:
        # Выводим уведомление, если операционная система windows 7, то выводим уведомление в консоль
        print(f"[red] {notification_text}")
