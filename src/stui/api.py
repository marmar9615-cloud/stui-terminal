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


def subheader(body: Any, *, key: str | None = None) -> None:
    get_current_runtime().subheader(body, key=key)


def text(body: Any) -> None:
    get_current_runtime().text(body)


def caption(body: Any) -> None:
    get_current_runtime().caption(body)


def markdown(body: Any) -> None:
    get_current_runtime().markdown(body)


def code(body: Any, language: str | None = None) -> None:
    get_current_runtime().code(body, language=language)


def json(obj: Any) -> None:
    get_current_runtime().json(obj)


def exception(exc: BaseException) -> None:
    get_current_runtime().exception(exc)


def progress(value: int | float, text: Any | None = None) -> None:
    get_current_runtime().progress(value, text=text)


def metric(label: Any, value: Any, delta: Any | None = None) -> None:
    get_current_runtime().metric(label, value, delta=delta)


def bar_chart(
    data: Any,
    *,
    width: int | None = None,
    height: int | None = None,
) -> None:
    get_current_runtime().bar_chart(data, width=width, height=height)


def table(data: Any) -> None:
    get_current_runtime().table(data)


def dataframe(data: Any) -> None:
    get_current_runtime().dataframe(data)


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


def container():
    """Group following elements when used as a context manager."""
    return get_current_runtime().container()


def expander(label: str, expanded: bool = False):
    """Render a static expandable-looking group.

    MVP note: v0.3.0 expanders render either open or closed based on the
    initial expanded flag; interactive toggling is intentionally deferred.
    """
    return get_current_runtime().expander(label, expanded=expanded)


def form(key: str):
    """Group widgets under a form key.

    MVP note: widgets inside forms still update session_state normally; the
    submit button only gates a one-shot submitted return value.
    """
    return get_current_runtime().form(key)


def form_submit_button(
    label: str = "Submit",
    *,
    disabled: bool = False,
    on_click=None,
    args: tuple[Any, ...] | None = None,
    kwargs: dict[str, Any] | None = None,
) -> bool:
    return get_current_runtime().form_submit_button(
        label,
        disabled=disabled,
        on_click=on_click,
        args=args,
        kwargs=kwargs,
    )


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


def number_input(
    label: str,
    min_value: int | float | None = None,
    max_value: int | float | None = None,
    value: int | float = 0,
    step: int | float = 1,
    *,
    key: str | None = None,
    disabled: bool = False,
    on_change=None,
    args: tuple[Any, ...] | None = None,
    kwargs: dict[str, Any] | None = None,
) -> int | float:
    return get_current_runtime().number_input(
        label,
        min_value=min_value,
        max_value=max_value,
        value=value,
        step=step,
        key=key,
        disabled=disabled,
        on_change=on_change,
        args=args,
        kwargs=kwargs,
    )


def selectbox(
    label: str,
    options,
    index: int = 0,
    *,
    key: str | None = None,
    disabled: bool = False,
    on_change=None,
    args: tuple[Any, ...] | None = None,
    kwargs: dict[str, Any] | None = None,
):
    return get_current_runtime().selectbox(
        label,
        options,
        index=index,
        key=key,
        disabled=disabled,
        on_change=on_change,
        args=args,
        kwargs=kwargs,
    )


def radio(
    label: str,
    options,
    index: int = 0,
    *,
    key: str | None = None,
    disabled: bool = False,
    on_change=None,
    args: tuple[Any, ...] | None = None,
    kwargs: dict[str, Any] | None = None,
):
    return get_current_runtime().radio(
        label,
        options,
        index=index,
        key=key,
        disabled=disabled,
        on_change=on_change,
        args=args,
        kwargs=kwargs,
    )


def rerun() -> None:
    raise RerunException()
