from dataclasses import dataclass

from domain.models import HistoryEntry
from domain.services import WalkStorage


@dataclass
class ShowHistoryUseCase:
    walk_storage: WalkStorage

    def list_history(self) -> list[HistoryEntry]:
        return self.walk_storage.load_history()

    def get_history_entry(self, entry_id: int) -> HistoryEntry | None:
        return self.walk_storage.get_entry(entry_id)
__all__ = ["ShowHistoryUseCase"]
