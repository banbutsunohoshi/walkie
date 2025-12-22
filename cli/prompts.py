from domain.models import UserParams
from cli.views import display_message

WALK_TYPES = {
    "1": "solo",
    "2": "pair",
    "3": "friends",
    "4": "dog",
}


def _prompt_walk_type() -> str:
    display_message("Выберите тип прогулки:")
    display_message("1 — Прогулка в одиночку")
    display_message("2 — Прогулка для пары")
    display_message("3 — Прогулка с друзьями")
    display_message("4 — Прогулка с собакой")
    while True:
        choice = input("Введите номер: ").strip()
        if choice in WALK_TYPES:
            return WALK_TYPES[choice]
        display_message("Некорректный выбор. Попробуйте снова.")


def _prompt_text(prompt: str) -> str:
    while True:
        value = input(prompt).strip()
        if value:
            return value
        display_message("Введите непустое значение.")


def _prompt_time() -> int:
    while True:
        value = input("Сколько минут вы готовы гулять? ").strip()
        if value.isdigit() and int(value) > 0:
            return int(value)
        display_message("Введите положительное число минут.")


def collect_walk_params() -> UserParams:
    walk_type = _prompt_walk_type()
    mood = _prompt_text("Ваше настроение (например, спокойное/игривое/романтичное): ")
    goal = _prompt_text("Цель прогулки (например, расслабиться/повеселиться/исследовать город): ")
    time_limit = _prompt_time()
    return UserParams(
        walk_type=walk_type,
        mood=mood,
        goal=goal,
        time_limit=time_limit,
    )
    

def confirm_walk_params(params: UserParams) -> str:
    display_message("\nПроверьте выбранные параметры:")
    display_message(
        f"Тип прогулки: {params.walk_type}, настроение: {params.mood}, цель: {params.goal}, "
        f"время: {params.time_limit} мин"
    )
    display_message("1 — Подтвердить и сгенерировать прогулку")
    display_message("2 — Изменить настройки")
    while True:
        choice = input("Выберите пункт: ").strip()
        if choice in {"1", "2"}:
            return choice
        display_message("Некорректный выбор. Попробуйте снова.")
