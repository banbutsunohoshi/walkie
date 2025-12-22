from pathlib import Path
from typing import Iterable

from domain.models import HistoryEntry, Walk, WalkTask
from domain.ports import PhotoStorage


def display_message(message: str) -> None:
    print(message)


def display_walk(walk: Walk) -> None:
    display_message("\nВаш маршрут:")
    for idx, task in enumerate(walk.tasks, start=1):
        display_message(
            f"{idx}. {task.quest.title} (≈ {task.quest.duration} мин, настроение: {', '.join(task.quest.mood)})"
        )
    display_message("Не забудьте сделать фото после каждого задания!\n")


def _collect_photo_metadata(
    entry_id: int,
    task_id: int,
    local_storage: PhotoStorage,
) -> list[dict[str, str]]:
    response = input("Сделали фото? (y/n): ").strip().lower()
    if response != "y":
        return []
    while True:
        file_path_raw = input("Введите путь к фото (Enter — отмена): ").strip()
        if not file_path_raw:
            return []
        file_path = Path(file_path_raw)
        if not file_path.exists():
            display_message("Файл не найден. Укажите корректный путь.")
            continue
        try:
            data = file_path.read_bytes()
        except OSError:
            display_message("Не удалось прочитать файл. Попробуйте снова.")
            continue
        metadata = local_storage.store_photo(
            entry_id=entry_id,
            task_id=task_id,
            filename=file_path.name,
            data=data,
        )
        caption = input("Короткая подпись к фото (Enter — без подписи): ").strip()
        if caption:
            metadata["caption"] = caption
        return [metadata]


def display_walk_completion(
    walk: Walk,
    entry_id: int,
    local_storage: PhotoStorage,
) -> list[WalkTask]:
    display_message("Отметьте выполнение заданий:")
    updated_tasks: list[WalkTask] = []
    for idx, task in enumerate(walk.tasks, start=1):
        response = input(f"Задание {idx} выполнено? (y/n): ").strip().lower()
        completed = response == "y"
        photos = _collect_photo_metadata(
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


def display_history_list(history: Iterable[HistoryEntry]) -> None:
    display_message("\nИстория прогулок:")
    for entry in history:
        duration = sum(task.quest.duration for task in entry.tasks)
        summary = entry.comment or f"балл {entry.score}"
        display_message(
            f"ID {entry.id} | {entry.date} | тип: {entry.walk_type} | "
            f"длительность: {duration} мин | {summary}"
        )


def display_history_entry(entry: HistoryEntry) -> None:
    display_message(f"\nПрогулка {entry.id} от {entry.date}")
    display_message(
        f"Тип: {entry.walk_type}, настроение: {entry.params.mood}, цель: {entry.params.goal}, время: {entry.params.time_limit} мин"
    )
    for idx, task in enumerate(entry.tasks, start=1):
        status = "готово" if task.completed else "не выполнено"
        display_message(f"{idx}. {task.quest.title} — {status}")
        if task.photos:
            display_message("   Фото:")
            for photo in task.photos:
                caption = f" ({photo['caption']})" if photo.get("caption") else ""
                display_message(f"   - {photo.get('file_path', '')}{caption}")
    display_message(f"Итоговый балл: {entry.score}")
    if entry.comment:
        display_message(f"Комментарий: {entry.comment}")
