import os
from pathlib import Path

from cli.menu import MainMenu
from cli.prompts import WalkPrompter
from cli.views import WalkView, display_message
from domain.models import UserParams
from domain.services import (
    MLRecommendationService,
    QuestRepository,
    ScoringService,
    WalkStorage,
)
from infrastructure.json_storage import JsonStorage
from infrastructure.photo_storage import LocalPhotoStorage
from use_cases.finish_walk import FinishWalkUseCase
from use_cases.generate_walk import GenerateWalkUseCase
from use_cases.show_history import ShowHistoryUseCase


def _build_storage(data_dir: str, filename: str) -> JsonStorage:
    path = Path(data_dir) / filename
    return JsonStorage(str(path))


def _seed_data_file(data_dir: str, filename: str, fallback_dir: Path) -> None:
    target_path = Path(data_dir) / filename
    if target_path.exists():
        return
    fallback_path = fallback_dir / filename
    if not fallback_path.exists():
        return
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(fallback_path.read_text(encoding="utf-8"), encoding="utf-8")

class WalkieApp:
    def __init__(
        self,
        menu: MainMenu,
        prompter: WalkPrompter,
        view: WalkView,
        generator: GenerateWalkUseCase,
        finisher: FinishWalkUseCase,
        historian: ShowHistoryUseCase,
        walk_storage: WalkStorage,
        local_photo_storage: LocalPhotoStorage,
    ) -> None:
        self.menu = menu
        self.prompter = prompter
        self.view = view
        self.generator = generator
        self.finisher = finisher
        self.historian = historian
        self.walk_storage = walk_storage
        self.local_photo_storage = local_photo_storage
        
    def run(self) -> None:
        while True:
            choice = self.menu.show()
            if choice == "1":
                self._run_new_walk()
            elif choice == "2":
                self._run_history()
            elif choice == "3":
                display_message("До встречи в Walkie!")
                break
            else:
                display_message("Некорректный выбор. Попробуйте снова.")

    def _run_new_walk(self, params: UserParams | None = None) -> None:
        while params is None:
            params = self.prompter.collect_walk_params()
            if self.prompter.confirm_walk_params(params) == "2":
                params = None
        walk = self.generator.execute(params)
        if not walk.tasks:
            display_message("Не удалось подобрать задания под ваши параметры.")
            return
        self.view.display_walk(walk)
        entry_id = self.walk_storage.next_id()
        tasks = self.view.display_walk_completion(
            walk=walk,
            entry_id=entry_id,
            local_storage=self.local_photo_storage,
        )
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
        entry = self.finisher.execute(
            params=params,
            tasks=tasks,
            entry_id=entry_id,
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

    def _run_history(self) -> None:
        history = self.historian.list_history()
        if not history:
            display_message("История пока пуста.")
            return
        self.view.display_history_list(history)
        choice = input("Введите ID прогулки для подробностей (или Enter для выхода): ").strip()
        if not choice:
            return
        if not choice.isdigit():
            display_message("Введите числовой ID.")
            return
        entry = self.historian.get_history_entry(int(choice))
        if not entry:
            display_message("Прогулка с таким ID не найдена.")
            return
        self.view.display_history_entry(entry)
        repeat = input("Повторить похожую прогулку? (y/n): ").strip().lower()
        if repeat == "y":
            self._run_new_walk(params=entry.params)


def build_app(data_dir: str) -> WalkieApp:
    fallback_dir = Path(__file__).resolve().parent / "data"
    _seed_data_file(data_dir, "quests.json", fallback_dir)
    _seed_data_file(data_dir, "history.json", fallback_dir)
    
    quest_storage = _build_storage(data_dir, "quests.json")
    history_storage = _build_storage(data_dir, "history.json")
    quest_repo = QuestRepository(storage=quest_storage)
    walk_storage = WalkStorage(storage=history_storage)
    ml_recommendation_service = MLRecommendationService()
    scoring_service = ScoringService()
    local_photo_storage = LocalPhotoStorage(data_dir)

    return WalkieApp(
        menu=MainMenu(),
        prompter=WalkPrompter(),
        view=WalkView(),
        generator=GenerateWalkUseCase(
            quest_repo=quest_repo,
            recommendation_service=ml_recommendation_service,
            walk_storage=walk_storage,
        ),
        finisher=FinishWalkUseCase(
            scoring_service=scoring_service,
            walk_storage=walk_storage,
        ),
        historian=ShowHistoryUseCase(walk_storage=walk_storage),
        walk_storage=walk_storage,
        local_photo_storage=local_photo_storage,
    )


def main() -> None:
    greeting = os.getenv("WALKIE_GREETING", "Добро пожаловать в Walkie!")
    data_dir = os.getenv("WALKIE_DATA_DIR", "/data")
    display_message(greeting)
    display_message(f"Data directory: {data_dir}")

    build_app(data_dir).run()


if __name__ == "__main__":
    main()
