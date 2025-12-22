from dataclasses import dataclass

from domain.models import UserParams, Walk, WalkTask
from domain.services import MLRecommendationService, QuestRepository, WalkStorage


@dataclass
class GenerateWalkUseCase:
    quest_repo: QuestRepository
    recommendation_service: MLRecommendationService
    walk_storage: WalkStorage

    def execute(self, params: UserParams) -> Walk:
        quests = self.quest_repo.find_matching(params)
        if not quests:
            quests = [
                quest
                for quest in self.quest_repo.load_quests()
                if quest.walk_type == params.walk_type
            ]
        history = self.walk_storage.load_history()
        recommended = self.recommendation_service.rank(quests, history, params)
        tasks: list[WalkTask] = []
        remaining = params.time_limit
        for quest in recommended:
            if quest.duration <= remaining:
                tasks.append(WalkTask(quest=quest))
                remaining -= quest.duration
        return Walk(tasks=tasks)
        

__all__ = ["GenerateWalkUseCase"]
