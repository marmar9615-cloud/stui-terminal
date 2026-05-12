from __future__ import annotations

from dataclasses import dataclass
from typing import Any, TypeAlias

Number: TypeAlias = int | float


@dataclass(frozen=True)
class TitleElement:
    body: str
    key: str | None = None


@dataclass(frozen=True)
class HeaderElement:
    body: str
    key: str | None = None


@dataclass(frozen=True)
class SubheaderElement:
    body: str
    key: str | None = None


@dataclass(frozen=True)
class TextElement:
    body: str


@dataclass(frozen=True)
class CaptionElement:
    body: str


@dataclass(frozen=True)
class MarkdownElement:
    body: str


@dataclass(frozen=True)
class CodeElement:
    body: str
    language: str | None = None


@dataclass(frozen=True)
class JsonElement:
    obj: Any
    text: str


@dataclass(frozen=True)
class ExceptionElement:
    traceback: str


@dataclass(frozen=True)
class ProgressElement:
    value: int
    text: str | None = None


@dataclass(frozen=True)
class StatusElement:
    label: str
    state: str = "running"
    expanded: bool = False
    children: list[Any] | None = None


@dataclass(frozen=True)
class SpinnerElement:
    text: str = "Working..."
    children: list[Any] | None = None


@dataclass(frozen=True)
class HelpElement:
    body: str


@dataclass(frozen=True)
class MetricElement:
    label: str
    value: str
    delta: str | None = None


@dataclass(frozen=True)
class BarChartPoint:
    label: str
    value: float


@dataclass(frozen=True)
class BarChartElement:
    points: tuple[BarChartPoint, ...]
    width: int | None = None
    height: int | None = None


@dataclass(frozen=True)
class LineChartSeries:
    label: str
    values: tuple[float, ...]


@dataclass(frozen=True)
class LineChartElement:
    series: tuple[LineChartSeries, ...]
    width: int | None = None
    height: int | None = None


@dataclass(frozen=True)
class TableElement:
    headers: tuple[str, ...]
    rows: tuple[tuple[str, ...], ...]


@dataclass(frozen=True)
class ContainerElement:
    children: list[Any]


@dataclass(frozen=True)
class ColumnsElement:
    columns: list[list[Any]]


@dataclass(frozen=True)
class ExpanderElement:
    label: str
    key: str
    expanded: bool = False
    children: list[Any] | None = None


@dataclass(frozen=True)
class DividerElement:
    pass


@dataclass(frozen=True)
class AlertElement:
    body: str
    kind: str


@dataclass(frozen=True)
class WriteElement:
    values: tuple[Any, ...]
    text: str


@dataclass(frozen=True)
class ButtonElement:
    label: str
    key: str
    help: str | None = None
    disabled: bool = False


@dataclass(frozen=True)
class SliderElement:
    label: str
    key: str
    min_value: Number
    max_value: Number
    value: Number
    step: Number
    help: str | None = None
    disabled: bool = False


@dataclass(frozen=True)
class TextInputElement:
    label: str
    key: str
    value: str
    placeholder: str | None = None
    disabled: bool = False


@dataclass(frozen=True)
class CheckboxElement:
    label: str
    key: str
    value: bool
    disabled: bool = False


@dataclass(frozen=True)
class NumberInputElement:
    label: str
    key: str
    value: Number
    min_value: Number | None = None
    max_value: Number | None = None
    step: Number = 1
    disabled: bool = False


@dataclass(frozen=True)
class SelectboxElement:
    label: str
    key: str
    options: tuple[Any, ...]
    index: int
    disabled: bool = False


@dataclass(frozen=True)
class RadioElement:
    label: str
    key: str
    options: tuple[Any, ...]
    index: int
    disabled: bool = False


@dataclass(frozen=True)
class ErrorElement:
    traceback: str


Element: TypeAlias = (
    TitleElement
    | HeaderElement
    | SubheaderElement
    | TextElement
    | CaptionElement
    | MarkdownElement
    | CodeElement
    | JsonElement
    | ExceptionElement
    | ProgressElement
    | StatusElement
    | SpinnerElement
    | HelpElement
    | MetricElement
    | BarChartElement
    | LineChartElement
    | TableElement
    | ContainerElement
    | ColumnsElement
    | ExpanderElement
    | DividerElement
    | AlertElement
    | WriteElement
    | ButtonElement
    | SliderElement
    | TextInputElement
    | CheckboxElement
    | NumberInputElement
    | SelectboxElement
    | RadioElement
    | ErrorElement
)
