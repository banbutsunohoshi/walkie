import json
from pathlib import Path
from typing import Any


class JsonStorage:
    def __init__(self, path: str) -> None:
        self.path = Path(path)

    def read_json(self, default: Any) -> Any:
        if not self.path.exists():
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.write_json(default)
            return default
        with self.path.open("r", encoding="utf-8") as file:
            return json.load(file)

    def write_json(self, data: Any) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
