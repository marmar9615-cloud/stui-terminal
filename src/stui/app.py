from __future__ import annotations

import hashlib

from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Vertical, VerticalScroll
from textual.widgets import Button, Checkbox, Footer, Header, Input, Static

from .elements import (
    AlertElement,
    ButtonElement,
    CheckboxElement,
    DividerElement,
    ErrorElement,
    HeaderElement,
    MarkdownElement,
    SliderElement,
    TextElement,
    TextInputElement,
    TitleElement,
    WriteElement,
)
from .runtime import Runtime
from .widgets.slider import StuiSlider


def dom_id_for_key(key: str) -> str:
    digest = hashlib.sha1(key.encode("utf-8")).hexdigest()[:12]
    return f"stui-{digest}"


class StuiButton(Button):
    def __init__(self, element: ButtonElement) -> None:
        self.stui_key = element.key
        super().__init__(
            element.label,
            id=dom_id_for_key(element.key),
            disabled=element.disabled,
            tooltip=element.help or "Enter activates. Tab and Shift+Tab move focus.",
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


class StuiCheckbox(Checkbox):
    def __init__(self, element: CheckboxElement) -> None:
        self.stui_key = element.key
        super().__init__(
            element.label,
            value=element.value,
            id=dom_id_for_key(element.key),
            disabled=element.disabled,
        )


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
        padding: 1 2;
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

    .write, .text, .markdown {
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
        min-width: 20;
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

    Input:focus {
        border: tall #8ab4ff;
        background: #202033;
    }

    Checkbox:focus {
        background: #202033;
        color: #ffffff;
        text-style: bold;
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
    """
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "rerun_script", "Rerun"),
        Binding("tab", "focus_next", "Next"),
        Binding("shift+tab", "focus_previous", "Previous"),
    ]

    def __init__(self, runtime: Runtime) -> None:
        super().__init__()
        self.runtime = runtime

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
        self.runtime.set_widget_value(key, event.value)
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
        if isinstance(element, WriteElement):
            return Static(element.text, classes="write")
        if isinstance(element, TextElement):
            return Static(element.body, classes="text")
        if isinstance(element, MarkdownElement):
            return Static(Markdown(element.body), classes="markdown")
        if isinstance(element, DividerElement):
            return Static("─" * 40, classes="divider")
        if isinstance(element, AlertElement):
            kind = element.kind.lower()
            return Static(
                Panel(
                    element.body,
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
            text_input.tooltip = "Enter submits. Tab and Shift+Tab move focus."
            return Vertical(
                Static(element.label, classes="stui-field-label"),
                text_input,
                classes="stui-field",
            )
        if isinstance(element, CheckboxElement):
            checkbox = StuiCheckbox(element)
            checkbox.tooltip = "Space toggles. Tab and Shift+Tab move focus."
            return checkbox
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
                element.help or "Left/right arrows or h/l adjust the value."
            )
            return slider
        if isinstance(element, ErrorElement):
            return Static(
                Panel(
                    Text(element.traceback, style="#ffd7d7"),
                    title="Script error",
                    border_style="red",
                    title_align="left",
                    padding=(0, 1),
                ),
                classes="error",
            )
        return Static(str(element))

    async def _restore_focus(self) -> None:
        key = self.runtime.last_focused_key
        if key is None:
            return
        widget = self.query(f"#{dom_id_for_key(key)}").first()
        if widget is not None and getattr(widget, "can_focus", False):
            self.set_focus(widget)

    def _focused_stui_key(self) -> str | None:
        focused = self.focused
        if focused is None:
            return None
        return getattr(focused, "stui_key", None)

    @staticmethod
    def _alert_style(kind: str) -> str:
        return {
            "success": "green",
            "info": "blue",
            "warning": "yellow",
            "error": "red",
        }.get(kind, "white")
