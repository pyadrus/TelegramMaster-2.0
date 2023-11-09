from rich.console import Console

console = Console()
program_version, date_of_program_change = "0.9.9", "09.11.2023"  # Версия программы, дата изменения


def banner() -> None:
    """Банер программы составлен с помощью https://manytools.org/hacker-tools/ascii-banner/"""
    console.print("╔╦╗╔═╗╦  ╔═╗╔═╗╦═╗╔═╗╔╦╗    ╔═╗╔╦╗╔╦╗    ╔╗ ╔═╗╔╦╗", style="bold red", justify="center")
    console.print("║ ║╣ ║  ║╣ ║ ╦╠╦╝╠═╣║║║    ╚═╗║║║║║║    ╠╩╗║ ║ ║", style="bold red", justify="center")
    console.print(" ╩ ╚═╝╩═╝╚═╝╚═╝╩╚═╩ ╩╩ ╩────╚═╝╩ ╩╩ ╩────╚═╝╚═╝ ╩ ", style="bold red", justify="center")
    console.print("Telegram: https://t.me/PyAdminRUS", style="bold red", justify="center")
    # Для удобства чтения, разделяем полосками https://rich.readthedocs.io/en/stable/console.html
    # Разнообразие консоли с модулем rich (python -m rich) - возможности модуля
    console.rule(f"[bold red]TELEGRAM_SMM_BOT версия программы: {program_version} "
                 f"(Дата изменения {date_of_program_change})")
    # Разнообразие консоли с модулем rich (пишем текст посередине)


if __name__ == "__main__":
    banner()
