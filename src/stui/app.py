from __future__ import annotations

import hashlib
import math
import os

from rich.json import JSON as RichJSON
from rich.markdown import Markdown
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table as RichTable
from rich.text import Text
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.css.query import NoMatches
from textual.message import Message
from textual.widgets import (
    Button,
    Checkbox,
    Footer,
    Header,
    Input,
    ProgressBar,
    Static,
)

from .elements import (
    AlertElement,
    BarChartElement,
    ButtonElement,
    CaptionElement,
    CheckboxElement,
    CodeElement,
    ColumnsElement,
    ContainerElement,
    DividerElement,
    ErrorElement,
    ExceptionElement,
    ExpanderElement,
    HeaderElement,
    HelpElement,
    JsonElement,
    LineChartElement,
    MarkdownElement,
    MetricElement,
    NumberInputElement,
    ProgressElement,
    RadioElement,
    SelectboxElement,
    SliderElement,
    SpinnerElement,
    StatusElement,
    SubheaderElement,
    TableElement,
    TextElement,
    TextInputElement,
    TitleElement,
    WriteElement,
)
from .runtime import Runtime
from .widgets.slider import StuiSlider

SUPPORTED_THEMES = {"default", "high-contrast"}
MAX_WIDGET_LABEL_WIDTH = 72
MAX_STATIC_LABEL_WIDTH = 120
MAX_TABLE_COLUMNS = 8
MIN_TABLE_COLUMN_WIDTH = 6
MAX_TABLE_COLUMN_WIDTH = 24
MIN_RENDERED_COLUMN_WIDTH = 28

HIGH_CONTRAST_CSS = """
    Screen {
        background: #000000;
        color: #ffffff;
    }

    Header, Footer {
        background: #000000;
        color: #ffffff;
    }

    .title, .header, .subheader {
        color: #ffff00;
    }

    .caption, .stui-field-label, .stui-progress-label {
        color: #ffffff;
    }

    .divider {
        color: #ffffff;
    }

    Button {
        border: tall #ffffff;
    }

    Button:focus {
        background: #ffff00;
        color: #000000;
        text-style: bold;
    }

    Input:focus, .stui-selectbox:focus, .stui-radio:focus {
        border: tall #ffff00;
        background: #000000;
        color: #ffffff;
    }

    Checkbox:focus, .stui-slider:focus {
        border: tall #ffff00;
        background: #000000;
        color: #ffffff;
        text-style: bold;
    }

    .stui-slider {
        border: tall #ffffff;
        background: #000000;
    }

    .stui-expander:focus {
        border: tall #ffff00;
        background: #000000;
        color: #ffffff;
        text-style: bold;
    }

    .alert-success, .alert-info, .alert-warning, .alert-error, .traceback {
        color: #ffffff;
    }

    .disabled {
        color: #bfbfbf;
    }
"""


def resolve_theme(value: str | None = None) -> str:
    raw_theme = value if value is not None else os.environ.get("STUI_THEME", "")
    theme = raw_theme.strip().lower()
    if theme in SUPPORTED_THEMES:
        return theme
    return "default"


def css_for_theme(base_css: str, theme: str | None = None) -> str:
    if resolve_theme(theme) == "high-contrast":
        return f"{base_css}\n{HIGH_CONTRAST_CSS}"
    return base_css


def dom_id_for_key(key: str) -> str:
    digest = hashlib.sha1(key.encode("utf-8")).hexdigest()[:12]
    return f"stui-{digest}"


def _clip_text(value: object, width: int) -> str:
    text = str(value)
    if width < 1:
        return ""
    if len(text) <= width:
        return text
    if width <= 3:
        return "." * width
    return f"{text[: width - 3]}..."


