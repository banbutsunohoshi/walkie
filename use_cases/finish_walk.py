from typing import Iterable
from domain.models import HistoryEntry, UserParams, Walk, WalkTask
from domain.services import ScoringService, WalkStorage


def finish_walk(
    walk: Walk,
    params: UserParams,
    completion: Iterable[bool],
    scoring_service: ScoringService,
    walk_storage: WalkStorage,
) -> HistoryEntry:
    tasks: list[WalkTask] = []
    for task, completed in zip(walk.tasks, completion):
        tasks.append(
            WalkTask(
                quest=task.quest,
                completed=completed,
                photos=list(task.photos),
            )
        )
    score = scoring_service.calculate_score(tasks)
    entry = HistoryEntry.create(
        walk_type=params.walk_type,
        params=params,
        tasks=tasks,
        score=score,
        status="finished",
        entry_id=walk_storage.next_id(),
    )
    walk_storage.add_entry(entry)
    return entry
