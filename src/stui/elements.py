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
class TextElement:
    body: str


@dataclass(frozen=True)
class MarkdownElement:
    body: str


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
class ErrorElement:
    traceback: str


Element: TypeAlias = (
    TitleElement
    | HeaderElement
    | TextElement
    | MarkdownElement
    | DividerElement
    | AlertElement
    | WriteElement
    | ButtonElement
    | SliderElement
    | TextInputElement
    | CheckboxElement
    | ErrorElement
)
