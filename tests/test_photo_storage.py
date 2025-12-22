from pathlib import Path

from infrastructure.photo_storage import LocalPhotoStorage


def test_local_photo_storage_saves_and_lists(tmp_path: Path) -> None:
    storage = LocalPhotoStorage(str(tmp_path))
    metadata = storage.store_photo(
        entry_id=1,
        task_id=2,
        filename="test.jpg",
        data=b"local-photo",
    )

    stored_path = tmp_path / metadata["file_path"]
    assert stored_path.exists()
    assert stored_path.read_bytes() == b"local-photo"
    assert metadata["storage"] == "local"

    listed = storage.list_photos(entry_id=1, task_id=2)
    assert len(listed) == 1
    assert (tmp_path / listed[0]["file_path"]).exists()


def test_local_photo_storage_deletes(tmp_path: Path) -> None:
    storage = LocalPhotoStorage(str(tmp_path))
    metadata = storage.store_photo(
        entry_id=3,
        task_id=1,
        filename="local.png",
        data=b"local-photo",
    )

    stored_path = tmp_path / metadata["file_path"]
    assert stored_path.exists()
    assert metadata["storage"] == "local"

    storage.delete_photo(metadata["file_path"])
    assert not stored_path.exists()
