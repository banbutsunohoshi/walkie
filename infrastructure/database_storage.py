from __future__ import annotations

from typing import Any


class DatabaseStorage:
    """Место для ДБ для хранения фотографий"""

    def __init__(self, dsn: str) -> None:
        self.dsn = dsn

    def connect(self) -> None:
        """инициаоизация соединения"""
        raise NotImplementedError("Database connection is not implemented yet :(")

    def fetch(self, query: str, parameters: tuple[Any, ...] | None = None) -> list[dict[str, Any]]:
        """запуск SELECT"""
        raise NotImplementedError("Database queries are not implemented yet :(")

    def execute(self, query: str, parameters: tuple[Any, ...] | None = None) -> None:
        """запуск INSERT/UPDATE/DELETE"""
        raise NotImplementedError("Database writes are not implemented yet :(")
