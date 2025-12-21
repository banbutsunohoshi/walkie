from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from domain.models import HistoryEntry, Quest, UserParams, WalkTask
from infrastructure.json_storage import JsonStorage


@dataclass
class QuestRepository:
    storage: JsonStorage

    def load_quests(self) -> list[Quest]:
        data = self.storage.read_json(default=[])
        return [Quest.from_dict(item) for item in data]

    def find_matching(self, params: UserParams) -> list[Quest]:
        quests = self.load_quests()
        matched = []
        for quest in quests:
            if quest.walk_type != params.walk_type:
                continue
            if params.mood not in quest.mood:
                continue
            if params.goal not in quest.goals:
                continue
            matched.append(quest)
        return matched


class RecommendationService:
    def recommend(
        self, quests: Iterable[Quest], history: Iterable[HistoryEntry]
    ) -> list[Quest]:
        recent_ids = {task.quest.id for entry in history for task in entry.tasks}
        scored: list[tuple[int, Quest]] = []
        for quest in quests:
            penalty = 1 if quest.id in recent_ids else 0
            scored.append((penalty, quest))
        scored.sort(key=lambda pair: pair[0])
        return [quest for _, quest in scored]


class ScoringService:
    def calculate_score(self, tasks: Iterable[WalkTask]) -> int:
        tasks = list(tasks)
        if not tasks:
            return 0
        completed = sum(1 for task in tasks if task.completed)
        photos_bonus = sum(1 for task in tasks if task.photos)
        score = int((completed / len(tasks)) * 100)
        return min(100, score + photos_bonus * 5)


@dataclass
class WalkStorage:
    storage: JsonStorage

    def load_history(self) -> list[HistoryEntry]:
        data = self.storage.read_json(default=[])
        return [HistoryEntry.from_dict(item) for item in data]

    def add_entry(self, entry: HistoryEntry) -> None:
        history = self.storage.read_json(default=[])
        history.append(entry.to_dict())
        self.storage.write_json(history)

    def get_entry(self, entry_id: int) -> HistoryEntry | None:
        for entry in self.load_history():
            if entry.id == entry_id:
                return entry
        return None

    def next_id(self) -> int:
        history = self.load_history()
        if not history:
            return 1
        return max(entry.id for entry in history) + 1


class MLRecommendationService:
    """Место для дальнейшей реализации МО"""

    def rank(
        self,
        quests: Iterable[Quest],
        history: Iterable[HistoryEntry],
        params: UserParams,
    ) -> list[Quest]:
        raise NotImplementedError("ML recommendation is not implemented yet :(")
