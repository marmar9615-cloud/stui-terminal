from __future__ import annotations

import contextvars
import json as json_lib
import runpy
import sys
import traceback
from collections.abc import Callable
from pathlib import Path
from typing import Any

from .elements import (
    AlertElement,
    ButtonElement,
    CaptionElement,
    CheckboxElement,
    CodeElement,
    DividerElement,
    Element,
    ErrorElement,
    ExceptionElement,
    HeaderElement,
    JsonElement,
    MarkdownElement,
    NumberInputElement,
    ProgressElement,
    RadioElement,
    SelectboxElement,
    SliderElement,
    SubheaderElement,
    TableElement,
    TextElement,
    TextInputElement,
    TitleElement,
    WriteElement,
)
from .session_state import SessionState
from .widgets.slider import snap_value

_current_runtime: contextvars.ContextVar[Runtime | None] = contextvars.ContextVar(
    "stui_current_runtime", default=None
)


class RerunException(Exception):
    """Internal signal used by st.rerun in later API slices."""


class DuplicateWidgetKeyError(Exception):
    """Raised when a script reuses an explicit widget key in one run."""


class Runtime:
    def __init__(self, script_path: str | Path) -> None:
        self.script_path = Path(script_path).resolve()
        self.session_state = SessionState()
        self.elements: list[Element] = []
        self.widget_call_counts: dict[tuple[str, str], int] = {}
        self.explicit_widget_keys_seen: set[str] = set()
        self.pending_button_presses: set[str] = set()
        self.pending_changed_widgets: set[str] = set()
        self.last_focused_key: str | None = None
        self._active_button_presses: set[str] = set()
        self._active_changed_widgets: set[str] = set()

    def run_script(self) -> list[Element]:
        for _ in range(10):
            self._prepare_run()
            token = _current_runtime.set(self)
            path_added = self._push_script_dir()
            session_snapshot = self.session_state.snapshot()
            try:
                runpy.run_path(str(self.script_path), run_name="__main__")
            except RerunException:
                continue
            except DuplicateWidgetKeyError as exc:
                self.session_state.restore(session_snapshot)
                self.elements = [ErrorElement(str(exc))]
            except Exception:
                self.session_state.restore(session_snapshot)
                self.elements = [ErrorElement(traceback.format_exc())]
            finally:
                self._pop_script_dir(path_added)
                _current_runtime.reset(token)
            return self.elements

        self.elements = [
            ErrorElement("stui stopped after 10 consecutive rerun requests.")
        ]
        return self.elements

    def title(self, body: Any, *, key: str | None = None) -> None:
        self.elements.append(TitleElement(str(body), key=key))

    def header(self, body: Any, *, key: str | None = None) -> None:
        self.elements.append(HeaderElement(str(body), key=key))

    def subheader(self, body: Any, *, key: str | None = None) -> None:
        self.elements.append(SubheaderElement(str(body), key=key))

    def text(self, body: Any) -> None:
        self.elements.append(TextElement(str(body)))

    def caption(self, body: Any) -> None:
        self.elements.append(CaptionElement(str(body)))

    def markdown(self, body: Any) -> None:
        self.elements.append(MarkdownElement(str(body)))

    def code(self, body: Any, language: str | None = None) -> None:
        self.elements.append(CodeElement(str(body), language=language))

    def json(self, obj: Any) -> None:
        text = json_lib.dumps(obj, indent=2, sort_keys=True, default=str)
        self.elements.append(JsonElement(obj=obj, text=text))

    def exception(self, exc: BaseException) -> None:
        rendered = "".join(
            traceback.format_exception(type(exc), exc, exc.__traceback__)
        )
        self.elements.append(ExceptionElement(rendered))

    def progress(self, value: int | float, text: Any | None = None) -> None:
        label = None if text is None else str(text)
        self.elements.append(
            ProgressElement(_normalize_progress(value), label)
        )

    def table(self, data: Any) -> None:
        headers, rows = _normalize_table(data)
        self.elements.append(TableElement(headers=headers, rows=rows))

    def dataframe(self, data: Any) -> None:
        self.table(data)

    def divider(self) -> None:
        self.elements.append(DividerElement())

    def success(self, body: Any) -> None:
        self.elements.append(AlertElement(str(body), "success"))

    def info(self, body: Any) -> None:
        self.elements.append(AlertElement(str(body), "info"))

    def warning(self, body: Any) -> None:
        self.elements.append(AlertElement(str(body), "warning"))

    def error(self, body: Any) -> None:
        self.elements.append(AlertElement(str(body), "error"))

    def write(self, *args: Any) -> None:
        text = " ".join(str(arg) for arg in args)
        self.elements.append(WriteElement(tuple(args), text))

    def button(
        self,
        label: str,
        *,
        key: str | None = None,
        help: str | None = None,
        disabled: bool = False,
        on_click: Callable[..., Any] | None = None,
        args: tuple[Any, ...] | None = None,
        kwargs: dict[str, Any] | None = None,
    ) -> bool:
        widget_key = self.next_widget_key("button", label, key)
        pressed = False if disabled else self.consume_button_press(widget_key)
        self.elements.append(
            ButtonElement(label=label, key=widget_key, help=help, disabled=disabled)
        )
        if pressed and on_click is not None:
            on_click(*(args or ()), **(kwargs or {}))
        return pressed

    def slider(
        self,
        label: str,
        min_value: int | float = 0,
        max_value: int | float = 100,
        value: int | float | None = None,
        step: int | float = 1,
        *,
        key: str | None = None,
        help: str | None = None,
        disabled: bool = False,
        on_change: Callable[..., Any] | None = None,
        args: tuple[Any, ...] | None = None,
        kwargs: dict[str, Any] | None = None,
    ) -> int | float:
        widget_key = self.next_widget_key("slider", label, key)
        default = min_value if value is None else value
        current = self.session_state.get(widget_key, default)
        snapped = snap_value(current, min_value, max_value, step)
        self.session_state[widget_key] = snapped
        self.elements.append(
            SliderElement(
                label=label,
                key=widget_key,
                min_value=min_value,
                max_value=max_value,
                value=snapped,
                step=step,
                help=help,
                disabled=disabled,
            )
        )
        if (
            not disabled
            and self.consume_changed_widget(widget_key)
            and on_change is not None
        ):
            on_change(*(args or ()), **(kwargs or {}))
        return snapped

    def text_input(
        self,
        label: str,
        value: str = "",
        *,
        key: str | None = None,
        placeholder: str | None = None,
        disabled: bool = False,
        on_change: Callable[..., Any] | None = None,
        args: tuple[Any, ...] | None = None,
        kwargs: dict[str, Any] | None = None,
    ) -> str:
        widget_key = self.next_widget_key("text_input", label, key)
        current = str(self.session_state.get(widget_key, value))
        self.session_state[widget_key] = current
        self.elements.append(
            TextInputElement(
                label=label,
                key=widget_key,
                value=current,
                placeholder=placeholder,
                disabled=disabled,
            )
        )
        if (
            not disabled
            and self.consume_changed_widget(widget_key)
            and on_change is not None
        ):
            on_change(*(args or ()), **(kwargs or {}))
        return current

    def checkbox(
        self,
        label: str,
        value: bool = False,
        *,
        key: str | None = None,
        disabled: bool = False,
        on_change: Callable[..., Any] | None = None,
        args: tuple[Any, ...] | None = None,
        kwargs: dict[str, Any] | None = None,
    ) -> bool:
        widget_key = self.next_widget_key("checkbox", label, key)
        current = bool(self.session_state.get(widget_key, value))
        self.session_state[widget_key] = current
        self.elements.append(
            CheckboxElement(
                label=label,
                key=widget_key,
                value=current,
                disabled=disabled,
            )
        )
        if (
            not disabled
            and self.consume_changed_widget(widget_key)
            and on_change is not None
        ):
            on_change(*(args or ()), **(kwargs or {}))
        return current

    def number_input(
        self,
        label: str,
        min_value: int | float | None = None,
        max_value: int | float | None = None,
        value: int | float = 0,
        step: int | float = 1,
        *,
        key: str | None = None,
        disabled: bool = False,
        on_change: Callable[..., Any] | None = None,
        args: tuple[Any, ...] | None = None,
        kwargs: dict[str, Any] | None = None,
    ) -> int | float:
        widget_key = self.next_widget_key("number_input", label, key)
        current = _coerce_number(
            self.session_state.get(widget_key, value),
            value,
            prefer_float=isinstance(step, float),
        )
        current = _clamp_number(current, min_value, max_value)
        self.session_state[widget_key] = current
        self.elements.append(
            NumberInputElement(
                label=label,
                key=widget_key,
                value=current,
                min_value=min_value,
                max_value=max_value,
                step=step,
                disabled=disabled,
            )
        )
        if (
            not disabled
            and self.consume_changed_widget(widget_key)
            and on_change is not None
        ):
            on_change(*(args or ()), **(kwargs or {}))
        return current

    def selectbox(
        self,
        label: str,
        options: Any,
        index: int = 0,
        *,
        key: str | None = None,
        disabled: bool = False,
        on_change: Callable[..., Any] | None = None,
        args: tuple[Any, ...] | None = None,
        kwargs: dict[str, Any] | None = None,
    ) -> Any:
        return self._choice_widget(
            "selectbox",
            label,
            tuple(options),
            index,
            key=key,
            disabled=disabled,
            on_change=on_change,
            args=args,
            kwargs=kwargs,
        )

    def radio(
        self,
        label: str,
        options: Any,
        index: int = 0,
        *,
        key: str | None = None,
        disabled: bool = False,
        on_change: Callable[..., Any] | None = None,
        args: tuple[Any, ...] | None = None,
        kwargs: dict[str, Any] | None = None,
    ) -> Any:
        return self._choice_widget(
            "radio",
            label,
            tuple(options),
            index,
            key=key,
            disabled=disabled,
            on_change=on_change,
            args=args,
            kwargs=kwargs,
        )

    def _choice_widget(
        self,
        widget_type: str,
        label: str,
        options: tuple[Any, ...],
        index: int,
        *,
        key: str | None,
        disabled: bool,
        on_change: Callable[..., Any] | None,
        args: tuple[Any, ...] | None,
        kwargs: dict[str, Any] | None,
    ) -> Any:
        widget_key = self.next_widget_key(widget_type, label, key)
        if not options:
            self.session_state[widget_key] = None
            self.elements.append(
                AlertElement(
                    f"{widget_type} '{label}' requires at least one option.",
                    "error",
                )
            )
            return None
        safe_index = min(max(index, 0), len(options) - 1)
        current = self.session_state.get(widget_key, options[safe_index])
        if current not in options:
            current = options[safe_index]
        current_index = options.index(current)
        self.session_state[widget_key] = current
        element_cls = SelectboxElement if widget_type == "selectbox" else RadioElement
        self.elements.append(
            element_cls(
                label=label,
                key=widget_key,
                options=options,
                index=current_index,
                disabled=disabled,
            )
        )
        if (
            not disabled
            and self.consume_changed_widget(widget_key)
            and on_change is not None
        ):
            on_change(*(args or ()), **(kwargs or {}))
        return current

    def next_widget_key(
        self, widget_type: str, label: str, explicit_key: str | None = None
    ) -> str:
        call_id = (widget_type, label)
        index = self.widget_call_counts.get(call_id, 0)
        self.widget_call_counts[call_id] = index + 1
        if explicit_key is not None:
            widget_key = str(explicit_key)
            if widget_key in self.explicit_widget_keys_seen:
                raise DuplicateWidgetKeyError(
                    f'Duplicate widget key "{widget_key}". '
                    "Explicit widget keys must be unique within a single run."
                )
            self.explicit_widget_keys_seen.add(widget_key)
            return widget_key
        return f"{widget_type}:{label}:{index}"

    def press_button(self, key: str) -> None:
        self.pending_button_presses.add(key)
        self.last_focused_key = key

    def set_widget_value(self, key: str, value: Any) -> None:
        self.session_state[key] = value
        self.pending_changed_widgets.add(key)
        self.last_focused_key = key

    def consume_button_press(self, key: str) -> bool:
        if key not in self._active_button_presses:
            return False
        self._active_button_presses.remove(key)
        return True

    def consume_changed_widget(self, key: str) -> bool:
        if key not in self._active_changed_widgets:
            return False
        self._active_changed_widgets.remove(key)
        return True

    def _prepare_run(self) -> None:
        self.elements = []
        self.widget_call_counts = {}
        self.explicit_widget_keys_seen = set()
        self._active_button_presses = set(self.pending_button_presses)
        self._active_changed_widgets = set(self.pending_changed_widgets)
        self.pending_button_presses.clear()
        self.pending_changed_widgets.clear()

    def _push_script_dir(self) -> bool:
        script_dir = str(self.script_path.parent)
        if sys.path and sys.path[0] == script_dir:
            return False
        sys.path.insert(0, script_dir)
        return True

    def _pop_script_dir(self, path_added: bool) -> None:
        if not path_added:
            return
        script_dir = str(self.script_path.parent)
        if sys.path and sys.path[0] == script_dir:
            sys.path.pop(0)
            return
        try:
            sys.path.remove(script_dir)
        except ValueError:
            pass


