from __future__ import annotations

import contextvars
import json as json_lib
import math
import runpy
import sys
import traceback
from collections.abc import Callable
from pathlib import Path
from typing import Any

from .elements import (
    AlertElement,
    BarChartElement,
    BarChartPoint,
    ButtonElement,
    CaptionElement,
    CheckboxElement,
    CodeElement,
    ContainerElement,
    DividerElement,
    Element,
    ErrorElement,
    ExceptionElement,
    ExpanderElement,
    HeaderElement,
    JsonElement,
    LineChartElement,
    LineChartSeries,
    MarkdownElement,
    MetricElement,
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
_MISSING = object()


class RerunException(Exception):
    """Internal signal used by st.rerun in later API slices."""


class DuplicateWidgetKeyError(Exception):
    """Raised when a script reuses an explicit widget key in one run."""


class ApiUsageError(Exception):
    """Raised for user-facing API misuse that should render without a traceback."""


class Form:
    def __init__(self, runtime: Runtime, key: str) -> None:
        self.runtime = runtime
        self.key = key

    def __enter__(self) -> Form:
        self.runtime.enter_form(self.key)
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> bool:
        self.runtime.exit_form(self.key)
        return False


class ElementBlock:
    def __init__(self, runtime: Runtime, children: list[Element]) -> None:
        self.runtime = runtime
        self.children = children

    def __enter__(self) -> ElementBlock:
        self.runtime._push_element_block(self.children)
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> bool:
        self.runtime._pop_element_block(self.children)
        return False


class Runtime:
    def __init__(self, script_path: str | Path) -> None:
        self.script_path = Path(script_path).resolve()
        self.session_state = SessionState()
        self.elements: list[Element] = []
        self._element_stack: list[list[Element]] = [self.elements]
        self.widget_call_counts: dict[tuple[str, str], int] = {}
        self.explicit_widget_keys_seen: set[str] = set()
        self.form_keys_seen: set[str] = set()
        self.active_form_stack: list[str] = []
        self.form_pending_values: dict[str, dict[str, Any]] = {}
        self.pending_button_presses: set[str] = set()
        self.pending_changed_widgets: set[str] = set()
        self.pending_widget_values: dict[str, Any] = {}
        self.last_focused_key: str | None = None
        self._active_button_presses: set[str] = set()
        self._active_changed_widgets: set[str] = set()
        self._active_widget_values: dict[str, Any] = {}
        self._committed_widget_values: dict[str, Any] = {}
        self._form_widget_callbacks: dict[
            str, dict[str, tuple[Callable[..., Any], tuple[Any, ...], dict[str, Any]]]
        ] = {}

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
                self._restore_committed_widget_values()
                self.elements = [ErrorElement(str(exc))]
            except ApiUsageError as exc:
                self.session_state.restore(session_snapshot)
                self._restore_committed_widget_values()
                self.elements = [ErrorElement(str(exc))]
            except Exception:
                self.session_state.restore(session_snapshot)
                self._restore_committed_widget_values()
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
        self._append_element(TitleElement(str(body), key=key))

    def header(self, body: Any, *, key: str | None = None) -> None:
        self._append_element(HeaderElement(str(body), key=key))

    def subheader(self, body: Any, *, key: str | None = None) -> None:
        self._append_element(SubheaderElement(str(body), key=key))

    def text(self, body: Any) -> None:
        self._append_element(TextElement(str(body)))

    def caption(self, body: Any) -> None:
        self._append_element(CaptionElement(str(body)))

    def markdown(self, body: Any) -> None:
        self._append_element(MarkdownElement(str(body)))

    def code(self, body: Any, language: str | None = None) -> None:
        self._append_element(CodeElement(str(body), language=language))

    def json(self, obj: Any) -> None:
        text = json_lib.dumps(obj, indent=2, sort_keys=True, default=str)
        self._append_element(JsonElement(obj=obj, text=text))

    def exception(self, exc: BaseException) -> None:
        rendered = "".join(
            traceback.format_exception(type(exc), exc, exc.__traceback__)
        )
        self._append_element(ExceptionElement(rendered))

    def progress(self, value: int | float, text: Any | None = None) -> None:
        label = None if text is None else str(text)
        self._append_element(
            ProgressElement(_normalize_progress(value), label)
        )

    def metric(self, label: Any, value: Any, delta: Any | None = None) -> None:
        delta_text = None if delta is None else str(delta)
        self._append_element(MetricElement(str(label), str(value), delta_text))

    def bar_chart(
        self,
        data: Any,
        *,
        width: int | None = None,
        height: int | None = None,
    ) -> None:
        self._append_element(
            BarChartElement(
                points=_normalize_chart_points(data),
                width=_normalize_optional_size(width, "width"),
                height=_normalize_optional_size(height, "height"),
            )
        )

    def line_chart(
        self,
        data: Any,
        *,
        width: int | None = None,
        height: int | None = None,
    ) -> None:
        self._append_element(
            LineChartElement(
                series=_normalize_line_chart_series(data),
                width=_normalize_optional_size(width, "width", "line_chart"),
                height=_normalize_optional_size(height, "height", "line_chart"),
            )
        )

    def table(self, data: Any) -> None:
        headers, rows = _normalize_table(data)
        self._append_element(TableElement(headers=headers, rows=rows))

    def dataframe(self, data: Any) -> None:
        self.table(data)

    def divider(self) -> None:
        self._append_element(DividerElement())

    def success(self, body: Any) -> None:
        self._append_element(AlertElement(str(body), "success"))

    def info(self, body: Any) -> None:
        self._append_element(AlertElement(str(body), "info"))

    def warning(self, body: Any) -> None:
        self._append_element(AlertElement(str(body), "warning"))

    def error(self, body: Any) -> None:
        self._append_element(AlertElement(str(body), "error"))

    def write(self, *args: Any) -> None:
        text = " ".join(str(arg) for arg in args)
        self._append_element(WriteElement(tuple(args), text))

    def container(self) -> ElementBlock:
        children: list[Element] = []
        self._append_element(ContainerElement(children))
        return ElementBlock(self, children)

    def expander(
        self,
        label: str,
        expanded: bool = False,
        *,
        key: str | None = None,
    ) -> ElementBlock:
        expander_label = str(label)
        expander_key = self.next_widget_key("expander", expander_label, key)
        current = bool(
            self._changed_widget_value(
                expander_key,
                self.session_state.get(expander_key, expanded),
                disabled=False,
            )
        )
        self.session_state[expander_key] = current
        self._remember_committed_widget_value(expander_key, current, disabled=False)
        children: list[Element] = []
        self._append_element(
            ExpanderElement(
                label=expander_label,
                key=expander_key,
                expanded=current,
                children=children,
            )
        )
        return ElementBlock(self, children)

    def form(self, key: str) -> Form:
        return Form(self, str(key))

    def form_submit_button(
        self,
        label: str = "Submit",
        *,
        disabled: bool = False,
        on_click: Callable[..., Any] | None = None,
        args: tuple[Any, ...] | None = None,
        kwargs: dict[str, Any] | None = None,
    ) -> bool:
        if not self.active_form_stack:
            raise ApiUsageError(
                "st.form_submit_button must be used inside st.form(...)."
            )
        form_key = self.active_form_stack[-1]
        widget_key = self.next_widget_key(
            "form_submit_button",
            f"{form_key}:{label}",
        )
        pressed = False if disabled else self.consume_button_press(widget_key)
        self._append_element(
            ButtonElement(label=label, key=widget_key, disabled=disabled)
        )
        if pressed:
            self._commit_form(form_key)
            if on_click is not None:
                on_click(*(args or ()), **(kwargs or {}))
        return pressed

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
        self._append_element(
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
        current = self._widget_value(
            widget_key,
            self.session_state.get(widget_key, default),
            disabled=disabled,
        )
        snapped = snap_value(current, min_value, max_value, step)
        changed = self._finalize_widget_value(widget_key, snapped, disabled=disabled)
        self._append_element(
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
        self._handle_widget_callback(widget_key, changed, on_change, args, kwargs)
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
        current = str(
            self._widget_value(
                widget_key,
                self.session_state.get(widget_key, value),
                disabled=disabled,
            )
        )
        changed = self._finalize_widget_value(widget_key, current, disabled=disabled)
        self._append_element(
            TextInputElement(
                label=label,
                key=widget_key,
                value=current,
                placeholder=placeholder,
                disabled=disabled,
            )
        )
        self._handle_widget_callback(widget_key, changed, on_change, args, kwargs)
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
        current = bool(
            self._widget_value(
                widget_key,
                self.session_state.get(widget_key, value),
                disabled=disabled,
            )
        )
        changed = self._finalize_widget_value(widget_key, current, disabled=disabled)
        self._append_element(
            CheckboxElement(
                label=label,
                key=widget_key,
                value=current,
                disabled=disabled,
            )
        )
        self._handle_widget_callback(widget_key, changed, on_change, args, kwargs)
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
            self._widget_value(
                widget_key,
                self.session_state.get(widget_key, value),
                disabled=disabled,
            ),
            value,
            prefer_float=isinstance(step, float),
        )
        current = _clamp_number(current, min_value, max_value)
        changed = self._finalize_widget_value(widget_key, current, disabled=disabled)
        self._append_element(
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
        self._handle_widget_callback(widget_key, changed, on_change, args, kwargs)
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
            self._append_element(
                AlertElement(
                    f"{widget_type} '{label}' requires at least one option.",
                    "error",
                )
            )
            return None
        safe_index = min(max(index, 0), len(options) - 1)
        current = self._widget_value(
            widget_key,
            self.session_state.get(widget_key, options[safe_index]),
            disabled=disabled,
        )
        if current not in options:
            current = options[safe_index]
        current_index = options.index(current)
        changed = self._finalize_widget_value(widget_key, current, disabled=disabled)
        element_cls = SelectboxElement if widget_type == "selectbox" else RadioElement
        self._append_element(
            element_cls(
                label=label,
                key=widget_key,
                options=options,
                index=current_index,
                disabled=disabled,
            )
        )
        self._handle_widget_callback(widget_key, changed, on_change, args, kwargs)
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

    def enter_form(self, key: str) -> None:
        if self.active_form_stack:
            raise ApiUsageError("Nested st.form blocks are not supported.")
        if key in self.form_keys_seen:
            raise DuplicateWidgetKeyError(
                f'Duplicate form key "{key}". '
                "Form keys must be unique within a single run."
            )
        self.form_keys_seen.add(key)
        self.active_form_stack.append(key)

    def exit_form(self, key: str) -> None:
        if self.active_form_stack and self.active_form_stack[-1] == key:
            self.active_form_stack.pop()

    def _append_element(self, element: Element) -> None:
        self._element_stack[-1].append(element)

    def _push_element_block(self, children: list[Element]) -> None:
        self._element_stack.append(children)

    def _pop_element_block(self, children: list[Element]) -> None:
        if self._element_stack and self._element_stack[-1] is children:
            self._element_stack.pop()

    def press_button(self, key: str) -> None:
        self.pending_button_presses.add(key)
        self.last_focused_key = key

    def set_widget_value(self, key: str, value: Any) -> None:
        self.pending_widget_values[key] = value
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

    def _changed_widget_value(
        self,
        key: str,
        current: Any,
        *,
        disabled: bool,
    ) -> Any:
        if disabled or key not in self._active_changed_widgets:
            return current
        return self._active_widget_values.get(key, current)

    def _widget_value(
        self,
        key: str,
        current: Any,
        *,
        disabled: bool,
    ) -> Any:
        form_key = self._active_form_key()
        if form_key is None:
            return self._changed_widget_value(key, current, disabled=disabled)
        if disabled:
            return current
        if key in self._active_changed_widgets:
            return self._active_widget_values.get(key, current)
        return self.form_pending_values.get(form_key, {}).get(key, current)

    def _finalize_widget_value(
        self,
        key: str,
        value: Any,
        *,
        disabled: bool,
    ) -> bool:
        changed = not disabled and self.consume_changed_widget(key)
        form_key = self._active_form_key()
        if form_key is None:
            self.session_state[key] = value
            if changed:
                self._committed_widget_values[key] = value
            return changed
        if changed:
            self.form_pending_values.setdefault(form_key, {})[key] = value
        return changed

    def _handle_widget_callback(
        self,
        key: str,
        changed: bool,
        callback: Callable[..., Any] | None,
        args: tuple[Any, ...] | None,
        kwargs: dict[str, Any] | None,
    ) -> None:
        if callback is None:
            return
        form_key = self._active_form_key()
        if form_key is not None:
            self._form_widget_callbacks.setdefault(form_key, {})[key] = (
                callback,
                args or (),
                kwargs or {},
            )
            return
        if changed:
            callback(*(args or ()), **(kwargs or {}))

    def _remember_committed_widget_value(
        self,
        key: str,
        value: Any,
        *,
        disabled: bool,
    ) -> None:
        if not disabled and key in self._active_changed_widgets:
            self._committed_widget_values[key] = value

    def _active_form_key(self) -> str | None:
        if not self.active_form_stack:
            return None
        return self.active_form_stack[-1]

    def _commit_form(self, form_key: str) -> None:
        callbacks = self._form_widget_callbacks.get(form_key, {})
        for key, value in self.form_pending_values.pop(form_key, {}).items():
            previous = self.session_state.get(key, _MISSING)
            self.session_state[key] = value
            self._committed_widget_values[key] = value
            if previous != value and key in callbacks:
                callback, args, kwargs = callbacks[key]
                callback(*args, **kwargs)

    def _restore_committed_widget_values(self) -> None:
        for key, value in self._committed_widget_values.items():
            self.session_state[key] = value

    def _prepare_run(self) -> None:
        self.elements = []
        self._element_stack = [self.elements]
        self.widget_call_counts = {}
        self.explicit_widget_keys_seen = set()
        self.form_keys_seen = set()
        self.active_form_stack = []
        self._active_button_presses = set(self.pending_button_presses)
        self._active_changed_widgets = set(self.pending_changed_widgets)
        self._active_widget_values = dict(self.pending_widget_values)
        self._committed_widget_values = {}
        self._form_widget_callbacks = {}
        self.pending_button_presses.clear()
        self.pending_changed_widgets.clear()
        self.pending_widget_values.clear()

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


def _normalize_optional_size(
    value: int | None,
    name: str,
    chart_name: str = "bar_chart",
) -> int | None:
    if value is None:
        return None
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError(f"{chart_name} {name} must be an int or None.")
    return max(1, value)


def _normalize_chart_points(data: Any) -> tuple[BarChartPoint, ...]:
    if _is_number(data):
        return (BarChartPoint("value", float(data)),)
    if isinstance(data, dict):
        points = [
            BarChartPoint(str(key), float(value))
            for key, value in data.items()
            if _is_number(value)
        ]
        return tuple(points) or (BarChartPoint("value", 0.0),)
    if isinstance(data, (list, tuple)):
        if not data:
            return ()
        numeric_items = [
            (index, item) for index, item in enumerate(data) if _is_number(item)
        ]
        if numeric_items:
            return tuple(
                BarChartPoint(str(index), float(value))
                for index, value in numeric_items
            )
        if all(isinstance(item, dict) for item in data):
            points = tuple(
                _chart_point_from_row(index, row)
                for index, row in enumerate(data)
            )
            return tuple(point for point in points if point is not None)
    return (BarChartPoint("value", 0.0),)


def _normalize_line_chart_series(data: Any) -> tuple[LineChartSeries, ...]:
    if _is_number(data):
        return (LineChartSeries("value", (float(data),)),)
    if isinstance(data, dict):
        series = [
            LineChartSeries(str(key), _numeric_values(value))
            for key, value in data.items()
        ]
        return tuple(item for item in series if item.values) or (
            LineChartSeries("value", (0.0,)),
        )
    values = _numeric_values(data)
    if values:
        return (LineChartSeries("value", values),)
    return (LineChartSeries("value", (0.0,)),)


def _numeric_values(data: Any) -> tuple[float, ...]:
    if _is_number(data):
        return (float(data),)
    if isinstance(data, (list, tuple)):
        return tuple(float(value) for value in data if _is_number(value))
    return ()


def _chart_point_from_row(index: int, row: dict[Any, Any]) -> BarChartPoint | None:
    numeric_items = [(key, value) for key, value in row.items() if _is_number(value)]
    if not numeric_items:
        return None
    label = _chart_label_from_row(index, row)
    value = _chart_value_from_row(row, numeric_items)
    return BarChartPoint(label, float(value))


def _chart_label_from_row(index: int, row: dict[Any, Any]) -> str:
    for preferred_key in ("label", "name", "key", "category"):
        value = row.get(preferred_key)
        if value is not None and not _is_number(value):
            return str(value)
    for value in row.values():
        if not _is_number(value):
            return str(value)
    numeric_items = [(key, value) for key, value in row.items() if _is_number(value)]
    if len(numeric_items) == 1:
        return str(numeric_items[0][0])
    return str(index)


def _chart_value_from_row(
    row: dict[Any, Any],
    numeric_items: list[tuple[Any, Any]],
) -> Any:
    for preferred_key in ("value", "score", "count", "total", "y"):
        value = row.get(preferred_key)
        if _is_number(value):
            return value
    return numeric_items[-1][1]


def _is_number(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )


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
