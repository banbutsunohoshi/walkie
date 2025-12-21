from typing import Iterable
from domain.models import HistoryEntry, Walk


def display_message(message: str) -> None:
    print(message)


def display_walk(walk: Walk) -> None:
    display_message("\nВаш маршрут:")
    for idx, task in enumerate(walk.tasks, start=1):
        display_message(
            f"{idx}. {task.quest.title} (≈ {task.quest.duration} мин, настроение: {', '.join(task.quest.mood)})"
        )
    display_message("Не забудьте сделать фото после каждого задания!\n")


def display_walk_completion(walk: Walk) -> list[bool]:
    completions: list[bool] = []
    display_message("Отметьте выполнение заданий:")
    for idx, task in enumerate(walk.tasks, start=1):
        response = input(f"Задание {idx} выполнено? (y/n): ").strip().lower()
        completions.append(response == "y")
    return completions


def display_history_list(history: Iterable[HistoryEntry]) -> None:
    display_message("\nИстория прогулок:")
    for entry in history:
        display_message(
            f"ID {entry.id} | {entry.date} | тип: {entry.walk_type} | балл: {entry.score} | статус: {entry.status}"
        )


def display_history_entry(entry: HistoryEntry) -> None:
    display_message(f"\nПрогулка {entry.id} от {entry.date}")
    display_message(
        f"Тип: {entry.walk_type}, настроение: {entry.params.mood}, цель: {entry.params.goal}, время: {entry.params.time_limit} мин"
    )
    for idx, task in enumerate(entry.tasks, start=1):
        status = "готово" if task.completed else "не выполнено"
        display_message(f"{idx}. {task.quest.title} — {status}")
    display_message(f"Итоговый балл: {entry.score}")
