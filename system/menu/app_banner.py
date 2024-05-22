from rich.console import Console

console = Console()
program_version, date_of_program_change = "0.14.3", "22.05.2024"  # Версия программы, дата изменения


def banner() -> None:
    """Банер программы составлен с помощью https://manytools.org/hacker-tools/ascii-banner/"""
    console.print("╔╦╗┌─┐┬  ┌─┐┌─┐┬─┐┌─┐┌┬┐╔╦╗┌─┐┌─┐┌┬┐┌─┐┬─┐", style="medium_purple3", justify="center")
    console.print(" ║ ├┤ │  ├┤ │ ┬├┬┘├─┤│││║║║├─┤└─┐ │ ├┤ ├┬┘", style="medium_purple3", justify="center")
    console.print(" ╩ └─┘┴─┘└─┘└─┘┴└─┴ ┴┴ ┴╩ ╩┴ ┴└─┘ ┴ └─┘┴└─", style="medium_purple3", justify="center")
    console.print("Telegram: https://t.me/PyAdminRU", style="medium_purple3", justify="center")
    # Для удобства чтения, разделяем полосками https://rich.readthedocs.io/en/stable/console.html
    # Разнообразие консоли с модулем rich (python -m rich) - возможности модуля
    console.print(f"TelegramMaster версия программы: {program_version} "
                  f"(Дата изменения {date_of_program_change})", style="cyan", justify="center")
    # Разнообразие консоли с модулем rich (пишем текст посередине)


if __name__ == "__main__":
    banner()
