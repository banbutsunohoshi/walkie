from cli.views import display_message


def show_main_menu() -> str:
    display_message("\nГлавное меню")
    display_message("1 — Новая прогулка")
    display_message("2 — История прогулок")
    display_message("3 — Выход")
    return input("Выберите пункт: ").strip()
