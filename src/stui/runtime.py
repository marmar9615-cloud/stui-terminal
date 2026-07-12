from __future__ import annotations

import contextvars
import dataclasses as dataclasses_lib
import hashlib
import importlib
import importlib.util
import inspect
import json as json_lib
import math
import runpy
import sys
import textwrap
import threading
import traceback
import weakref
from collections.abc import Callable, Iterable, Sequence
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
    ColumnsElement,
    ContainerElement,
    DataTableElement,
    DividerElement,
    Element,
    ErrorElement,
    ExceptionElement,
    ExpanderElement,
    HeaderElement,
    HelpElement,
    JsonElement,
    LineChartElement,
    LineChartSeries,
    MarkdownElement,
    MetricElement,
    MultiselectElement,
    NumberInputElement,
    PathInputElement,
    ProgressElement,
    RadioElement,
    SelectboxElement,
    SliderElement,
    SpinnerElement,
    StatusElement,
    SubheaderElement,
    TableElement,
    TabsElement,
    TextElement,
    TextInputElement,
    TitleElement,
    ToggleElement,
    WriteElement,
)
from .path_input import (
    PATH_KINDS,
    PathKind,
    _normalize_extensions,
    _normalize_path,
    _normalize_root,
    _validation_error,
    _visible_path_text,
)
from .session_state import SessionState
from .widgets.slider import snap_value

_current_runtime: contextvars.ContextVar[Runtime | None] = contextvars.ContextVar(
    "stui_current_runtime", default=None
)
_SCRIPT_EXECUTION_LOCK = threading.RLock()
_PROCESS_ACTIVE_RUNTIME_LOCK = threading.RLock()
_process_active_runtime: Runtime | None = None
_PROCESS_MODULE_OWNERS: weakref.WeakKeyDictionary[
    object, weakref.ReferenceType[Any]
] = weakref.WeakKeyDictionary()
_MISSING = object()
_IGNORED_WATCH_PARTS = {
    ".git",
    ".hg",
    ".mypy_cache",
    ".nox",
    ".pytest_cache",
    ".ruff_cache",
    ".svn",
    ".tox",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
    "venv",
}

SourceSignature = tuple[int, int, int, bytes] | None
SourceChangeCallback = Callable[[frozenset[Path], int], None]


class RerunException(BaseException):
    """Internal signal used by st.rerun in later API slices."""


class StopException(BaseException):
    """Internal signal used by st.stop to end the current script pass."""


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


class StatusBlock(ElementBlock):
    pass


class SpinnerBlock(ElementBlock):
    pass


