from __future__ import annotations


class FileSystemPhotoStorage:
    """Местечко для будущего хранилища фотографий"""

    def __init__(self, base_dir: str) -> None:
        self.base_dir = base_dir

    def store_photo(self, entry_id: int, task_id: int, filename: str, data: bytes) -> dict[str, str]:
        """сохранение фото и возврат метаданных для хранения"""
        raise NotImplementedError("Photo storage is not implemented yet.")

    def list_photos(self, entry_id: int, task_id: int) -> list[dict[str, str]]:
        """возврат метаданных для уже сохраненных фото"""
        raise NotImplementedError("Photo listing is not implemented yet.")

    def delete_photo(self, photo_id: str) -> None:
        """удалить фото"""
        raise NotImplementedError("Photo deletion is not implemented yet.")
