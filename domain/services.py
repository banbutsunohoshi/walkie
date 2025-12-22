from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
import re
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
    """несложная ML-ранжировка на основе вводов и истории"""

    def __init__(self) -> None:
        self._mood_weights: dict[str, float] = {}
        self._goal_weights: dict[str, float] = {}
        self._quest_counts: dict[int, int] = {}

    @staticmethod
    def _tokenize(text: str) -> set[str]:
        tokens = re.findall(r"[a-zA-Zа-яА-Я0-9]+", text.lower())
        return set(tokens)

    @staticmethod
    def _token_overlap(source: set[str], target: set[str]) -> float:
        if not source or not target:
            return 0.0
        return len(source & target) / max(1, len(source))

    def _refresh_model(self, history: Iterable[HistoryEntry]) -> None:
        mood_weights: dict[str, float] = defaultdict(float)
        goal_weights: dict[str, float] = defaultdict(float)
        quest_counts: dict[int, int] = defaultdict(int)

        for entry in history:
            for task in entry.tasks:
                weight = 1.0
                if task.completed:
                    weight += 0.75
                if task.photos:
                    weight += 0.1 * len(task.photos)
                for mood in task.quest.mood:
                    mood_weights[mood.lower()] += weight
                for goal in task.quest.goals:
                    goal_weights[goal.lower()] += weight
                quest_counts[task.quest.id] += 1

        self._mood_weights = dict(mood_weights)
        self._goal_weights = dict(goal_weights)
        self._quest_counts = dict(quest_counts)

    def rank(
        self,
        quests: Iterable[Quest],
        history: Iterable[HistoryEntry],
        params: UserParams,
    ) -> list[Quest]:
        self._refresh_model(history)
        mood_tokens = self._tokenize(params.mood)
        goal_tokens = self._tokenize(params.goal)
        scored: list[tuple[float, Quest]] = []

        for quest in quests:
            if quest.walk_type != params.walk_type:
                continue
            quest_mood_tokens: set[str] = set()
            for mood in quest.mood:
                quest_mood_tokens |= self._tokenize(mood)
            quest_goal_tokens: set[str] = set()
            for goal in quest.goals:
                quest_goal_tokens |= self._tokenize(goal)

            score = 0.0
            score += self._token_overlap(mood_tokens, quest_mood_tokens) * 2.0
            score += self._token_overlap(goal_tokens, quest_goal_tokens) * 2.0
            if params.mood.lower() in {m.lower() for m in quest.mood}:
                score += 1.5
            if params.goal.lower() in {g.lower() for g in quest.goals}:
                score += 1.5
            for mood in quest.mood:
                score += self._mood_weights.get(mood.lower(), 0.0) * 0.2
            for goal in quest.goals:
                score += self._goal_weights.get(goal.lower(), 0.0) * 0.2
            score -= self._quest_counts.get(quest.id, 0) * 1.0

            scored.append((score, quest))

        scored.sort(key=lambda item: item[0], reverse=True)
        return [quest for _, quest in scored]
