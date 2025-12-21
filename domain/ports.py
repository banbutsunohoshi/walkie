from __future__ import annotations

from typing import Iterable, Protocol

from domain.models import HistoryEntry, Quest, UserParams


class QuestRanker(Protocol):
    """Интерфейс для ML (чтобы предлагать нужные квесты)"""

    def rank(
        self,
        quests: Iterable[Quest],
        history: Iterable[HistoryEntry],
        params: UserParams,
    ) -> list[Quest]:
        """Возврат заданий, упорядоченных по значимости для текущего запроса"""


class PhotoStorage(Protocol):
    """Интерфейс для хранения фотографий после прохождения квестов"""

    def store_photo(
        self,
        entry_id: int,
        task_id: int,
        filename: str,
        data: bytes,
    ) -> dict[str, str]:
        """Сохранение фото и возвраст метаданных для хранения в истории"""

    def list_photos(self, entry_id: int, task_id: int) -> list[dict[str, str]]:
        """Возврат метаданных от фото после прохождения квеста"""

    def delete_photo(self, photo_id: str) -> None:
        """Удаление фото по ид"""