class StuiButton(Button):
    BINDINGS = [
        Binding("enter", "press", "Press button", show=False),
        Binding("space", "press", "Press button", show=False),
    ]

    def __init__(self, element: ButtonElement) -> None:
        self.stui_key = element.key
        super().__init__(
            _clip_text(element.label, MAX_WIDGET_LABEL_WIDTH),
            id=dom_id_for_key(element.key),
            disabled=element.disabled,
            tooltip=element.help
            or "Enter or Space activates. Tab and Shift+Tab move focus.",
        )


class StuiTextInput(Input):
    def __init__(self, element: TextInputElement) -> None:
        self.stui_key = element.key
        super().__init__(
            value=element.value,
            placeholder=element.placeholder or "",
            id=dom_id_for_key(element.key),
            disabled=element.disabled,
        )


class StuiNumberInput(Input):
    def __init__(self, element: NumberInputElement) -> None:
        self.stui_key = element.key
        self.stui_fallback = element.value
        self.stui_min_value = element.min_value
        self.stui_max_value = element.max_value
        self.stui_step = element.step
        super().__init__(
            value=str(element.value),
            id=dom_id_for_key(element.key),
            disabled=element.disabled,
        )


class StuiCheckbox(Checkbox):
    def __init__(self, element: CheckboxElement) -> None:
        self.stui_key = element.key
        super().__init__(
            _clip_text(element.label, MAX_WIDGET_LABEL_WIDTH),
            value=element.value,
            id=dom_id_for_key(element.key),
            disabled=element.disabled,
        )


class StuiSelectbox(Static, can_focus=True):
    BINDINGS = [
        Binding("enter", "choose_next", "Next choice", show=False),
        Binding("right", "choose_next", "Next choice"),
        Binding("down", "choose_next", "Next choice", show=False),
        Binding("left", "choose_previous", "Previous choice"),
        Binding("up", "choose_previous", "Previous choice", show=False),
    ]

    class Changed(Message):
        def __init__(self, selectbox: StuiSelectbox, value: object) -> None:
            super().__init__()
            self.selectbox = selectbox
            self.value = value

    def __init__(self, element: SelectboxElement) -> None:
        self.stui_key = element.key
        self.stui_options = element.options
        self.stui_index = element.index
        super().__init__(
            self._render_value(),
            id=dom_id_for_key(element.key),
            classes="stui-selectbox",
        )
        self.disabled = element.disabled

    def action_choose_next(self) -> None:
        self._move(1)

    def action_choose_previous(self) -> None:
        self._move(-1)

    def _move(self, delta: int) -> None:
        if self.disabled or len(self.stui_options) < 2:
            return
        self.stui_index = (self.stui_index + delta) % len(self.stui_options)
        value = self.stui_options[self.stui_index]
        self.update(self._render_value())
        self.post_message(self.Changed(self, value))

    def _render_value(self) -> str:
        value = self.stui_options[self.stui_index]
        return f"[ {_clip_text(value, MAX_WIDGET_LABEL_WIDTH)} ]"


class StuiRadioSet(Static, can_focus=True):
    BINDINGS = [
        Binding("down", "next_button", "Next option"),
        Binding("right", "next_button", "Next option", show=False),
        Binding("up", "previous_button", "Previous option"),
        Binding("left", "previous_button", "Previous option", show=False),
        Binding("enter", "next_button", "Next option", show=False),
        Binding("space", "next_button", "Next option", show=False),
    ]

    class Changed(Message):
        def __init__(self, radio: StuiRadioSet, value: object) -> None:
            super().__init__()
            self.radio = radio
            self.value = value

    def __init__(self, element: RadioElement) -> None:
        self.stui_key = element.key
        self.stui_options = element.options
        self.stui_index = element.index
        super().__init__(
            self._render_value(),
            id=dom_id_for_key(element.key),
            classes="stui-radio",
        )
        self.disabled = element.disabled

    def action_next_button(self) -> None:
        self._move(1)

    def action_previous_button(self) -> None:
        self._move(-1)

    def _move(self, delta: int) -> None:
        if self.disabled or len(self.stui_options) < 2:
            return
        self.stui_index = (self.stui_index + delta) % len(self.stui_options)
        value = self.stui_options[self.stui_index]
        self.update(self._render_value())
        self.post_message(self.Changed(self, value))

    def _render_value(self) -> str:
        lines = []
        for index, option in enumerate(self.stui_options):
            marker = "*" if index == self.stui_index else " "
            lines.append(f"({marker}) {_clip_text(option, MAX_WIDGET_LABEL_WIDTH)}")
        return "\n".join(lines)


