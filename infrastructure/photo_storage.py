from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class FileSystemPhotoStorage:
    """Хранилище фоток (локально пока что)"""

    data_dir: Path
    storage_name: str

    def __init__(self, data_dir: str, storage_name: str) -> None:
        self.data_dir = Path(data_dir)
        self.storage_name = storage_name

    @property
    def base_dir(self) -> Path:
        return self.data_dir / "photos" / self.storage_name

    def store_photo(
        self,
        entry_id: int,
        task_id: int,
        filename: str,
        data: bytes,
    ) -> dict[str, str]:
        """Сохранение фото и возврат метаданных для истории"""
        safe_name = Path(filename).name or "photo.jpg"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        target_dir = self.base_dir / str(entry_id) / f"task_{task_id}"
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / f"{timestamp}_{safe_name}"
        target_path.write_bytes(data)
        relative_path = target_path.relative_to(self.data_dir)
        return {"file_path": str(relative_path), "storage": self.storage_name}

    def list_photos(self, entry_id: int, task_id: int) -> list[dict[str, str]]:
        """Возврат метаданных для уже сохраненных фото"""
        target_dir = self.base_dir / str(entry_id) / f"task_{task_id}"
        if not target_dir.exists():
            return []
        photos = []
        for path in sorted(target_dir.iterdir()):
            if path.is_file():
                relative_path = path.relative_to(self.data_dir)
                photos.append(
                    {"file_path": str(relative_path), "storage": self.storage_name}
                )
        return photos

    def delete_photo(self, photo_id: str) -> None:
        """Удалить фото по пути"""
        path = Path(photo_id)
        if not path.is_absolute():
            path = self.data_dir / path
        if path.exists():
            path.unlink()


class LocalPhotoStorage(FileSystemPhotoStorage):
    """Локальное хранилище фотографий"""

    def __init__(self, data_dir: str) -> None:
        super().__init__(data_dir=data_dir, storage_name="local")
