from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class UserParams:
    walk_type: str
    mood: str
    goal: str
    time_limit: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "walk_type": self.walk_type,
            "mood": self.mood,
            "goal": self.goal,
            "time_limit": self.time_limit,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "UserParams":
        return cls(
            walk_type=data["walk_type"],
            mood=data["mood"],
            goal=data["goal"],
            time_limit=int(data["time_limit"]),
        )


@dataclass(frozen=True)
class Quest:
    id: int
    title: str
    walk_type: str
    mood: list[str]
    goals: list[str]
    duration: int
    location_type: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "type": self.walk_type,
            "mood": self.mood,
            "goals": self.goals,
            "duration": self.duration,
            "location_type": self.location_type,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Quest":
        return cls(
            id=int(data["id"]),
            title=data["title"],
            walk_type=data["type"],
            mood=list(data.get("mood", [])),
            goals=list(data.get("goals", [])),
            duration=int(data.get("duration", 0)),
            location_type=data.get("location_type"),
        )


@dataclass
class WalkTask:
    quest: Quest
    completed: bool = False
    photos: list[dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.quest.title,
            "completed": self.completed,
            "photos": self.photos,
            "quest": self.quest.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "WalkTask":
        quest_data = data.get("quest") or {
            "id": data.get("id", 0),
            "title": data.get("title", ""),
            "type": data.get("type", ""),
            "mood": data.get("mood", []),
            "goals": data.get("goals", []),
            "duration": data.get("duration", 0),
            "location_type": data.get("location_type"),
        }
        return cls(
            quest=Quest.from_dict(quest_data),
            completed=bool(data.get("completed", False)),
            photos=list(data.get("photos", [])),
        )


@dataclass
class Walk:
    tasks: list[WalkTask]


@dataclass
class HistoryEntry:
    id: int
    date: str
    walk_type: str
    params: UserParams
    tasks: list[WalkTask]
    score: int
    status: str
    comment: str | None = None

    @classmethod
    def create(
        cls,
        walk_type: str,
        params: UserParams,
        tasks: list[WalkTask],
        score: int,
        status: str,
        comment: str | None,
        entry_id: int,
    ) -> "HistoryEntry":
        return cls(
            id=entry_id,
            date=datetime.now().isoformat(timespec="minutes"),
            walk_type=walk_type,
            params=params,
            tasks=tasks,
            score=score,
            status=status,
            comment=comment,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "date": self.date,
            "walk_type": self.walk_type,
            "params": self.params.to_dict(),
            "tasks": [task.to_dict() for task in self.tasks],
            "score": self.score,
            "status": self.status,
            "comment": self.comment,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "HistoryEntry":
        return cls(
            id=int(data["id"]),
            date=data["date"],
            walk_type=data["walk_type"],
            params=UserParams.from_dict(data["params"]),
            tasks=[WalkTask.from_dict(task) for task in data.get("tasks", [])],
            score=int(data.get("score", 0)),
            status=data.get("status", "unknown"),
            comment=data.get("comment"),
        )
