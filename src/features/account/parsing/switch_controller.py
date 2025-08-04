# -*- coding: utf-8 -*-


class ToggleController:
    """Обработчики для взаимоисключающего поведения"""

    def __init__(self, admin_switch=None, account_groups_switch=None, members_switch=None,
                 account_group_selection_switch=None, active_switch=None, inviting_switch=None,
                 inviting_1_time_per_hour_switch=None, inviting_at_a_certain_time_switch=None,
                 inviting_every_day_switch=None):

        # Парсинг
        self.admin_switch = admin_switch
        self.account_groups_switch = account_groups_switch
        self.members_switch = members_switch
        self.account_group_selection_switch = account_group_selection_switch
        self.active_switch = active_switch
        # Инвайтинг
        self.inviting_switch = inviting_switch
        self.inviting_1_time_per_hour_switch = inviting_1_time_per_hour_switch
        self.inviting_at_a_certain_time_switch = inviting_at_a_certain_time_switch
        self.inviting_every_day_switch = inviting_every_day_switch

    def toggle_inviting_switch(self, page):
        """Обработчик переключателя инвайтинга"""
        if self.inviting_switch.value:
            self.inviting_1_time_per_hour_switch.value = False
            self.inviting_at_a_certain_time_switch.value = False
            self.inviting_every_day_switch.value = False
        page.update()

    def toggle_inviting_1_time_per_hour_switch(self, page):
        """Обработчик переключателя инвайтинга 1 раз в час"""
        if self.inviting_1_time_per_hour_switch.value:
            self.inviting_switch.value = False
            self.inviting_at_a_certain_time_switch.value = False
            self.inviting_every_day_switch.value = False
        page.update()

    def toggle_inviting_at_a_certain_time_switch(self, page):
        """Обработчик переключателя инвайтинга в определенное время"""
        if self.inviting_at_a_certain_time_switch.value:
            self.inviting_switch.value = False
            self.inviting_1_time_per_hour_switch.value = False
            self.inviting_every_day_switch.value = False
        page.update()

    def toggle_inviting_every_day_switch(self, page):
        """Обработчик переключателя инвайтинга каждый день"""
        if self.inviting_every_day_switch.value:
            self.inviting_switch.value = False
            self.inviting_1_time_per_hour_switch.value = False
            self.inviting_at_a_certain_time_switch = False
        page.update()

    def element_handler_inviting(self, page):
        self.inviting_switch.on_change = lambda e: self.toggle_inviting_switch(page)
        self.inviting_1_time_per_hour_switch.on_change = lambda e: self.toggle_inviting_1_time_per_hour_switch(page)
        self.inviting_at_a_certain_time_switch.on_change = lambda e: self.toggle_inviting_at_a_certain_time_switch(page)
        self.inviting_every_day_switch.on_change = lambda e: self.toggle_inviting_every_day_switch(page)

    def toggle_admin_switch(self, page):
        """Обработчик переключателя администраторов"""
        if self.admin_switch.value:
            self.account_groups_switch.value = False
            self.members_switch.value = False
            self.account_group_selection_switch.value = False
            self.active_switch.value = False
        page.update()

    def toggle_account_groups_switch(self, page):
        """Обработчик переключателя групп аккаунта"""
        if self.account_groups_switch.value:
            self.admin_switch.value = False
            self.members_switch.value = False
            self.account_group_selection_switch.value = False
            self.active_switch.value = False
        page.update()

    def toggle_members_switch(self, page):
        """Обработчик переключателя участников"""
        if self.members_switch.value:
            self.admin_switch.value = False
            self.account_groups_switch.value = False
            self.account_group_selection_switch.value = False
            self.active_switch.value = False
        page.update()

    def toggle_account_group_selection_switch(self, page):
        """Обработчик переключателя группы аккаунта"""
        if self.account_group_selection_switch.value:
            self.admin_switch.value = False
            self.account_groups_switch.value = False
            self.members_switch.value = False
            self.active_switch.value = False
        page.update()

    def toggle_active_switch(self, page):
        """Обработчик парсинга активных пользователей"""
        if self.active_switch.value:
            self.admin_switch.value = False
            self.account_groups_switch.value = False
            self.members_switch.value = False
            self.account_groups_switch.value = False
        page.update()

    def element_handler(self, page):
        """Присоединяем обработчики к элементам интерфейса"""
        # Привязываем обработчики, используя lambda для передачи параметра event
        self.admin_switch.on_change = lambda e: self.toggle_admin_switch(page)
        self.account_groups_switch.on_change = lambda e: self.toggle_account_groups_switch(page)
        self.members_switch.on_change = lambda e: self.toggle_members_switch(page)
        self.account_group_selection_switch.on_change = lambda e: self.toggle_account_group_selection_switch(page)
        self.active_switch.on_change = lambda e: self.toggle_active_switch(page)
