from __future__ import annotations

import copy
from collections.abc import Iterator, MutableMapping
from typing import Any


class SessionState(MutableMapping[str, Any]):
    """Small dict-like state object with attribute access."""

    def __init__(self, initial: dict[str, Any] | None = None) -> None:
        object.__setattr__(self, "_data", dict(initial or {}))

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self._data[key] = value

    def __delitem__(self, key: str) -> None:
        del self._data[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __getattr__(self, name: str) -> Any:
        try:
            return self._data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    def __setattr__(self, name: str, value: Any) -> None:
        if name.startswith("_"):
            object.__setattr__(self, name, value)
            return
        self._data[name] = value

    def __delattr__(self, name: str) -> None:
        if name.startswith("_"):
            object.__delattr__(self, name)
            return
        try:
            del self._data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    def __repr__(self) -> str:
        return f"SessionState({self._data!r})"

    def snapshot(self) -> dict[str, Any]:
        snapshot: dict[str, Any] = {}
        for key, value in self._data.items():
            try:
                snapshot[key] = copy.deepcopy(value)
            except Exception:
                snapshot[key] = value
        return snapshot

    def restore(self, snapshot: dict[str, Any]) -> None:
        self._data.clear()
        self._data.update(snapshot)
