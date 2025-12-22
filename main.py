import os
from pathlib import Path

from cli.menu import show_main_menu
from cli.prompts import collect_walk_params, confirm_walk_params
from cli.views import (
    display_history_entry,
    display_history_list,
    display_message,
    display_walk,
    display_walk_completion,
)
from domain.models import UserParams
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
    params: UserParams | None = None,
) -> None:
    while params is None:
        params = collect_walk_params()
        if confirm_walk_params(params) == "2":
            params = None
    walk = generate_walk(params, quest_repo, recommendation_service, walk_storage)
    if not walk.tasks:
        display_message("Не удалось подобрать задания под ваши параметры.")
        return
    display_walk(walk)
    tasks = display_walk_completion(walk)
    display_message("\nЗавершить прогулку?")
    display_message("1 — Завершить прогулку")
    display_message("2 — Прервать прогулку")
    while True:
        finish_choice = input("Выберите пункт: ").strip()
        if finish_choice in {"1", "2"}:
            break
        display_message("Некорректный выбор. Попробуйте снова.")
    status = "finished" if finish_choice == "1" else "aborted"
    if status == "aborted":
        save_partial = input("Сохранить частичный результат? (y/n): ").strip().lower()
        if save_partial != "y":
            display_message("Прогулка прервана без сохранения.")
            return
    comment = input("Короткий комментарий/оценка (Enter — без комментария): ").strip()
    entry = finish_walk(
        params=params,
        tasks=tasks,
        scoring_service=scoring_service,
        walk_storage=walk_storage,
        status=status,
        comment=comment or None,
    )
    completed_count = sum(1 for task in tasks if task.completed)
    display_message(
        f"Прогулка сохранена в историю! Выполнено заданий: {completed_count} из {len(tasks)}."
    )
    if entry.comment:
        display_message(f"Комментарий: {entry.comment}")
    else:
        display_message("Комментарий: без комментария.")
    display_message(f"Ваш итоговый балл: {entry.score}")


def _run_history(
    quest_repo: QuestRepository,
    recommendation_service: RecommendationService,
    scoring_service: ScoringService,
    walk_storage: WalkStorage,
) -> None:
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
    repeat = input("Повторить похожую прогулку? (y/n): ").strip().lower()
    if repeat == "y":
        _run_new_walk(
            quest_repo=quest_repo,
            recommendation_service=recommendation_service,
            scoring_service=scoring_service,
            walk_storage=walk_storage,
            params=entry.params,
        )

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
            _run_history(
                quest_repo,
                recommendation_service,
                scoring_service,
                walk_storage,
            )
        elif choice == "3":
            display_message("До встречи в Walkie!")
            break
        else:
            display_message("Некорректный выбор. Попробуйте снова.")


if __name__ == "__main__":
    main()
