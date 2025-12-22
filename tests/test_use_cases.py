from domain.models import WalkTask
from domain.services import QuestRepository, RecommendationService, ScoringService, WalkStorage
from infrastructure.json_storage import JsonStorage
from use_cases.finish_walk import finish_walk
from use_cases.generate_walk import generate_walk
from use_cases.show_history import get_history_entry, list_history


def test_generate_walk_uses_recommendations_and_time_limit(
    sample_user_params, sample_quests, sample_history, tmp_path
):
    quests_storage = JsonStorage(str(tmp_path / "quests.json"))
    quests_storage.write_json([quest.to_dict() for quest in sample_quests])
    history_storage = JsonStorage(str(tmp_path / "history.json"))
    history_storage.write_json([entry.to_dict() for entry in sample_history])

    walk = generate_walk(
        params=sample_user_params,
        quest_repo=QuestRepository(storage=quests_storage),
        recommendation_service=RecommendationService(),
        walk_storage=WalkStorage(storage=history_storage),
    )

    assert [task.quest.id for task in walk.tasks] == [1]


def test_finish_walk_persists_entry(sample_user_params, sample_quests, tmp_path):
    storage = JsonStorage(str(tmp_path / "history.json"))
    walk_storage = WalkStorage(storage=storage)
    tasks = [
        WalkTask(quest=sample_quests[0], completed=True),
        WalkTask(quest=sample_quests[1], completed=False),
    ]

    entry = finish_walk(
        params=sample_user_params,
        tasks=tasks,
        scoring_service=ScoringService(),
        walk_storage=walk_storage,
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

    history = list_history(walk_storage)

    assert len(history) == 1
    assert get_history_entry(walk_storage, entry_id=1) is not None
    assert get_history_entry(walk_storage, entry_id=999) is None
