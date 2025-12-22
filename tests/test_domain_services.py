from domain.models import WalkTask
from domain.services import MLRecommendationService, QuestRepository, RecommendationService, ScoringService
from infrastructure.json_storage import JsonStorage


def test_find_matching_filters_by_params(sample_user_params, sample_quests, tmp_path):
    storage = JsonStorage(str(tmp_path / "quests.json"))
    storage.write_json([quest.to_dict() for quest in sample_quests])

    repo = QuestRepository(storage=storage)
    matched = repo.find_matching(sample_user_params)

    assert [quest.id for quest in matched] == [1, 2]


def test_recommendation_prioritizes_unseen(sample_history, sample_quests):
    service = RecommendationService()

    recommended = service.recommend(sample_quests[:2], sample_history)

    assert [quest.id for quest in recommended] == [1, 2]


def test_ml_recommendation_uses_history_and_params(
    sample_history, sample_quests, sample_user_params
):
    service = MLRecommendationService()

    ranked = service.rank(sample_quests, sample_history, sample_user_params)

    assert [quest.id for quest in ranked] == [1, 2]


def test_scoring_accounts_for_completion_and_photos(sample_quests):
    service = ScoringService()

    tasks = [
        WalkTask(quest=sample_quests[0], completed=True),
        WalkTask(quest=sample_quests[1], completed=False, photos=[{"path": "1.jpg"}]),
    ]

    assert service.calculate_score(tasks) == 55


def test_scoring_caps_at_100(sample_quests):
    service = ScoringService()

    tasks = [WalkTask(quest=sample_quests[0], completed=True, photos=[{"path": "1.jpg"}])]

    assert service.calculate_score(tasks) == 100


def test_scoring_empty_tasks_is_zero():
    service = ScoringService()

    assert service.calculate_score([]) == 0
