import os
from pathlib import Path

from cli.menu import show_main_menu
from cli.prompts import collect_walk_params
from cli.views import (
    display_history_entry,
    display_history_list,
    display_message,
    display_walk,
    display_walk_completion,
)
from domain.services import (
    QuestRepository,
    RecommendationService,
    ScoringService,
    WalkStorage,
)
from infrastructure.json_storage import JsonStorage
from use_cases.finish_walk import finish_walk
from use_cases.generate_walk import generate_walk
from use_cases.show_history import get_history_entry, list_history


def _build_storage(data_dir: str, filename: str) -> JsonStorage:
    path = Path(data_dir) / filename
    return JsonStorage(str(path))


def _run_new_walk(
    quest_repo: QuestRepository,
    recommendation_service: RecommendationService,
    scoring_service: ScoringService,
    walk_storage: WalkStorage,
) -> None:
    params = collect_walk_params()
    walk = generate_walk(params, quest_repo, recommendation_service, walk_storage)
    if not walk.tasks:
        display_message("Не удалось подобрать задания под ваши параметры.")
        return
    display_walk(walk)
    completion = display_walk_completion(walk)
    entry = finish_walk(walk, params, completion, scoring_service, walk_storage)
    display_message(
        f"Прогулка завершена! Выполнено заданий: {sum(completion)} из {len(walk.tasks)}."
    )
    display_message(f"Ваш итоговый балл: {entry.score}")


def _run_history(walk_storage: WalkStorage) -> None:
    history = list_history(walk_storage)
    if not history:
        display_message("История пока пуста.")
        return
    display_history_list(history)
    choice = input("Введите ID прогулки для подробностей (или Enter для выхода): ").strip()
    if not choice:
        return
    if not choice.isdigit():
        display_message("Введите числовой ID.")
        return
    entry = get_history_entry(walk_storage, int(choice))
    if not entry:
        display_message("Прогулка с таким ID не найдена.")
        return
    display_history_entry(entry)

def main() -> None:
    greeting = os.getenv("WALKIE_GREETING", "Добро пожаловать в Walkie!")
    data_dir = os.getenv("WALKIE_DATA_DIR", "/data")
        display_message(greeting)
    display_message(f"Data directory: {data_dir}")

    quest_storage = _build_storage(data_dir, "quests.json")
    history_storage = _build_storage(data_dir, "history.json")
    quest_repo = QuestRepository(storage=quest_storage)
    walk_storage = WalkStorage(storage=history_storage)
    recommendation_service = RecommendationService()
    scoring_service = ScoringService()

    while True:
        choice = show_main_menu()
        if choice == "1":
            _run_new_walk(
                quest_repo,
                recommendation_service,
                scoring_service,
                walk_storage,
            )
        elif choice == "2":
            _run_history(walk_storage)
        elif choice == "3":
            display_message("До встречи в Walkie!")
            break
        else:
            display_message("Некорректный выбор. Попробуйте снова.")


if __name__ == "__main__":
    main()
