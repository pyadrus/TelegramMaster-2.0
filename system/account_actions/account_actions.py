from loguru import logger

from system.account_actions.invitation.inviting_participants_telegram import InvitingToAGroup
from system.account_actions.subscription.subscription import subscribe_to_group_or_channel


async def subscribe_telegram() -> None:
    """Подписка на группы / каналы Telegram"""
    logger.info(f"Запуск подписки на группы / каналы Telegram")
    inviting_to_a_group = InvitingToAGroup()
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
            await subscribe_to_group_or_channel(client, link[0])
    logger.info(f"Окончание подписки на группы / каналы Telegram")


if __name__ == "__main__":
    subscribe_telegram()
