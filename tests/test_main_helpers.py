from pathlib import Path

from infrastructure.json_storage import JsonStorage
from infrastructure.database_storage import DatabaseStorage
from main import _build_storage, _seed_data_file


def test_build_storage_returns_json_storage(tmp_path: Path) -> None:
    storage = _build_storage(str(tmp_path), "data.json")

    assert isinstance(storage, JsonStorage)
    assert storage.path == tmp_path / "data.json"


def test_json_storage_creates_file_on_read(tmp_path: Path) -> None:
    storage = JsonStorage(str(tmp_path / "state.json"))

    data = storage.read_json(default={"status": "ok"})

    assert data == {"status": "ok"}
    assert storage.path.exists()


def test_seed_data_file_copies_once(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    fallback_dir = tmp_path / "fallback"
    fallback_dir.mkdir()
    fallback_file = fallback_dir / "seed.json"
    fallback_file.write_text("seed", encoding="utf-8")

    _seed_data_file(str(data_dir), "seed.json", fallback_dir)
    target_file = data_dir / "seed.json"
    assert target_file.read_text(encoding="utf-8") == "seed"

    target_file.write_text("changed", encoding="utf-8")
    _seed_data_file(str(data_dir), "seed.json", fallback_dir)
    assert target_file.read_text(encoding="utf-8") == "changed"


def test_database_storage_not_implemented() -> None:
    storage = DatabaseStorage("dsn")

    try:
        storage.connect()
    except NotImplementedError:
        pass
    else:
        raise AssertionError("connect should raise NotImplementedError")

    try:
        storage.fetch("SELECT 1")
    except NotImplementedError:
        pass
    else:
        raise AssertionError("fetch should raise NotImplementedError")

    try:
        storage.execute("DELETE")
    except NotImplementedError:
        pass
    else:
        raise AssertionError("execute should raise NotImplementedError")
