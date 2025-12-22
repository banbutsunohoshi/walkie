from dataclasses import dataclass
from typing import Callable

from domain.models import UserParams
from cli.views import display_message

WALK_TYPES = {
    "1": "solo",
    "2": "pair",
    "3": "friends",
    "4": "dog",
}


@dataclass
class WalkPrompter:
    input_func: Callable[[str], str] = input
    display_func: Callable[[str], None] = display_message

    def prompt_walk_type(self) -> str:
        self.display_func("Выберите тип прогулки:")
        self.display_func("1 — Прогулка в одиночку")
        self.display_func("2 — Прогулка для пары")
        self.display_func("3 — Прогулка с друзьями")
        self.display_func("4 — Прогулка с собакой")
        while True:
            choice = self.input_func("Введите номер: ").strip()
            if choice in WALK_TYPES:
                return WALK_TYPES[choice]
            self.display_func("Некорректный выбор. Попробуйте снова.")

    def prompt_text(self, prompt: str) -> str:
        while True:
            value = self.input_func(prompt).strip()
            if value:
                return value
            self.display_func("Введите непустое значение.")

    def prompt_time(self) -> int:
        while True:
            value = self.input_func("Сколько минут вы готовы гулять? ").strip()
            if value.isdigit() and int(value) > 0:
                return int(value)
            self.display_func("Введите положительное число минут.")

    def collect_walk_params(self) -> UserParams:
        walk_type = self.prompt_walk_type()
        mood = self.prompt_text("Ваше настроение (например, спокойное/игривое/романтичное): ")
        goal = self.prompt_text(
            "Цель прогулки (например, расслабиться/повеселиться/исследовать город): "
        )
        time_limit = self.prompt_time()
        return UserParams(
            walk_type=walk_type,
            mood=mood,
            goal=goal,
            time_limit=time_limit,
        )

    def confirm_walk_params(self, params: UserParams) -> str:
        self.display_func("\nПроверьте выбранные параметры:")
        self.display_func(
            f"Тип прогулки: {params.walk_type}, настроение: {params.mood}, цель: {params.goal}, "
            f"время: {params.time_limit} мин"
        )
        self.display_func("1 — Подтвердить и сгенерировать прогулку")
        self.display_func("2 — Изменить настройки")
        while True:
            choice = self.input_func("Выберите пункт: ").strip()
            if choice in {"1", "2"}:
                return choice
            self.display_func("Некорректный выбор. Попробуйте снова.")


def _prompt_walk_type() -> str:
    return WalkPrompter().prompt_walk_type()


def _prompt_text(prompt: str) -> str:
    return WalkPrompter().prompt_text(prompt)


def _prompt_time() -> int:
    return WalkPrompter().prompt_time()


def collect_walk_params() -> UserParams:
    return WalkPrompter().collect_walk_params()
    

def confirm_walk_params(params: UserParams) -> str:
    return WalkPrompter().confirm_walk_params(params)
