# -*- coding: utf-8 -*-


class ToggleController:
    """Обработчики для взаимоисключающего поведения"""

    def __init__(self, admin_switch, account_groups_switch, members_switch, account_group_selection_switch,
                 active_switch):
        self.admin_switch = admin_switch
        self.account_groups_switch = account_groups_switch
        self.members_switch = members_switch
        self.account_group_selection_switch = account_group_selection_switch
        self.active_switch = active_switch

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