def get_current_runtime() -> Runtime:
    runtime = _current_runtime.get()
    if runtime is None:
        raise RuntimeError("stui API calls must run inside `stui run`.")
    return runtime


def _normalize_progress(value: int | float) -> int:
    if not isinstance(value, int | float):
        raise TypeError("progress value must be an int or float.")
    if isinstance(value, float) and 0 <= value <= 1:
        percent = round(value * 100)
    else:
        percent = round(value)
    return max(0, min(100, percent))


def _coerce_number(
    value: Any,
    fallback: int | float = 0,
    *,
    prefer_float: bool = False,
) -> int | float:
    try:
        if (
            isinstance(fallback, int)
            and not isinstance(fallback, bool)
            and not prefer_float
        ):
            return int(value)
        return float(value)
    except (TypeError, ValueError):
        return fallback


def _clamp_number(
    value: int | float,
    min_value: int | float | None,
    max_value: int | float | None,
) -> int | float:
    if min_value is not None:
        value = max(value, min_value)
    if max_value is not None:
        value = min(value, max_value)
    return value


def _normalize_table(data: Any) -> tuple[tuple[str, ...], tuple[tuple[str, ...], ...]]:
    if hasattr(data, "to_dict") and hasattr(data, "columns"):
        return _normalize_table(data.to_dict(orient="records"))
    if isinstance(data, dict):
        if data and all(isinstance(value, (list, tuple)) for value in data.values()):
            headers = tuple(str(key) for key in data)
            max_len = max((len(value) for value in data.values()), default=0)
            rows = tuple(
                tuple(
                    str(data[key][row_index])
                    if row_index < len(data[key])
                    else ""
                    for key in data
                )
                for row_index in range(max_len)
            )
            return headers, rows
        return ("key", "value"), tuple(
            (str(key), str(value)) for key, value in data.items()
        )
    if isinstance(data, (list, tuple)):
        if not data:
            return ("value",), ()
        if all(isinstance(item, dict) for item in data):
            headers = tuple(dict.fromkeys(str(key) for row in data for key in row))
            rows = tuple(
                tuple(str(row.get(header, "")) for header in headers)
                for row in data
            )
            return headers, rows
        if all(isinstance(item, (list, tuple)) for item in data):
            width = max((len(item) for item in data), default=0)
            headers = tuple(f"col_{index + 1}" for index in range(width))
            rows = tuple(
                tuple(
                    str(item[index]) if index < len(item) else ""
                    for index in range(width)
                )
                for item in data
            )
            return headers, rows
        return ("value",), tuple((str(item),) for item in data)
    return ("value",), ((str(data),),)
