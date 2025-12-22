from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable

from domain.models import HistoryEntry, Walk, WalkTask
from domain.ports import PhotoStorage


def display_message(message: str) -> None:
    print(message)


@dataclass
class WalkView:
    input_func: Callable[[str], str] = input
    display_func: Callable[[str], None] = display_message

    def display_walk(self, walk: Walk) -> None:
        self.display_func("\nВаш маршрут:")
        for idx, task in enumerate(walk.tasks, start=1):
            self.display_func(
                f"{idx}. {task.quest.title} (≈ {task.quest.duration} мин, настроение: {', '.join(task.quest.mood)})"
            )
        self.display_func("Не забудьте сделать фото после каждого задания!\n")

    def _collect_photo_metadata(
        self,
        entry_id: int,
        task_id: int,
        local_storage: PhotoStorage,
    ) -> list[dict[str, str]]:
        response = self.input_func("Сделали фото? (y/n): ").strip().lower()
        if response != "y":
            return []
        while True:
            file_path_raw = self.input_func("Введите путь к фото (Enter — отмена): ").strip()
            if not file_path_raw:
                return []
            file_path = Path(file_path_raw)
            if not file_path.exists():
                self.display_func("Файл не найден. Укажите корректный путь.")
                continue
            try:
                data = file_path.read_bytes()
            except OSError:
                self.display_func("Не удалось прочитать файл. Попробуйте снова.")
                continue
            metadata = local_storage.store_photo(
                entry_id=entry_id,
                task_id=task_id,
                filename=file_path.name,
                data=data,
            )
            caption = self.input_func("Короткая подпись к фото (Enter — без подписи): ").strip()
            if caption:
                metadata["caption"] = caption
            return [metadata]

    def display_walk_completion(
        self,
        walk: Walk,
        entry_id: int,
        local_storage: PhotoStorage,
    ) -> list[WalkTask]:
        self.display_func("Отметьте выполнение заданий:")
        updated_tasks: list[WalkTask] = []
        for idx, task in enumerate(walk.tasks, start=1):
            response = self.input_func(f"Задание {idx} выполнено? (y/n): ").strip().lower()
            completed = response == "y"
            photos = self._collect_photo_metadata(
                entry_id=entry_id,
                task_id=idx,
                local_storage=local_storage,
            )
            updated_tasks.append(
                WalkTask(
                    quest=task.quest,
                    completed=completed,
                    photos=photos,
                )
            )
        return updated_tasks

    def display_history_list(self, history: Iterable[HistoryEntry]) -> None:
        self.display_func("\nИстория прогулок:")
        for entry in history:
            duration = sum(task.quest.duration for task in entry.tasks)
            summary = entry.comment or f"балл {entry.score}"
            self.display_func(
                f"ID {entry.id} | {entry.date} | тип: {entry.walk_type} | "
                f"длительность: {duration} мин | {summary}"
            )

    def display_history_entry(self, entry: HistoryEntry) -> None:
        self.display_func(f"\nПрогулка {entry.id} от {entry.date}")
        self.display_func(
            f"Тип: {entry.walk_type}, настроение: {entry.params.mood}, цель: {entry.params.goal}, время: {entry.params.time_limit} мин"
        )
        for idx, task in enumerate(entry.tasks, start=1):
            status = "готово" if task.completed else "не выполнено"
            self.display_func(f"{idx}. {task.quest.title} — {status}")
            if task.photos:
                self.display_func("   Фото:")
                for photo in task.photos:
                    caption = f" ({photo['caption']})" if photo.get("caption") else ""
                    self.display_func(f"   - {photo.get('file_path', '')}{caption}")
        self.display_func(f"Итоговый балл: {entry.score}")
        if entry.comment:
            self.display_func(f"Комментарий: {entry.comment}")


def display_walk(walk: Walk) -> None:
    WalkView().display_walk(walk)


def display_walk_completion(
    walk: Walk,
    entry_id: int,
    local_storage: PhotoStorage,
) -> list[WalkTask]:
    return WalkView().display_walk_completion(
        walk=walk,
        entry_id=entry_id,
        local_storage=local_storage,
    )


def display_history_list(history: Iterable[HistoryEntry]) -> None:
    WalkView().display_history_list(history)


def display_history_entry(entry: HistoryEntry) -> None:
    WalkView().display_history_entry(entry)
