from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from .runtime import RerunException, get_current_runtime


class SessionStateProxy:
    def __getitem__(self, key: str) -> Any:
        return get_current_runtime().session_state[key]

    def __setitem__(self, key: str, value: Any) -> None:
        get_current_runtime().session_state[key] = value

    def __delitem__(self, key: str) -> None:
        del get_current_runtime().session_state[key]

    def __contains__(self, key: object) -> bool:
        return key in get_current_runtime().session_state

    def __iter__(self) -> Iterator[str]:
        return iter(get_current_runtime().session_state)

    def __len__(self) -> int:
        return len(get_current_runtime().session_state)

    def __getattr__(self, name: str) -> Any:
        return getattr(get_current_runtime().session_state, name)

    def __setattr__(self, name: str, value: Any) -> None:
        if name.startswith("_"):
            object.__setattr__(self, name, value)
            return
        setattr(get_current_runtime().session_state, name, value)

    def get(self, key: str, default: Any = None) -> Any:
        return get_current_runtime().session_state.get(key, default)

    def items(self):
        return get_current_runtime().session_state.items()

    def keys(self):
        return get_current_runtime().session_state.keys()

    def values(self):
        return get_current_runtime().session_state.values()


session_state = SessionStateProxy()


def title(body: Any, *, key: str | None = None) -> None:
    get_current_runtime().title(body, key=key)


def header(body: Any, *, key: str | None = None) -> None:
    get_current_runtime().header(body, key=key)


def text(body: Any) -> None:
    get_current_runtime().text(body)


def markdown(body: Any) -> None:
    get_current_runtime().markdown(body)


def divider() -> None:
    get_current_runtime().divider()


def success(body: Any) -> None:
    get_current_runtime().success(body)


def info(body: Any) -> None:
    get_current_runtime().info(body)


def warning(body: Any) -> None:
    get_current_runtime().warning(body)


def error(body: Any) -> None:
    get_current_runtime().error(body)


def write(*args: Any) -> None:
    get_current_runtime().write(*args)


def button(
    label: str,
    key: str | None = None,
    help: str | None = None,
    disabled: bool = False,
    on_click=None,
    args: tuple[Any, ...] | None = None,
    kwargs: dict[str, Any] | None = None,
) -> bool:
    return get_current_runtime().button(
        label,
        key=key,
        help=help,
        disabled=disabled,
        on_click=on_click,
        args=args,
        kwargs=kwargs,
    )


def slider(
    label: str,
    min_value: int | float = 0,
    max_value: int | float = 100,
    value: int | float | None = None,
    step: int | float = 1,
    *,
    key: str | None = None,
    help: str | None = None,
    disabled: bool = False,
    on_change=None,
    args: tuple[Any, ...] | None = None,
    kwargs: dict[str, Any] | None = None,
) -> int | float:
    return get_current_runtime().slider(
        label,
        min_value,
        max_value,
        value,
        step,
        key=key,
        help=help,
        disabled=disabled,
        on_change=on_change,
        args=args,
        kwargs=kwargs,
    )


def text_input(
    label: str,
    value: str = "",
    *,
    key: str | None = None,
    placeholder: str | None = None,
    disabled: bool = False,
    on_change=None,
    args: tuple[Any, ...] | None = None,
    kwargs: dict[str, Any] | None = None,
) -> str:
    return get_current_runtime().text_input(
        label,
        value,
        key=key,
        placeholder=placeholder,
        disabled=disabled,
        on_change=on_change,
        args=args,
        kwargs=kwargs,
    )


def checkbox(
    label: str,
    value: bool = False,
    *,
    key: str | None = None,
    disabled: bool = False,
    on_change=None,
    args: tuple[Any, ...] | None = None,
    kwargs: dict[str, Any] | None = None,
) -> bool:
    return get_current_runtime().checkbox(
        label,
        value,
        key=key,
        disabled=disabled,
        on_change=on_change,
        args=args,
        kwargs=kwargs,
    )


def rerun() -> None:
    raise RerunException()
