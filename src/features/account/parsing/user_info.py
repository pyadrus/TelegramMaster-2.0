# -*- coding: utf-8 -*-

from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import (User, UserProfilePhoto, UserStatusEmpty, UserStatusLastMonth, UserStatusLastWeek,
                               UserStatusOffline, UserStatusOnline, UserStatusRecently)


class UserInfo:

    @staticmethod
    async def get_bio_user(full_user):
        return full_user.full_user.about or ""

    async def get_full_user_info(self, user: User, client):
        full_user = await client(GetFullUserRequest(id=await self.get_user_id(user)))
        return full_user

    async def get_user_id(self, user: User) -> int:
        return user.id

    @staticmethod
    async def get_access_hash(user: User) -> int:
        return user.access_hash

    @staticmethod
    async def get_last_name(user: User) -> str:
        return user.last_name or ""

    @staticmethod
    async def get_first_name(user: User) -> str:
        return user.first_name or ""

    @staticmethod
    async def get_username(user: User) -> str:
        return user.username or ""

    @staticmethod
    async def get_user_phone(user: User) -> str:
        return user.phone if getattr(user, "phone", None) else "Номер телефона скрыт"

    @staticmethod
    async def get_user_premium_status(user: User) -> str:
        return "Пользователь с premium" if getattr(user, "premium", False) else "Обычный пользователь"

    @staticmethod
    async def get_photo_status(user: User) -> str:
        return "С фото" if isinstance(user.photo, UserProfilePhoto) else "Без фото"

    @staticmethod
    async def get_user_online_status(user):
        """
        Определяет статус онлайна пользователя на основе его статуса.
        https://core.telegram.org/type/UserStatus
        :param user: Объект пользователя из Telethon
        :return: Строка или datetime, описывающая статус онлайна
        """
        online_at = "Был(а) недавно"  # Значение по умолчанию
        if user.status:
            if isinstance(user.status, UserStatusOffline):
                online_at = user.status.was_online
            elif isinstance(user.status, UserStatusRecently):
                online_at = "Был(а) недавно"
            elif isinstance(user.status, UserStatusLastWeek):
                online_at = "Был(а) на этой неделе"
            elif isinstance(user.status, UserStatusLastMonth):
                online_at = "Был(а) в этом месяце"
            elif isinstance(user.status, UserStatusOnline):
                online_at = user.status.expires
            elif isinstance(user.status, UserStatusEmpty):
                online_at = "Статус пользователя не определен"
        return online_at
