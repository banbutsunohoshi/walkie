rom pathlib import Path

from cli.menu import MainMenu
from cli.views import WalkView
from domain.models import HistoryEntry, Quest, UserParams, Walk, WalkTask
from infrastructure.photo_storage import LocalPhotoStorage


def test_main_menu_returns_choice():
    inputs = iter(["2"])
    messages: list[str] = []

    menu = MainMenu(
        input_func=lambda _: next(inputs),
        display_func=lambda message: messages.append(message),
    )

    assert menu.show() == "2"
    assert messages[0] == "\nГлавное меню"


def test_walk_view_display_walk_and_history():
    outputs: list[str] = []
    view = WalkView(display_func=outputs.append)
    quest = Quest(
        id=1,
        title="Test Quest",
        walk_type="solo",
        mood=["calm"],
        goals=["relax"],
        duration=10,
    )
    walk = Walk(tasks=[WalkTask(quest=quest)])

    view.display_walk(walk)

    params = UserParams(walk_type="solo", mood="calm", goal="relax", time_limit=30)
    entry = HistoryEntry.create(
        walk_type="solo",
        params=params,
        tasks=[WalkTask(quest=quest, completed=True)],
        score=80,
        status="finished",
        comment="Отлично",
        entry_id=1,
    )
    view.display_history_list([entry])
    view.display_history_entry(entry)

    assert any("Ваш маршрут" in line for line in outputs)
    assert any("История прогулок" in line for line in outputs)
    assert any("Прогулка 1" in line for line in outputs)


def test_walk_view_completion_with_photo(tmp_path: Path) -> None:
    photo_path = tmp_path / "photo.jpg"
    photo_path.write_bytes(b"test")

    quest = Quest(
        id=1,
        title="Photo Quest",
        walk_type="solo",
        mood=["calm"],
        goals=["relax"],
        duration=10,
    )
    walk = Walk(tasks=[WalkTask(quest=quest)])
    storage = LocalPhotoStorage(str(tmp_path))

    inputs = iter([
        "y",
        "y",
        str(photo_path),
        "Nice photo",
    ])
    view = WalkView(
        input_func=lambda _: next(inputs),
        display_func=lambda _: None,
    )

    tasks = view.display_walk_completion(walk=walk, entry_id=1, local_storage=storage)

    assert tasks[0].completed is True
    assert tasks[0].photos[0]["caption"] == "Nice photo"
    stored_path = tmp_path / tasks[0].photos[0]["file_path"]
    assert stored_path.exists()
