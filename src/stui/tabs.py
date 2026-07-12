from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any

from .runtime import ElementBlock, get_current_runtime


def tabs(
    labels: Sequence[str],
    *,
    key: str | None = None,
    default: int = 0,
    on_change: Callable[..., Any] | None = None,
    args: tuple[Any, ...] | None = None,
    kwargs: dict[str, Any] | None = None,
) -> tuple[ElementBlock, ...]:
    return get_current_runtime().tabs(
        labels,
        key=key,
        default=default,
        on_change=on_change,
        args=args,
        kwargs=kwargs,
    )
