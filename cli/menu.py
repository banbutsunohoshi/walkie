from dataclasses import dataclass
from typing import Callable

from cli.views import display_message


@dataclass
class MainMenu:
    input_func: Callable[[str], str] = input
    display_func: Callable[[str], None] = display_message

    def show(self) -> str:
        self.display_func("\nГлавное меню")
        self.display_func("1 — Новая прогулка")
        self.display_func("2 — История прогулок")
        self.display_func("3 — Выход")
        return self.input_func("Выберите пункт: ").strip()


def show_main_menu() -> str:
    dreturn MainMenu().show()
