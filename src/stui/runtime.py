from __future__ import annotations

import contextvars
import runpy
import sys
import traceback
from collections.abc import Callable
from pathlib import Path
from typing import Any

from .elements import (
    AlertElement,
    ButtonElement,
    CheckboxElement,
    DividerElement,
    Element,
    ErrorElement,
    HeaderElement,
    MarkdownElement,
    SliderElement,
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

    def text(self, body: Any) -> None:
        self.elements.append(TextElement(str(body)))

    def markdown(self, body: Any) -> None:
        self.elements.append(MarkdownElement(str(body)))

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
        if self.consume_changed_widget(widget_key) and on_change is not None:
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
        if self.consume_changed_widget(widget_key) and on_change is not None:
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
        if self.consume_changed_widget(widget_key) and on_change is not None:
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
