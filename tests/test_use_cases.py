from domain.models import WalkTask
from domain.services import MLRecommendationService, QuestRepository, ScoringService, WalkStorage
from infrastructure.json_storage import JsonStorage
from use_cases.finish_walk import FinishWalkUseCase
from use_cases.generate_walk import GenerateWalkUseCase
from use_cases.show_history import ShowHistoryUseCase


def test_generate_walk_uses_recommendations_and_time_limit(
    sample_user_params, sample_quests, sample_history, tmp_path
):
    quests_storage = JsonStorage(str(tmp_path / "quests.json"))
    quests_storage.write_json([quest.to_dict() for quest in sample_quests])
    history_storage = JsonStorage(str(tmp_path / "history.json"))
    history_storage.write_json([entry.to_dict() for entry in sample_history])

    use_case = GenerateWalkUseCase(
        quest_repo=QuestRepository(storage=quests_storage),
        recommendation_service=MLRecommendationService(),
        walk_storage=WalkStorage(storage=history_storage),
    )

    walk = use_case.execute(sample_user_params)
    
    assert [task.quest.id for task in walk.tasks] == [1]


def test_finish_walk_persists_entry(sample_user_params, sample_quests, tmp_path):
    storage = JsonStorage(str(tmp_path / "history.json"))
    walk_storage = WalkStorage(storage=storage)
    tasks = [
        WalkTask(quest=sample_quests[0], completed=True),
        WalkTask(quest=sample_quests[1], completed=False),
    ]

    use_case = FinishWalkUseCase(
        scoring_service=ScoringService(),
        walk_storage=walk_storage,
    )

    entry = use_case.execute(
        params=sample_user_params,
        tasks=tasks,
        comment="Отличная прогулка",
    )

    saved = storage.read_json(default=[])

    assert entry.id == 1
    assert len(saved) == 1
    assert saved[0]["score"] == 50
    assert saved[0]["tasks"][0]["completed"] is True
    assert saved[0]["comment"] == "Отличная прогулка"


def test_show_history_reads_entries(sample_history, tmp_path):
    storage = JsonStorage(str(tmp_path / "history.json"))
    storage.write_json([entry.to_dict() for entry in sample_history])
    walk_storage = WalkStorage(storage=storage)

    use_case = ShowHistoryUseCase(walk_storage=walk_storage)

    history = use_case.list_history()

    assert len(history) == 1
    assert use_case.get_history_entry(entry_id=1) is not None
    assert use_case.get_history_entry(entry_id=999) is None
