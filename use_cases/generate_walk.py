from domain.models import Walk, WalkTask
from domain.services import QuestRepository, RecommendationService, WalkStorage
from domain.models import UserParams


def generate_walk(
    params: UserParams,
    quest_repo: QuestRepository,
    recommendation_service: RecommendationService,
    walk_storage: WalkStorage,
) -> Walk:
    quests = quest_repo.find_matching(params)
    history = walk_storage.load_history()
    recommended = recommendation_service.recommend(quests, history)
    tasks = []
    remaining = params.time_limit
    for quest in recommended:
        if quest.duration <= remaining:
            tasks.append(WalkTask(quest=quest))
            remaining -= quest.duration
    return Walk(tasks=tasks)