class Runtime:
    def __init__(self, script_path: str | Path) -> None:
        self.script_path = Path(script_path).resolve()
        self.project_root = _resolve_project_root(self.script_path)
        self.session_state = SessionState()
        self.elements: list[Element] = []
        self.toasts: list[str] = []
        self._element_stack: list[list[Element]] = [self.elements]
        self.widget_call_counts: dict[tuple[str, str], int] = {}
        self.widget_keys_seen: set[str] = set()
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
        self._form_rendered_widget_keys: dict[str, set[str]] = {}
        self._local_module_paths: dict[str, Path] = {}
        self._watched_source_signatures: dict[Path, SourceSignature] = {
            self.script_path: _source_signature(self.script_path)
        }
        self._source_change_callbacks: list[SourceChangeCallback] = []
        self._cache_registries: dict[object, dict[Any, Any]] = {}
        self.source_revision = 0

    def run_script(self) -> list[Element]:
        global _process_active_runtime

        with _SCRIPT_EXECUTION_LOCK:
            with _PROCESS_ACTIVE_RUNTIME_LOCK:
                previous_runtime = _process_active_runtime
                _process_active_runtime = self
            try:
                return self._run_script_locked()
            finally:
                with _PROCESS_ACTIVE_RUNTIME_LOCK:
                    _process_active_runtime = previous_runtime

    def _run_script_locked(self) -> list[Element]:
        initial_session_snapshot = self.session_state.snapshot()
        for _ in range(10):
            self._prepare_run()
            token = _current_runtime.set(self)
            sys_path_snapshot = self._push_script_dir()
            displaced_host_modules = self._evict_conflicting_local_modules()
            module_ownership_snapshot = self._snapshot_local_modules()
            session_snapshot = self.session_state.snapshot()
            try:
                runpy.run_path(str(self.script_path), run_name="__main__")
            except RerunException:
                continue
            except StopException:
                pass
            except DuplicateWidgetKeyError as exc:
                self.session_state.restore(session_snapshot)
                self.elements = [ErrorElement(str(exc))]
                self.toasts = []
            except ApiUsageError as exc:
                self.session_state.restore(session_snapshot)
                self.elements = [ErrorElement(str(exc))]
                self.toasts = []
            except Exception as exc:
                self.session_state.restore(session_snapshot)
                self._restore_committed_widget_values()
                self.elements = [
                    ErrorElement(
                        _format_script_exception(
                            exc,
                            self.script_path,
                            self.project_root,
                        )
                    )
                ]
                self.toasts = []
            finally:
                self._discover_local_modules(module_ownership_snapshot)
                self._restore_displaced_host_modules(displaced_host_modules)
                self._restore_sys_path(sys_path_snapshot)
                _current_runtime.reset(token)
            return self.elements

        self.session_state.restore(initial_session_snapshot)
        self.elements = [
            ErrorElement("stui stopped after 10 consecutive rerun requests.")
        ]
        return self.elements

    @property
    def watched_source_paths(self) -> tuple[Path, ...]:
        """Python source files currently tracked by watch mode."""
        return tuple(sorted(self._watched_source_signatures))

    def is_watchable_source(self, path: str | Path) -> bool:
        """Return whether *path* is local Python source suitable for watch mode."""
        candidate = Path(path).resolve()
        if candidate.suffix != ".py":
            return False
        try:
            relative = candidate.relative_to(self.project_root)
        except ValueError:
            return False
        return not any(_is_ignored_watch_part(part) for part in relative.parts)

    def poll_source_changes(self) -> tuple[Path, ...]:
        """Return coalesced local source changes since the previous poll."""
        changed: list[Path] = []
        for path, previous in tuple(self._watched_source_signatures.items()):
            current = _source_signature(path)
            if current == previous:
                continue
            self._watched_source_signatures[path] = current
            changed.append(path)
        return tuple(sorted(changed))

    def add_source_change_callback(self, callback: SourceChangeCallback) -> None:
        """Register an internal cache/runtime invalidation hook for source reloads."""
        self._source_change_callbacks.append(callback)

    def _get_cache_registry(
        self,
        namespace: object,
        *,
        create: bool = True,
    ) -> dict[Any, Any] | None:
        registry = self._cache_registries.get(namespace)
        if registry is None and create:
            registry = {}
            self._cache_registries[namespace] = registry
        return registry

    def _clear_cache_registry(self, namespace: object) -> None:
        registry = self._cache_registries.pop(namespace, None)
        if registry is not None:
            registry.clear()

    def prepare_source_reload(
        self,
        changed_paths: Iterable[str | Path],
    ) -> tuple[str, ...]:
        """Evict this app's imported modules before rerunning changed source."""
        with _SCRIPT_EXECUTION_LOCK:
            return self._prepare_source_reload_locked(changed_paths)

    def _prepare_source_reload_locked(
        self,
        changed_paths: Iterable[str | Path],
    ) -> tuple[str, ...]:
        changed = frozenset(Path(path).resolve() for path in changed_paths)
        if not changed:
            return ()

        evicted: list[str] = []
        for module_name in sorted(
            self._local_module_paths,
            key=lambda name: (name.count("."), name),
            reverse=True,
        ):
            module = sys.modules.get(module_name)
            if module is None:
                continue
            module_path = _module_source_path(module)
            if module_path is None or not self.is_watchable_source(module_path):
                continue
            sys.modules.pop(module_name, None)
            evicted.append(module_name)

        for source_path in self._local_module_paths.values():
            _remove_cached_bytecode(source_path)
        importlib.invalidate_caches()

        self.source_revision += 1
        for callback in tuple(self._source_change_callbacks):
            callback(changed, self.source_revision)
        return tuple(sorted(evicted))

    def _snapshot_local_modules(self) -> dict[str, object]:
        snapshot: dict[str, object] = {}
        for module_name, module in tuple(sys.modules.items()):
            if module_name == "stui" or module_name.startswith("stui."):
                continue
            module_path = _module_source_path(module)
            if module_path is None or not self.is_watchable_source(module_path):
                continue
            snapshot[module_name] = module
        return snapshot

    def _discover_local_modules(self, before_run: dict[str, object]) -> None:
        for module_name, module in tuple(sys.modules.items()):
            if module_name == "stui" or module_name.startswith("stui."):
                continue
            module_path = _module_source_path(module)
            if module_path is None or not self.is_watchable_source(module_path):
                continue
            if (
                module_name not in self._local_module_paths
                and before_run.get(module_name) is module
            ):
                continue
            self._local_module_paths[module_name] = module_path
            try:
                _PROCESS_MODULE_OWNERS[module] = weakref.ref(self)
            except TypeError:
                pass
            self._watched_source_signatures.setdefault(
                module_path,
                _source_signature(module_path),
            )

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
        text = json_lib.dumps(
            _json_display_value(obj),
            indent=2,
            sort_keys=True,
        )
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

    def status(
        self,
        label: Any,
        state: str = "running",
        expanded: bool = False,
    ) -> StatusBlock:
        children: list[Element] = []
        self._append_element(
            StatusElement(
                label=str(label),
                state=_normalize_status_state(state),
                expanded=bool(expanded),
                children=children,
            )
        )
        return StatusBlock(self, children)

    def spinner(self, text: Any = "Working...") -> SpinnerBlock:
        children: list[Element] = []
        self._append_element(SpinnerElement(text=str(text), children=children))
        return SpinnerBlock(self, children)

    def help(self, obj_or_text: Any) -> None:
        self._append_element(HelpElement(_format_help(obj_or_text)))

    def toast(self, body: Any) -> None:
        self.toasts.append(str(body))

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
                empty=not _has_chart_data(data),
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
                empty=not _has_line_chart_data(data),
            )
        )

    def table(
        self,
        data: Any,
        *,
        max_rows: int | None = None,
        max_cols: int | None = None,
    ) -> None:
        headers, rows = _normalize_table(data, max_rows=max_rows, max_cols=max_cols)
        self._append_element(TableElement(headers=headers, rows=rows))

    def dataframe(
        self,
        data: Any,
        *,
        max_rows: int | None = None,
        max_cols: int | None = None,
    ) -> None:
        self.table(data, max_rows=max_rows, max_cols=max_cols)

    def data_table(
        self,
        data: Any,
        *,
        selection_mode: str | None = None,
        key: str | None = None,
        disabled: bool = False,
        on_select: Callable[..., Any] | None = None,
        args: tuple[Any, ...] | None = None,
        kwargs: dict[str, Any] | None = None,
        max_rows: int | None = None,
        max_cols: int | None = None,
        height: int | None = None,
        show_index: bool = False,
    ) -> int | None:
        if selection_mode not in (None, "single"):
            raise ApiUsageError(
                'st.data_table selection_mode must be None or "single".'
            )
        row_limit = _normalize_data_table_limit(max_rows, "max_rows")
        col_limit = _normalize_data_table_limit(max_cols, "max_cols")
        normalized_height = _normalize_data_table_limit(height, "height")
        if not isinstance(show_index, bool):
            raise ApiUsageError("st.data_table show_index must be a bool.")

        widget_key = self.next_widget_key("data_table", "data", key)
        headers, source_rows = _normalize_table(data)
        source_row_count = len(source_rows)
        headers, limited_columns = _limit_table(
            headers,
            source_rows,
            max_rows=None,
            max_cols=col_limit,
        )
        visible_count = (
            len(limited_columns)
            if row_limit is None
            else min(row_limit, len(limited_columns))
        )
        source_row_indices = tuple(range(visible_count))
        rows = limited_columns[:visible_count]
        if show_index:
            headers = ("#", *headers)
            rows = tuple(
                (str(source_index), *row)
                for source_index, row in zip(source_row_indices, rows)
            )

        stored_value = self.session_state.get(widget_key)
        stored_is_valid = _is_valid_data_table_selection(
            stored_value,
            selection_mode=selection_mode,
            source_row_count=source_row_count,
        )
        stored = _normalize_data_table_selection(
            stored_value,
            selection_mode=selection_mode,
            source_row_count=source_row_count,
        )
        if not stored_is_valid and widget_key in self.session_state:
            self.session_state[widget_key] = None
        baseline = stored
        form_key = self._active_form_key()
        if form_key is not None and not disabled:
            pending_values = self.form_pending_values.get(form_key, {})
            if widget_key in pending_values and not _is_valid_data_table_selection(
                pending_values[widget_key],
                selection_mode=selection_mode,
                source_row_count=source_row_count,
            ):
                pending_values.pop(widget_key)
            baseline = _normalize_data_table_selection(
                pending_values.get(widget_key, stored),
                selection_mode=selection_mode,
                source_row_count=source_row_count,
            )
        raw_value = self._widget_value(widget_key, baseline, disabled=disabled)
        queued_change = not disabled and widget_key in self._active_changed_widgets
        valid_change = _is_valid_data_table_selection(
            raw_value,
            selection_mode=selection_mode,
            source_row_count=source_row_count,
        )
        current = (
            _normalize_data_table_selection(
                raw_value,
                selection_mode=selection_mode,
                source_row_count=source_row_count,
            )
            if valid_change
            else baseline
        )
        changed = self._finalize_widget_value(
            widget_key,
            current,
            disabled=disabled,
        )
        if queued_change and not valid_change:
            changed = False
        self._append_element(
            DataTableElement(
                headers=headers,
                rows=rows,
                source_row_indices=source_row_indices,
                source_row_count=source_row_count,
                hidden_rows=source_row_count - visible_count,
                key=widget_key,
                selected_index=current,
                selection_mode=selection_mode,
                disabled=disabled,
                height=normalized_height,
                show_index=show_index,
            )
        )
        self._handle_widget_callback(
            widget_key,
            changed,
            on_select,
            args,
            kwargs,
        )
        return current

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

    def columns(self, count: int) -> tuple[ElementBlock, ...]:
        if not isinstance(count, int) or isinstance(count, bool) or count < 1:
            raise ApiUsageError("st.columns(count) requires a positive integer count.")
        column_children: list[list[Element]] = [[] for _ in range(count)]
        self._append_element(ColumnsElement(column_children))
        return tuple(ElementBlock(self, children) for children in column_children)

    def tabs(
        self,
        labels: Sequence[str],
        *,
        key: str | None = None,
        default: int = 0,
        on_change: Callable[..., Any] | None = None,
        args: tuple[Any, ...] | None = None,
        kwargs: dict[str, Any] | None = None,
    ) -> tuple[ElementBlock, ...]:
        if isinstance(labels, (str, bytes)) or not isinstance(labels, Sequence):
            raise ApiUsageError(
                "st.tabs(labels) requires a non-empty sequence of non-empty strings."
            )
        tab_labels = tuple(labels)
        if not tab_labels or any(
            not isinstance(label, str) or not label.strip() for label in tab_labels
        ):
            raise ApiUsageError(
                "st.tabs(labels) requires a non-empty sequence of non-empty strings."
            )
        if (
            isinstance(default, bool)
            or not isinstance(default, int)
            or not 0 <= default < len(tab_labels)
        ):
            raise ApiUsageError(
                "st.tabs default must be an integer index between "
                f"0 and {len(tab_labels) - 1}."
            )
        tab_key = self.next_widget_key("tabs", repr(tab_labels), key)
        active = self._widget_value(
            tab_key,
            self.session_state.get(tab_key, default),
            disabled=False,
        )
        if (
            isinstance(active, bool)
            or not isinstance(active, int)
            or not 0 <= active < len(tab_labels)
        ):
            active = default
        changed = self._finalize_widget_value(tab_key, active, disabled=False)
        panes: list[list[Element]] = [[] for _ in tab_labels]
        self._append_element(
            TabsElement(
                labels=tab_labels,
                key=tab_key,
                active=active,
                panes=panes,
            )
        )
        self._handle_widget_callback(
            tab_key,
            changed,
            on_change,
            args,
            kwargs,
        )
        return tuple(ElementBlock(self, pane) for pane in panes)

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

    def path_input(
        self,
        label: str,
        value: str = "",
        *,
        root: str | Path | None = None,
        kind: PathKind = "any",
        must_exist: bool = False,
        extensions: str | Iterable[str] | None = None,
        browse: bool = True,
        key: str | None = None,
        disabled: bool = False,
        on_change: Callable[..., Any] | None = None,
        args: tuple[Any, ...] | None = None,
        kwargs: dict[str, Any] | None = None,
    ) -> str:
        if not isinstance(must_exist, bool):
            raise ApiUsageError("st.path_input must_exist must be a boolean.")
        if not isinstance(browse, bool):
            raise ApiUsageError("st.path_input browse must be a boolean.")
        if kind not in PATH_KINDS:
            raise ApiUsageError(
                "st.path_input kind must be 'file', 'directory', or 'any'."
            )
        try:
            normalized_extensions = _normalize_extensions(extensions)
        except ValueError as exc:
            raise ApiUsageError(
                "st.path_input extensions must contain file extensions."
            ) from exc

        label_text = _visible_path_text(label)
        normalized_root = _normalize_root(root, self.script_path.parent)
        widget_key = self.next_widget_key("path_input", label_text, key)
        pending_value = self._widget_value(
            widget_key,
            self.session_state.get(widget_key, value),
            disabled=disabled,
        )
        current = _normalize_path(pending_value, root=normalized_root)
        changed = self._finalize_widget_value(
            widget_key,
            current,
            disabled=disabled,
        )
        validation_error = _validation_error(
            current,
            kind=kind,
            must_exist=must_exist,
            extensions=normalized_extensions,
        )
        self._append_element(
            PathInputElement(
                label=label_text,
                key=widget_key,
                value=current,
                root=normalized_root,
                kind=kind,
                must_exist=must_exist,
                extensions=normalized_extensions,
                browse=browse,
                disabled=disabled,
                validation_error=validation_error,
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

    def toggle(
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
        widget_key = self.next_widget_key("toggle", label, key)
        current = bool(
            self._widget_value(
                widget_key,
                self.session_state.get(widget_key, value),
                disabled=disabled,
            )
        )
        changed = self._finalize_widget_value(widget_key, current, disabled=disabled)
        self._append_element(
            ToggleElement(
                label=label,
                key=widget_key,
                value=current,
                disabled=disabled,
            )
        )
        self._handle_widget_callback(widget_key, changed, on_change, args, kwargs)
        return current

    def multiselect(
        self,
        label: str,
        options: Any,
        default: Any = None,
        *,
        key: str | None = None,
        disabled: bool = False,
        on_change: Callable[..., Any] | None = None,
        args: tuple[Any, ...] | None = None,
        kwargs: dict[str, Any] | None = None,
    ) -> tuple[Any, ...]:
        options_tuple = tuple(options)
        if _has_duplicate_options(options_tuple):
            raise ApiUsageError(
                "st.multiselect options must not contain duplicates."
            )
        widget_key = self.next_widget_key("multiselect", label, key)
        default_selection = _normalize_multiselect_selection(default, options_tuple)
        current = _normalize_multiselect_selection(
            self._widget_value(
                widget_key,
                self.session_state.get(widget_key, default_selection),
                disabled=disabled,
            ),
            options_tuple,
        )
        changed = self._finalize_widget_value(widget_key, current, disabled=disabled)
        self._append_element(
            MultiselectElement(
                label=label,
                key=widget_key,
                options=options_tuple,
                selected=current,
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
            form_key = self._active_form_key()
            if form_key is None:
                self.session_state[widget_key] = None
            else:
                self._form_rendered_widget_keys.setdefault(form_key, set()).add(
                    widget_key
                )
                if not disabled:
                    self.form_pending_values.setdefault(form_key, {})[
                        widget_key
                    ] = None
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
        else:
            widget_key = f"{widget_type}:{label}:{index}"
        if widget_key in self.widget_keys_seen:
            raise DuplicateWidgetKeyError(
                f'Duplicate widget key "{widget_key}". '
                "Widget keys must be unique within a single run."
            )
        self.widget_keys_seen.add(widget_key)
        return widget_key

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
        if disabled:
            self.form_pending_values.get(form_key, {}).pop(key, None)
            return False
        self._form_rendered_widget_keys.setdefault(form_key, set()).add(key)
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
        rendered_keys = self._form_rendered_widget_keys.get(form_key, set())
        pending = {
            key: value
            for key, value in self.form_pending_values.pop(form_key, {}).items()
            if key in rendered_keys
        }
        changed_keys = []
        for key, value in pending.items():
            if self.session_state.get(key, _MISSING) != value:
                changed_keys.append(key)
            self.session_state[key] = value
            self._committed_widget_values[key] = value
        for key in changed_keys:
            if key in callbacks:
                callback, args, kwargs = callbacks[key]
                callback(*args, **kwargs)

    def _restore_committed_widget_values(self) -> None:
        for key, value in self._committed_widget_values.items():
            self.session_state[key] = value

    def _prepare_run(self) -> None:
        self.elements = []
        self.toasts = []
        self._element_stack = [self.elements]
        self.widget_call_counts = {}
        self.widget_keys_seen = set()
        self.explicit_widget_keys_seen = set()
        self.form_keys_seen = set()
        self.active_form_stack = []
        self._active_button_presses = set(self.pending_button_presses)
        self._active_changed_widgets = set(self.pending_changed_widgets)
        self._active_widget_values = dict(self.pending_widget_values)
        self._committed_widget_values = {}
        self._form_widget_callbacks = {}
        self._form_rendered_widget_keys = {}
        self.pending_button_presses.clear()
        self.pending_changed_widgets.clear()
        self.pending_widget_values.clear()

    def _push_script_dir(self) -> list[str]:
        sys_path_snapshot = list(sys.path)
        script_dir = str(self.script_path.parent)
        if sys.path and sys.path[0] == script_dir:
            return sys_path_snapshot
        sys.path.insert(0, script_dir)
        return sys_path_snapshot

    def _evict_conflicting_local_modules(self) -> dict[str, object]:
        """Prefer modules beside this app over same-named modules from another app."""
        import_roots = _local_import_roots(
            self.script_path.parent,
            self.project_root,
        )
        if not import_roots:
            return {}

        displaced_host_modules: dict[str, object] = {}
        for module_name, module in tuple(sys.modules.items()):
            root_name = module_name.partition(".")[0]
            local_locations = import_roots.get(root_name)
            if local_locations is None or root_name == "stui":
                continue
            module_path = _module_source_path(module)
            module_locations = _module_search_paths(module)
            if module_path is None and not module_locations:
                continue
            paths = (module_path,) if module_path is not None else module_locations
            if not any(
                _is_relative_to(path, local_location)
                for path in paths
                for local_location in local_locations
            ):
                owner_ref = _PROCESS_MODULE_OWNERS.get(module)
                if owner_ref is None or owner_ref() is None:
                    displaced_host_modules[module_name] = module
                sys.modules.pop(module_name, None)
        return displaced_host_modules

    def _restore_displaced_host_modules(
        self,
        displaced_host_modules: dict[str, object],
    ) -> None:
        """Restore pre-existing host modules after a local collision finishes."""
        if not displaced_host_modules:
            return

        displaced_roots = {
            module_name.partition(".")[0] for module_name in displaced_host_modules
        }
        for module_name, module in tuple(sys.modules.items()):
            if module_name.partition(".")[0] not in displaced_roots:
                continue
            owner_ref = _PROCESS_MODULE_OWNERS.get(module)
            if owner_ref is not None and owner_ref() is self:
                sys.modules.pop(module_name, None)
        sys.modules.update(displaced_host_modules)

    def _restore_sys_path(self, sys_path_snapshot: list[str]) -> None:
        sys.path[:] = sys_path_snapshot


def _is_ignored_watch_part(part: str) -> bool:
    return (
        part in _IGNORED_WATCH_PARTS
        or part.startswith(".venv")
        or part.endswith(".egg-info")
    )


def _resolve_project_root(script_path: Path) -> Path:
    for candidate in (script_path.parent, *script_path.parents):
        if (candidate / "pyproject.toml").is_file() or (candidate / ".git").exists():
            return candidate.resolve()
    return script_path.parent


def _local_import_roots(*search_paths: Path) -> dict[str, tuple[Path, ...]]:
    roots: dict[str, list[Path]] = {}
    for search_path in dict.fromkeys(path.resolve() for path in search_paths):
        try:
            children = tuple(search_path.iterdir())
        except OSError:
            continue

        for child in children:
            if child.is_file() and child.suffix == ".py":
                roots.setdefault(child.stem, []).append(child.resolve())
            elif child.is_dir() and _contains_local_python_source(child):
                roots.setdefault(child.name, []).append(child.resolve())
    return {name: tuple(locations) for name, locations in roots.items()}


def _contains_local_python_source(root: Path) -> bool:
    if _is_ignored_watch_part(root.name):
        return False
    try:
        candidates = root.rglob("*.py")
        return any(
            not any(
                _is_ignored_watch_part(part)
                for part in path.relative_to(root).parts
            )
            for path in candidates
        )
    except OSError:
        return False


def _module_search_paths(module: object) -> tuple[Path, ...]:
    raw_paths = getattr(module, "__path__", None)
    if raw_paths is None:
        return ()
    paths: list[Path] = []
    for raw_path in raw_paths:
        try:
            paths.append(Path(raw_path).resolve())
        except (OSError, TypeError):
            continue
    return tuple(paths)


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _module_source_path(module: object) -> Path | None:
    raw_path = getattr(module, "__file__", None)
    if not raw_path:
        return None
    path = Path(raw_path)
    if path.suffix in {".pyc", ".pyo"}:
        try:
            path = Path(importlib.util.source_from_cache(str(path)))
        except ValueError:
            return None
    if path.suffix != ".py":
        return None
    return path.resolve()


def _source_signature(path: Path) -> SourceSignature:
    try:
        stat_result = path.stat()
        digest = hashlib.blake2b(path.read_bytes(), digest_size=16).digest()
    except OSError:
        return None
    return (
        stat_result.st_mtime_ns,
        stat_result.st_size,
        stat_result.st_ino,
        digest,
    )


def _remove_cached_bytecode(source_path: Path) -> None:
    if source_path.suffix != ".py":
        return
    try:
        cache_path = Path(importlib.util.cache_from_source(str(source_path)))
        cache_path.unlink(missing_ok=True)
    except (OSError, ValueError):
        pass


def get_current_runtime() -> Runtime:
    runtime = _current_runtime.get()
    if runtime is None:
        raise RuntimeError("stui API calls must run inside `stui run`.")
    return runtime


def _get_process_active_runtime() -> Runtime | None:
    """Return the runtime that owns the currently serialized script run."""
    with _PROCESS_ACTIVE_RUNTIME_LOCK:
        return _process_active_runtime


def _format_script_exception(
    exc: BaseException,
    script_path: Path,
    project_root: Path | None = None,
) -> str:
    if isinstance(exc, FileNotFoundError):
        return f"FileNotFoundError: {exc}"
    if isinstance(exc, SyntaxError):
        return "".join(traceback.format_exception_only(type(exc), exc)).rstrip()

    extracted = traceback.extract_tb(exc.__traceback__)
    local_root = (project_root or script_path.parent).resolve()
    local_frames = []
    for frame in extracted:
        try:
            Path(frame.filename).resolve().relative_to(local_root)
        except (OSError, ValueError):
            continue
        local_frames.append(frame)
    frames = local_frames or list(extracted[-1:])
    rendered_frames = ["Traceback (most recent call last):\n"]
    rendered_frames.extend(traceback.format_list(frames))
    rendered_frames.extend(traceback.format_exception_only(type(exc), exc))
    return "".join(rendered_frames).rstrip()


def _json_display_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            str(key): _json_display_value(item)
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple, set)):
        return [_json_display_value(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def _normalize_progress(value: int | float) -> int:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise ApiUsageError("st.progress value must be an int or float.")
    if not math.isfinite(value):
        raise ApiUsageError("st.progress value must be finite.")
    if isinstance(value, float) and 0 <= value <= 1:
        percent = round(value * 100)
    else:
        percent = round(value)
    return max(0, min(100, percent))


def _normalize_status_state(state: str) -> str:
    normalized = str(state).strip().lower()
    if normalized not in {"running", "complete", "error"}:
        raise ApiUsageError(
            "st.status state must be one of: running, complete, error."
        )
    return normalized


def _format_help(obj_or_text: Any) -> str:
    if isinstance(obj_or_text, str):
        return obj_or_text

    lines: list[str] = []
    name = getattr(obj_or_text, "__qualname__", None) or getattr(
        obj_or_text,
        "__name__",
        None,
    )
    if name:
        try:
            signature = str(inspect.signature(obj_or_text))
        except (TypeError, ValueError):
            signature = ""
        lines.append(f"{name}{signature}")

    doc = inspect.getdoc(obj_or_text)
    if doc:
        lines.append(textwrap.dedent(doc).strip())

    if lines:
        return "\n\n".join(lines)
    return str(obj_or_text)


def _normalize_multiselect_selection(
    value: Any,
    options: tuple[Any, ...],
) -> tuple[Any, ...]:
    if value is None:
        items: tuple[Any, ...] = ()
    elif isinstance(value, (list, tuple, set, frozenset)):
        items = tuple(value)
    else:
        items = (value,)
    return tuple(option for option in options if option in items)


def _has_duplicate_options(options: tuple[Any, ...]) -> bool:
    for index, option in enumerate(options):
        for previous in options[:index]:
            try:
                if bool(option == previous):
                    return True
            except Exception:
                if option is previous:
                    return True
    return False


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
        raise ApiUsageError(f"st.{chart_name} {name} must be an int or None.")
    if value < 1:
        raise ApiUsageError(f"st.{chart_name} {name} must be a positive int or None.")
    return value


def _has_chart_data(data: Any) -> bool:
    return bool(_normalize_chart_points(data))


def _has_line_chart_data(data: Any) -> bool:
    series = _normalize_line_chart_series(data)
    return any(any(_is_number(value) for value in item.values) for item in series)


def _normalize_chart_points(data: Any) -> tuple[BarChartPoint, ...]:
    if _is_number(data):
        return (BarChartPoint("value", float(data)),)
    if isinstance(data, dict):
        points = [
            BarChartPoint(str(key), float(value))
            for key, value in data.items()
            if _is_number(value)
        ]
        return tuple(points) or _chart_points_from_column_dict(data)
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
        pair_points = tuple(
            point
            for point in (_chart_point_from_pair(item) for item in data)
            if point is not None
        )
        if pair_points:
            return pair_points
    return ()


def _normalize_line_chart_series(data: Any) -> tuple[LineChartSeries, ...]:
    if _is_number(data):
        return (LineChartSeries("value", (float(data),)),)
    if isinstance(data, dict):
        column_series = _line_series_from_column_dict(data)
        if column_series:
            return column_series
        series = [
            LineChartSeries(str(key), _numeric_values(value))
            for key, value in data.items()
        ]
        return tuple(item for item in series if item.values)
    if isinstance(data, (list, tuple)) and all(isinstance(item, dict) for item in data):
        row_series = _line_series_from_rows(data)
        if row_series:
            return row_series
    if isinstance(data, (list, tuple)):
        pair_values = _numeric_values_from_pairs(data)
        if pair_values:
            return (LineChartSeries("value", pair_values),)
    values = _numeric_values(data)
    if values:
        return (LineChartSeries("value", values),)
    return ()


def _numeric_values(data: Any) -> tuple[float, ...]:
    if _is_number(data):
        return (float(data),)
    if isinstance(data, (list, tuple)):
        return tuple(float(value) for value in data if _is_number(value))
    return ()


def _is_sequence(value: Any) -> bool:
    return isinstance(value, (list, tuple))


def _chart_point_from_pair(item: Any) -> BarChartPoint | None:
    if not _is_sequence(item) or len(item) < 2:
        return None
    label, value = item[0], item[1]
    if not _is_number(value):
        return None
    return BarChartPoint(str(label), float(value))


def _chart_points_from_column_dict(data: dict[Any, Any]) -> tuple[BarChartPoint, ...]:
    value_column = _first_column(data, ("value", "score", "count", "total", "y"))
    if value_column is None:
        return ()
    label_column = _first_column(data, ("label", "name", "key", "category", "x"))
    points = []
    for index, value in enumerate(value_column):
        if not _is_number(value):
            continue
        label = (
            str(label_column[index])
            if label_column is not None and index < len(label_column)
            else str(index)
        )
        points.append(BarChartPoint(label, float(value)))
    return tuple(points)


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


def _line_series_from_rows(
    rows: list[Any] | tuple[Any, ...],
) -> tuple[LineChartSeries, ...]:
    numeric_keys = list(
        dict.fromkeys(
            key
            for row in rows
            for key, value in row.items()
            if _is_number(value)
        )
    )
    if len(numeric_keys) > 1:
        numeric_keys = [
            key
            for key in numeric_keys
            if str(key).lower() not in {"x", "step", "index"}
        ] or numeric_keys
    series = []
    for key in numeric_keys:
        values = tuple(
            float(row[key])
            for row in rows
            if key in row and _is_number(row[key])
        )
        if values:
            series.append(LineChartSeries(str(key), values))
    return tuple(series)


def _line_series_from_column_dict(data: dict[Any, Any]) -> tuple[LineChartSeries, ...]:
    sequence_keys = [key for key, value in data.items() if _is_sequence(value)]
    if not sequence_keys:
        return ()
    numeric_keys = [
        key
        for key in sequence_keys
        if any(_is_number(value) for value in data[key])
    ]
    if len(numeric_keys) > 1:
        numeric_keys = [
            key
            for key in numeric_keys
            if str(key).lower() not in {"x", "step", "index"}
        ] or numeric_keys
    return tuple(
        LineChartSeries(str(key), _numeric_values(data[key]))
        for key in numeric_keys
        if _numeric_values(data[key])
    )


def _numeric_values_from_pairs(data: list[Any] | tuple[Any, ...]) -> tuple[float, ...]:
    values = []
    for item in data:
        if _is_sequence(item) and len(item) >= 2 and _is_number(item[1]):
            values.append(float(item[1]))
    return tuple(values)


def _first_column(
    data: dict[Any, Any],
    preferred_keys: tuple[str, ...],
) -> list[Any] | tuple[Any, ...] | None:
    for preferred_key in preferred_keys:
        for key, value in data.items():
            if str(key).lower() == preferred_key and _is_sequence(value):
                return value
    return None


def _is_number(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )


def _normalize_table(
    data: Any,
    *,
    max_rows: int | None = None,
    max_cols: int | None = None,
) -> tuple[tuple[str, ...], tuple[tuple[str, ...], ...]]:
    if hasattr(data, "to_dict") and hasattr(data, "columns"):
        records = data.to_dict(orient="records")
        columns = tuple(getattr(data, "columns", ()))
        if isinstance(records, list) and all(isinstance(row, dict) for row in records):
            return _normalize_records_table(
                records,
                declared_columns=columns,
                max_rows=max_rows,
                max_cols=max_cols,
            )
        return _normalize_table(records, max_rows=max_rows, max_cols=max_cols)
    if isinstance(data, dict):
        if data and all(isinstance(value, (list, tuple)) for value in data.values()):
            headers = tuple(str(key) for key in data)
            max_len = max((len(value) for value in data.values()), default=0)
            rows = tuple(
                tuple(
                    _table_cell_text(data[key][row_index])
                    if row_index < len(data[key])
                    else ""
                    for key in data
                )
                for row_index in range(max_len)
            )
            return _limit_table(headers, rows, max_rows=max_rows, max_cols=max_cols)
        headers, rows = ("key", "value"), tuple(
            (_table_cell_text(key), _table_cell_text(value))
            for key, value in data.items()
        )
        return _limit_table(headers, rows, max_rows=max_rows, max_cols=max_cols)
    if isinstance(data, (list, tuple)):
        if not data:
            return _limit_table(("value",), (), max_rows=max_rows, max_cols=max_cols)
        records = tuple(_table_record(item) for item in data)
        if all(record is not None for record in records):
            return _normalize_records_table(
                records,
                max_rows=max_rows,
                max_cols=max_cols,
            )
        if all(isinstance(item, (list, tuple)) for item in data):
            width = max((len(item) for item in data), default=0)
            headers = tuple(f"col_{index + 1}" for index in range(width))
            rows = tuple(
                tuple(
                    _table_cell_text(item[index]) if index < len(item) else ""
                    for index in range(width)
                )
                for item in data
            )
            return _limit_table(headers, rows, max_rows=max_rows, max_cols=max_cols)
        headers, rows = ("value",), tuple((_table_cell_text(item),) for item in data)
        return _limit_table(headers, rows, max_rows=max_rows, max_cols=max_cols)
    return _limit_table(
        ("value",),
        ((_table_cell_text(data),),),
        max_rows=max_rows,
        max_cols=max_cols,
    )


def _normalize_table_limit(value: int | None, name: str) -> int | None:
    if value is None:
        return None
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise ApiUsageError(f"st.table {name} must be a positive integer or None.")
    return value


def _normalize_data_table_limit(value: int | None, name: str) -> int | None:
    if value is None:
        return None
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise ApiUsageError(f"st.data_table {name} must be a positive integer or None.")
    return value


def _is_valid_data_table_selection(
    value: Any,
    *,
    selection_mode: str | None,
    source_row_count: int,
) -> bool:
    if value is None:
        return True
    return (
        selection_mode == "single"
        and isinstance(value, int)
        and not isinstance(value, bool)
        and 0 <= value < source_row_count
    )


def _normalize_data_table_selection(
    value: Any,
    *,
    selection_mode: str | None,
    source_row_count: int,
) -> int | None:
    if not _is_valid_data_table_selection(
        value,
        selection_mode=selection_mode,
        source_row_count=source_row_count,
    ):
        return None
    return value


def _normalize_records_table(
    records: list[Any] | tuple[Any, ...],
    *,
    declared_columns: tuple[Any, ...] = (),
    max_rows: int | None,
    max_cols: int | None,
) -> tuple[tuple[str, ...], tuple[tuple[str, ...], ...]]:
    keys = tuple(
        dict.fromkeys(
            (
                *declared_columns,
                *(key for row in records for key in row),
            )
        )
    )
    headers = tuple(str(key) for key in keys)
    rows = tuple(
        tuple(_table_cell_text(row.get(key, "")) for key in keys)
        for row in records
    )
    if not headers:
        headers = ("value",)
    return _limit_table(headers, rows, max_rows=max_rows, max_cols=max_cols)


def _limit_table(
    headers: tuple[str, ...],
    rows: tuple[tuple[str, ...], ...],
    *,
    max_rows: int | None,
    max_cols: int | None,
) -> tuple[tuple[str, ...], tuple[tuple[str, ...], ...]]:
    row_limit = _normalize_table_limit(max_rows, "max_rows")
    col_limit = _normalize_table_limit(max_cols, "max_cols")
    if not headers and not any(row for row in rows):
        headers = ("value",)
    column_count = max(
        1,
        len(headers),
        max((len(row) for row in rows), default=0),
    )
    if len(headers) < column_count:
        headers = (
            *headers,
            *(
                f"col_{index + 1}"
                for index in range(len(headers), column_count)
            ),
        )
    rows = tuple(
        (
            *row[:column_count],
            *("" for _ in range(column_count - len(row))),
        )
        for row in rows
    )
    original_header_count = len(headers)
    original_row_count = len(rows)
    if col_limit is not None:
        visible_headers = headers[:col_limit]
        hidden_count = max(0, original_header_count - len(visible_headers))
        headers = visible_headers
        rows = tuple(row[:col_limit] for row in rows)
        if hidden_count:
            headers = (*headers, "...")
            rows = tuple((*row, f"+{hidden_count} cols") for row in rows)
    if row_limit is not None:
        visible_rows = rows[:row_limit]
        hidden_count = max(0, original_row_count - len(visible_rows))
        rows = visible_rows
        if hidden_count:
            rows = (*rows, (f"+{hidden_count} rows", *("" for _ in headers[1:])))
    return headers, rows


def _table_record(value: Any) -> dict[Any, Any] | None:
    if isinstance(value, dict):
        return value
    if dataclasses_lib.is_dataclass(value) and not isinstance(value, type):
        return dataclasses_lib.asdict(value)
    asdict = getattr(value, "_asdict", None)
    if callable(asdict):
        record = asdict()
        if isinstance(record, dict):
            return record
    attributes = getattr(value, "__dict__", None)
    if isinstance(attributes, dict):
        public = {
            key: item
            for key, item in attributes.items()
            if not str(key).startswith("_") and not callable(item)
        }
        if public:
            return public
    return None


def _table_cell_text(value: Any) -> str:
    text = str(value)
    text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\t", "    ")
    if "\n" in text:
        return " / ".join(part.strip() for part in text.split("\n"))
    return text
