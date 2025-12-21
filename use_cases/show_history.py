from domain.models import HistoryEntry
from domain.services import WalkStorage


def list_history(walk_storage: WalkStorage) -> list[HistoryEntry]:
    return walk_storage.load_history()


def get_history_entry(walk_storage: WalkStorage, entry_id: int) -> HistoryEntry | None:
    return walk_storage.get_entry(entry_id)
