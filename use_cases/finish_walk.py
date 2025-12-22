from domain.models import HistoryEntry, UserParams, WalkTask
from domain.services import ScoringService, WalkStorage


def finish_walk(
    params: UserParams,
    tasks: list[WalkTask],
    scoring_service: ScoringService,
    walk_storage: WalkStorage,
    status: str = "finished",
    comment: str | None = None,
) -> HistoryEntry:
    score = scoring_service.calculate_score(tasks)
    entry_id = walk_storage.next_id()
    entry = HistoryEntry.create(
        walk_type=params.walk_type,
        params=params,
        tasks=tasks,
        score=score,
        status=status,
        comment=comment,
        entry_id=entry_id,
    )
    walk_storage.add_entry(entry)
    return entry
