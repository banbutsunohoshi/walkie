from pathlib import Path
import sys

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def pytest_addoption(parser):
    parser.addoption("--cov", action="append", default=[], help="(noop) coverage target")
    parser.addoption(
        "--cov-report",
        action="append",
        default=[],
        help="(noop) coverage report",
    )

from domain.models import HistoryEntry, Quest, UserParams, WalkTask


@pytest.fixture
def sample_user_params() -> UserParams:
    return UserParams(
        walk_type="solo",
        mood="calm",
        goal="relax",
        time_limit=25,
    )


@pytest.fixture
def sample_quests() -> list[Quest]:
    return [
        Quest(
            id=1,
            title="Quiet park loop",
            walk_type="solo",
            mood=["calm", "mindful"],
            goals=["relax"],
            duration=10,
        ),
        Quest(
            id=2,
            title="City photo hunt",
            walk_type="solo",
            mood=["calm", "fun"],
            goals=["relax", "explore"],
            duration=20,
        ),
        Quest(
            id=3,
            title="Dog friendly trail",
            walk_type="dog",
            mood=["active"],
            goals=["exercise"],
            duration=15,
        ),
    ]


@pytest.fixture
def sample_history(sample_user_params: UserParams, sample_quests: list[Quest]) -> list[HistoryEntry]:
    tasks = [WalkTask(quest=sample_quests[1], completed=True)]
    return [
        HistoryEntry(
            id=1,
            date="2024-01-01T10:00",
            walk_type=sample_user_params.walk_type,
            params=sample_user_params,
            tasks=tasks,
            score=80,
            status="finished",
        )
    ]
