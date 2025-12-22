from domain.models import Walk, WalkTask
from domain.services import MLRecommendationService, QuestRepository, WalkStorage
from domain.models import UserParams


def generate_walk(
    params: UserParams,
    quest_repo: QuestRepository,
    recommendation_service: MLRecommendationService,
    walk_storage: WalkStorage,
) -> Walk:
    quests = quest_repo.load_quests()
    history = walk_storage.load_history()
    recommended = recommendation_service.rank(quests, history, params)
    tasks = []
    remaining = params.time_limit
    for quest in recommended:
        if quest.duration <= remaining:
            tasks.append(WalkTask(quest=quest))
            remaining -= quest.duration
    return Walk(tasks=tasks)
