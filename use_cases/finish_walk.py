from dataclasses import dataclass

from domain.models import HistoryEntry, UserParams, WalkTask
from domain.services import ScoringService, WalkStorage


@dataclass
class FinishWalkUseCase:
    scoring_service: ScoringService
    walk_storage: WalkStorage

    def execute(
        self,
        params: UserParams,
        tasks: list[WalkTask],
        entry_id: int | None = None,
        status: str = "finished",
        comment: str | None = None,
    ) -> HistoryEntry:
        score = self.scoring_service.calculate_score(tasks)
        if entry_id is None:
            entry_id = self.walk_storage.next_id()
        entry = HistoryEntry.create(
            walk_type=params.walk_type,
            params=params,
            tasks=tasks,
            score=score,
            status=status,
            comment=comment,
            entry_id=entry_id,
        )
        self.walk_storage.add_entry(entry)
        return entry


def finish_walk(
    params: UserParams,
    tasks: list[WalkTask],
    scoring_service: ScoringService,
    walk_storage: WalkStorage,
    entry_id: int | None = None,
    status: str = "finished",
    comment: str | None = None,
) -> HistoryEntry:
    return FinishWalkUseCase(
        scoring_service=scoring_service,
        walk_storage=walk_storage,
    ).execute(
        params=params,
        tasks=tasks,
        entry_id=entry_id,
        status=status,
        comment=comment,
    )