class StuiExpander(Vertical, can_focus=True):
    BINDINGS = [
        Binding("enter", "toggle", "Toggle"),
        Binding("space", "toggle", "Toggle", show=False),
    ]

    class Changed(Message):
        def __init__(self, expander: StuiExpander, expanded: bool) -> None:
            super().__init__()
            self.expander = expander
            self.expanded = expanded

    def __init__(self, element: ExpanderElement, *children) -> None:
        self.stui_key = element.key
        self.stui_expanded = element.expanded
        marker = "-" if element.expanded else "+"
        label = Static(
            f"[{marker}] {_clip_text(element.label, MAX_STATIC_LABEL_WIDTH)}",
            classes="stui-expander-label",
        )
        super().__init__(
            label,
            *children,
            id=dom_id_for_key(element.key),
            classes="stui-expander",
        )
        self.tooltip = "Enter or Space toggles. Tab and Shift+Tab move focus."

    def action_toggle(self) -> None:
        self.stui_expanded = not self.stui_expanded
        self.post_message(self.Changed(self, self.stui_expanded))


class StuiApp(App[None]):
    TITLE = "stui"
    CSS = """
    Screen {
        background: #101014;
        color: #e8e8ee;
    }

    Header, Footer {
        background: #15151d;
    }

    #body {
        padding: 1 1;
    }

    .title {
        color: #8ab4ff;
        text-style: bold;
        margin: 0 0 1 0;
    }

    .header {
        color: #d7ddff;
        text-style: bold;
        margin: 1 0 1 0;
    }

    .subheader {
        color: #cfd6ff;
        text-style: bold;
        margin: 1 0 1 0;
    }

    .caption {
        color: #a2a4b3;
        text-style: italic;
        margin: 0 0 1 0;
    }

    .write, .text, .markdown, .code, .json {
        margin: 0 0 1 0;
    }

    .divider {
        color: #343444;
        margin: 1 0;
    }

    .alert {
        margin: 1 0;
    }

    .alert-success {
        color: #d7ffdf;
    }

    .alert-info {
        color: #d8e7ff;
    }

    .alert-warning {
        color: #fff1bd;
    }

    .alert-error {
        color: #ffd9d9;
    }

    Button {
        margin: 1 0;
        min-width: 16;
    }

    Button:focus {
        background: #8ab4ff;
        color: #101014;
        text-style: bold;
    }

    .stui-field {
        margin: 1 0;
    }

    .stui-field-label {
        color: #cfd3df;
    }

    Input, Checkbox {
        margin: 0 0 1 0;
    }

    .stui-selectbox, .stui-radio {
        margin: 0 0 1 0;
    }

    Input:focus {
        border: tall #8ab4ff;
        background: #202033;
    }

    Checkbox:focus {
        background: #202033;
        color: #ffffff;
        text-style: bold;
    }

    .stui-selectbox:focus, .stui-radio:focus {
        border: tall #8ab4ff;
        background: #202033;
    }

    .stui-slider {
        border: round #343444;
        padding: 1;
        margin: 1 0;
        background: #171722;
    }

    .stui-slider:focus {
        border: round #8ab4ff;
        background: #202033;
        color: #ffffff;
    }

    .disabled {
        color: #777783;
    }

    .error {
        margin: 1 0;
    }

    .traceback {
        color: #ffd7d7;
    }

    .exception {
        margin: 1 0;
    }

    .stui-progress {
        margin: 1 0;
    }

    .stui-progress-label {
        color: #cfd3df;
        margin: 0 0 1 0;
    }

    .stui-status, .stui-spinner, .stui-help {
        margin: 1 0;
    }

    .table {
        margin: 1 0;
    }

    .metric, .bar-chart {
        margin: 1 0;
    }

    .stui-container {
        border-left: solid #343444;
        padding: 0 0 0 1;
        margin: 1 0;
    }

    .stui-columns {
        margin: 1 0;
    }

    .stui-column {
        width: 1fr;
        min-width: 0;
        padding: 0 1 0 0;
    }

    .stui-columns-stacked .stui-column {
        width: 100%;
        padding: 0;
        margin: 0 0 1 0;
    }

    .stui-expander {
        border: round #343444;
        padding: 0 1;
        margin: 1 0;
    }

    .stui-expander:focus {
        border: round #8ab4ff;
        background: #202033;
    }

    .stui-expander-label {
        color: #d7ddff;
        text-style: bold;
        margin: 0 0 1 0;
    }
    """
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "rerun_script", "Rerun"),
        Binding("tab", "focus_next", "Next widget"),
        Binding("shift+tab", "focus_previous", "Previous widget"),
    ]

    def __init__(self, runtime: Runtime) -> None:
        super().__init__()
        self.runtime = runtime
        self.stui_theme = resolve_theme()
        self.CSS = css_for_theme(type(self).CSS, self.stui_theme)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        yield VerticalScroll(id="body")
        yield Footer()

    async def on_mount(self) -> None:
        self.runtime.run_script()
        await self.render_runtime()

    async def action_rerun_script(self) -> None:
        focused_key = self._focused_stui_key()
        if focused_key is not None:
            self.runtime.last_focused_key = focused_key
        self.runtime.run_script()
        await self.render_runtime()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        key = getattr(event.button, "stui_key", None)
        if key is None:
            return
        event.stop()
        self.runtime.press_button(key)
        self.runtime.run_script()
        await self.render_runtime()

    async def on_stui_slider_changed(self, event: StuiSlider.Changed) -> None:
        event.stop()
        self.runtime.set_widget_value(event.key, event.value)
        self.runtime.run_script()
        await self.render_runtime()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        input_widget = getattr(event, "input", None) or event.control
        key = getattr(input_widget, "stui_key", None)
        if key is None:
            return
        event.stop()
        value = event.value
        if isinstance(input_widget, StuiNumberInput):
            value = self._parse_number_input(input_widget, event.value)
        self.runtime.set_widget_value(key, value)
        self.runtime.run_script()
        await self.render_runtime()

    async def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        checkbox = event.checkbox
        key = getattr(checkbox, "stui_key", None)
        if key is None:
            return
        event.stop()
        self.runtime.set_widget_value(key, event.value)
        self.runtime.run_script()
        await self.render_runtime()

    async def on_stui_radio_set_changed(
        self, event: StuiRadioSet.Changed
    ) -> None:
        key = getattr(event.radio, "stui_key", None)
        if key is None:
            return
        if not self._body_is_ready():
            return
        event.stop()
        self.runtime.last_focused_key = key
        self.runtime.set_widget_value(key, event.value)
        self.runtime.run_script()
        await self.render_runtime()

    async def render_runtime(self) -> None:
        body = self.query_one("#body", VerticalScroll)
        await body.remove_children()
        widgets = [self._build_widget(element) for element in self.runtime.elements]
        if widgets:
            await body.mount(*widgets)
        await self._restore_focus()

    def _build_widget(self, element):
        if isinstance(element, TitleElement):
            return Static(Text(element.body, style="bold"), classes="title")
        if isinstance(element, HeaderElement):
            return Static(Text(element.body, style="bold"), classes="header")
        if isinstance(element, SubheaderElement):
            return Static(Text(element.body, style="bold"), classes="subheader")
        if isinstance(element, WriteElement):
            return Static(element.text, classes="write")
        if isinstance(element, TextElement):
            return Static(element.body, classes="text")
        if isinstance(element, CaptionElement):
            return Static(Text(element.body, style="italic dim"), classes="caption")
        if isinstance(element, MarkdownElement):
            return Static(Markdown(element.body), classes="markdown")
        if isinstance(element, CodeElement):
            return Static(
                Syntax(
                    element.body,
                    element.language or "text",
                    word_wrap=True,
                    theme="ansi_dark",
                ),
                classes="code",
            )
        if isinstance(element, JsonElement):
            return Static(RichJSON(element.text), classes="json")
        if isinstance(element, TableElement):
            return Static(
                self._render_table(element, self.size.width),
                classes="table",
            )
        if isinstance(element, ExceptionElement):
            return Static(
                Panel(
                    Text(element.traceback, style="#ffd7d7", overflow="fold"),
                    title="Exception",
                    border_style="red",
                    title_align="left",
                    padding=(0, 1),
                ),
                classes="exception",
            )
        if isinstance(element, ProgressElement):
            progress_bar = ProgressBar(total=100, show_eta=False)
            progress_bar.update(progress=element.value)
            if element.text is None:
                return Vertical(progress_bar, classes="stui-progress")
            return Vertical(
                Static(
                    _clip_text(element.text, MAX_STATIC_LABEL_WIDTH),
                    classes="stui-progress-label",
                ),
                progress_bar,
                classes="stui-progress",
            )
        if isinstance(element, StatusElement):
            panel = Static(
                Panel(
                    Text(_clip_text(element.label, MAX_STATIC_LABEL_WIDTH)),
                    title=element.state,
                    title_align="left",
                    border_style=self._status_style(element.state),
                    padding=(0, 1),
                ),
                classes=f"stui-status stui-status-{element.state}",
            )
            if not element.expanded:
                return panel
            children = [
                self._build_widget(child)
                for child in (element.children or [])
            ]
            return Vertical(panel, *children, classes="stui-status")
        if isinstance(element, SpinnerElement):
            panel = Static(
                Panel(
                    Text(_clip_text(element.text, MAX_STATIC_LABEL_WIDTH)),
                    title="spinner",
                    title_align="left",
                    border_style="cyan",
                    padding=(0, 1),
                ),
                classes="stui-spinner",
            )
            children = [
                self._build_widget(child)
                for child in (element.children or [])
            ]
            if not children:
                return panel
            return Vertical(panel, *children, classes="stui-spinner")
        if isinstance(element, HelpElement):
            return Static(
                Panel(
                    Text(element.body, overflow="fold"),
                    title="help",
                    title_align="left",
                    border_style="#6f7cff",
                    padding=(0, 1),
                ),
                classes="stui-help",
            )
        if isinstance(element, MetricElement):
            return Static(self._render_metric(element), classes="metric")
        if isinstance(element, BarChartElement):
            return Static(self._render_bar_chart(element), classes="bar-chart")
        if isinstance(element, LineChartElement):
            return Static(self._render_line_chart(element), classes="bar-chart")
        if isinstance(element, ContainerElement):
            children = [self._build_widget(child) for child in element.children]
            return Vertical(*children, classes="stui-container")
        if isinstance(element, ColumnsElement):
            columns = [
                Vertical(
                    *(self._build_widget(child) for child in column),
                    classes="stui-column",
                )
                for column in element.columns
            ]
            if self._should_stack_columns(len(columns)):
                return Vertical(*columns, classes="stui-columns stui-columns-stacked")
            return Horizontal(*columns, classes="stui-columns")
        if isinstance(element, ExpanderElement):
            if not element.expanded:
                return StuiExpander(element)
            children = [
                self._build_widget(child)
                for child in (element.children or [])
            ]
            return StuiExpander(element, *children)
        if isinstance(element, DividerElement):
            width = max(8, min(40, self.size.width - 4))
            return Static("─" * width, classes="divider")
        if isinstance(element, AlertElement):
            kind = element.kind.lower()
            return Static(
                Panel(
                    Text(str(element.body), overflow="fold"),
                    title=element.kind,
                    title_align="left",
                    border_style=self._alert_style(kind),
                    padding=(0, 1),
                ),
                classes=f"alert alert-{kind}",
            )
        if isinstance(element, ButtonElement):
            return StuiButton(element)
        if isinstance(element, TextInputElement):
            text_input = StuiTextInput(element)
            text_input.tooltip = (
                "Type text. Enter submits. Tab and Shift+Tab move focus."
            )
            return Vertical(
                Static(
                    _clip_text(element.label, MAX_STATIC_LABEL_WIDTH),
                    classes="stui-field-label",
                ),
                text_input,
                classes="stui-field",
            )
        if isinstance(element, NumberInputElement):
            number_input = StuiNumberInput(element)
            number_input.tooltip = (
                "Type a number. Enter submits. Tab and Shift+Tab move focus."
            )
            return Vertical(
                Static(
                    _clip_text(element.label, MAX_STATIC_LABEL_WIDTH),
                    classes="stui-field-label",
                ),
                number_input,
                classes="stui-field",
            )
        if isinstance(element, CheckboxElement):
            checkbox = StuiCheckbox(element)
            checkbox.tooltip = (
                "Space toggles. Tab and Shift+Tab move focus."
            )
            return checkbox
        if isinstance(element, SelectboxElement):
            selectbox = StuiSelectbox(element)
            selectbox.tooltip = (
                "Right/down/Enter choose next. Left/up choose previous. "
                "Tab and Shift+Tab move focus."
            )
            return Vertical(
                Static(
                    _clip_text(element.label, MAX_STATIC_LABEL_WIDTH),
                    classes="stui-field-label",
                ),
                selectbox,
                classes="stui-field",
            )
        if isinstance(element, RadioElement):
            radio = StuiRadioSet(element)
            radio.tooltip = (
                "Arrow keys choose. Tab and Shift+Tab move focus."
            )
            return Vertical(
                Static(
                    _clip_text(element.label, MAX_STATIC_LABEL_WIDTH),
                    classes="stui-field-label",
                ),
                radio,
                classes="stui-field",
            )
        if isinstance(element, SliderElement):
            slider = StuiSlider(
                label=element.label,
                key=element.key,
                min_value=element.min_value,
                max_value=element.max_value,
                value=element.value,
                step=element.step,
                disabled=element.disabled,
                id=dom_id_for_key(element.key),
            )
            slider.tooltip = (
                element.help
                or "Left/right arrows or h/l adjust. Home/End jump to min/max."
            )
            return slider
        if isinstance(element, ErrorElement):
            return Static(
                Panel(
                    Text(element.traceback, style="#ffd7d7", overflow="fold"),
                    title=self._script_error_title(element.traceback),
                    border_style="red",
                    title_align="left",
                    padding=(0, 1),
                ),
                classes="error",
            )
        return Static(str(element))

    async def on_stui_selectbox_changed(
        self, event: StuiSelectbox.Changed
    ) -> None:
        key = getattr(event.selectbox, "stui_key", None)
        if key is None:
            return
        event.stop()
        self.runtime.set_widget_value(key, event.value)
        self.runtime.run_script()
        await self.render_runtime()

    async def on_stui_expander_changed(self, event: StuiExpander.Changed) -> None:
        key = getattr(event.expander, "stui_key", None)
        if key is None:
            return
        event.stop()
        self.runtime.set_widget_value(key, event.expanded)
        self.runtime.run_script()
        await self.render_runtime()

    async def _restore_focus(self) -> None:
        key = self.runtime.last_focused_key
        if key is None:
            return
        try:
            widget = self.query(f"#{dom_id_for_key(key)}").first()
        except NoMatches:
            return
        if widget is not None and getattr(widget, "can_focus", False):
            self.set_focus(widget)

    def _focused_stui_key(self) -> str | None:
        focused = self.focused
        if focused is None:
            return None
        return getattr(focused, "stui_key", None)

    def _body_is_ready(self) -> bool:
        try:
            self.query_one("#body", VerticalScroll)
        except NoMatches:
            return False
        return True

    def _should_stack_columns(self, count: int) -> bool:
        if count < 2:
            return True
        available_width = self.size.width or 80
        return available_width // count < MIN_RENDERED_COLUMN_WIDTH

    @staticmethod
    def _parse_number_input(widget: StuiNumberInput, raw: str) -> int | float:
        fallback = widget.stui_fallback
        try:
            value: int | float
            if (
                isinstance(fallback, int)
                and not isinstance(fallback, bool)
                and not isinstance(widget.stui_step, float)
            ):
                value = int(float(raw))
            else:
                value = float(raw)
        except ValueError:
            value = fallback
        if widget.stui_min_value is not None:
            value = max(value, widget.stui_min_value)
        if widget.stui_max_value is not None:
            value = min(value, widget.stui_max_value)
        return value

    @staticmethod
    def _render_table(
        element: TableElement,
        available_width: int = 80,
    ) -> RichTable | Text:
        if available_width and available_width < 16:
            return Text("Table requires a wider terminal.", style="yellow")
        headers, rows = StuiApp._trim_table(
            element.headers,
            element.rows,
            available_width,
        )
        column_count = max(1, len(headers))
        usable_width = max(20, available_width or 80)
        column_width = max(
            MIN_TABLE_COLUMN_WIDTH,
            min(MAX_TABLE_COLUMN_WIDTH, usable_width // column_count - 3),
        )
        table = RichTable(show_lines=False)
        for header in headers:
            table.add_column(
                _clip_text(header, column_width),
                overflow="fold",
                max_width=column_width,
            )
        for row in rows:
            table.add_row(*(_clip_text(cell, column_width * 2) for cell in row))
        return table

    @staticmethod
    def _trim_table(
        headers: tuple[str, ...],
        rows: tuple[tuple[str, ...], ...],
        available_width: int = 80,
    ) -> tuple[tuple[str, ...], tuple[tuple[str, ...], ...]]:
        if len(headers) <= 1:
            return headers or ("value",), rows
        width = max(20, available_width or 80)
        visible_columns = max(1, width // MIN_TABLE_COLUMN_WIDTH)
        visible_columns = min(MAX_TABLE_COLUMNS, visible_columns, len(headers))
        if visible_columns >= len(headers):
            return headers, rows
        kept_columns = max(1, visible_columns - 1)
        trimmed_headers = (*headers[:kept_columns], "...")
        hidden_count = len(headers) - kept_columns
        trimmed_rows = tuple(
            (*row[:kept_columns], f"+{hidden_count} cols")
            for row in rows
        )
        return trimmed_headers, trimmed_rows

    @staticmethod
    def _render_metric(element: MetricElement) -> Panel:
        body = Text()
        body.append(_clip_text(element.label, MAX_STATIC_LABEL_WIDTH), style="dim")
        body.append("\n")
        body.append(
            _clip_text(element.value, MAX_STATIC_LABEL_WIDTH),
            style="bold #ffffff",
        )
        if element.delta is not None:
            style = "green" if not element.delta.startswith("-") else "red"
            body.append(
                f"  {_clip_text(element.delta, MAX_WIDGET_LABEL_WIDTH)}",
                style=style,
            )
        return Panel(
            body,
            border_style="#343444",
            padding=(0, 1),
        )

    @staticmethod
    def _render_bar_chart(element: BarChartElement) -> Text:
        if element.empty:
            return Text("No chart data", style="dim")
        points = tuple(
            point for point in element.points if math.isfinite(point.value)
        )
        if element.height is not None:
            points = points[: element.height]
        if not points:
            return Text("No chart data", style="dim")

        max_abs = max(abs(point.value) for point in points) or 1
        label_width = min(
            12,
            max(1, max(len(point.label) for point in points)),
        )
        plot_width = min(max(element.width or 28, 1), 60)
        half_width = max(1, plot_width // 2)
        has_negative = any(point.value < 0 for point in points)
        has_positive = any(point.value > 0 for point in points)
        chart = Text()
        for index, point in enumerate(points):
            bar_len = round((abs(point.value) / max_abs) * half_width)
            bar_len = max(1, bar_len) if point.value else 0
            if has_negative and has_positive:
                left = (
                    ("█" * bar_len).rjust(half_width)
                    if point.value < 0
                    else " " * half_width
                )
                right = "█" * bar_len if point.value > 0 else ""
                bar = f"{left}│{right or '·'}"
            else:
                bar = "█" * bar_len if point.value else "·"
            style = "red" if point.value < 0 else "green"
            label = _clip_text(point.label, label_width)
            chart.append(label.rjust(label_width), style="dim")
            chart.append(" │ ", style="dim")
            chart.append(bar, style=style)
            chart.append(f" {point.value:g}")
            if index != len(points) - 1:
                chart.append("\n")
        return chart

    @staticmethod
    def _render_line_chart(element: LineChartElement) -> Text:
        if element.empty:
            return Text("No chart data", style="dim")
        series = tuple(
            item
            for item in element.series
            if any(math.isfinite(value) for value in item.values)
        )
        if element.height is not None:
            series = series[: element.height]
        if not series:
            return Text("No chart data", style="dim")

        label_width = min(
            12,
            max(1, max(len(item.label) for item in series)),
        )
        plot_width = min(max(element.width or 28, 1), 60)
        chart = Text()
        for index, item in enumerate(series):
            values = tuple(value for value in item.values if math.isfinite(value))
            sparkline = StuiApp._sparkline(values, plot_width)
            label = _clip_text(item.label, label_width)
            chart.append(label.rjust(label_width), style="dim")
            chart.append(" │ ", style="dim")
            chart.append(sparkline, style="cyan")
            chart.append(f" {values[-1]:g}" if values else " 0")
            if index != len(series) - 1:
                chart.append("\n")
        return chart

    @staticmethod
    def _sparkline(values: tuple[float, ...], width: int) -> str:
        if not values:
            return "·"
        if len(values) > width:
            step = (len(values) - 1) / max(1, width - 1)
            values = tuple(values[round(index * step)] for index in range(width))
        low = min(values)
        high = max(values)
        if high == low:
            return "─" * max(1, len(values))
        ticks = "▁▂▃▄▅▆▇█"
        scale = len(ticks) - 1
        spread = high - low
        if not math.isfinite(spread):
            max_abs = max(abs(value) for value in values) or 1
            return "".join(
                ticks[
                    StuiApp._clamped_tick_index(
                        ((value / max_abs) + 1) / 2,
                        scale,
                    )
                ]
                for value in values
            )
        return "".join(
            ticks[
                StuiApp._clamped_tick_index(
                    (value - low) / spread,
                    scale,
                )
            ]
            for value in values
        )

    @staticmethod
    def _clamped_tick_index(normalized: float, scale: int) -> int:
        if not math.isfinite(normalized):
            normalized = 0.0
        normalized = min(1.0, max(0.0, normalized))
        return round(normalized * scale)

    @staticmethod
    def _alert_style(kind: str) -> str:
        return {
            "success": "green",
            "info": "blue",
            "warning": "yellow",
            "error": "red",
        }.get(kind, "white")

    @staticmethod
    def _status_style(state: str) -> str:
        return {
            "running": "blue",
            "complete": "green",
            "error": "red",
        }.get(state, "white")

    @staticmethod
    def _script_error_title(traceback: str) -> str:
        if traceback.startswith("Duplicate widget key"):
            return "Duplicate widget key"
        return "Script error"
