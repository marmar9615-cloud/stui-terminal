from __future__ import annotations

import inspect

import stui as st


def _sig(*parts: str) -> str:
    return "".join(parts)


EXPECTED_PUBLIC_EXPORTS = [
    "__version__",
    "button",
    "bar_chart",
    "caption",
    "checkbox",
    "code",
    "container",
    "dataframe",
    "divider",
    "error",
    "exception",
    "expander",
    "form",
    "form_submit_button",
    "header",
    "info",
    "json",
    "line_chart",
    "markdown",
    "metric",
    "number_input",
    "progress",
    "radio",
    "rerun",
    "session_state",
    "selectbox",
    "slider",
    "stop",
    "subheader",
    "table",
    "success",
    "text",
    "text_input",
    "title",
    "warning",
    "write",
]

EXPECTED_PUBLIC_SIGNATURES = {
    "bar_chart": _sig(
        "(data: 'Any', *, width: 'int | None' = None, ",
        "height: 'int | None' = None) -> 'None'",
    ),
    "button": _sig(
        "(label: 'str', key: 'str | None' = None, ",
        "help: 'str | None' = None, disabled: 'bool' = False, ",
        "on_click=None, args: 'tuple[Any, ...] | None' = None, ",
        "kwargs: 'dict[str, Any] | None' = None) -> 'bool'",
    ),
    "caption": "(body: 'Any') -> 'None'",
    "checkbox": _sig(
        "(label: 'str', value: 'bool' = False, *, ",
        "key: 'str | None' = None, disabled: 'bool' = False, ",
        "on_change=None, args: 'tuple[Any, ...] | None' = None, ",
        "kwargs: 'dict[str, Any] | None' = None) -> 'bool'",
    ),
    "code": "(body: 'Any', language: 'str | None' = None) -> 'None'",
    "container": "()",
    "dataframe": "(data: 'Any') -> 'None'",
    "divider": "() -> 'None'",
    "error": "(body: 'Any') -> 'None'",
    "exception": "(exc: 'BaseException') -> 'None'",
    "expander": _sig(
        "(label: 'str', expanded: 'bool' = False, *, ",
        "key: 'str | None' = None)",
    ),
    "form": "(key: 'str')",
    "form_submit_button": _sig(
        "(label: 'str' = 'Submit', *, disabled: 'bool' = False, ",
        "on_click=None, args: 'tuple[Any, ...] | None' = None, ",
        "kwargs: 'dict[str, Any] | None' = None) -> 'bool'",
    ),
    "header": "(body: 'Any', *, key: 'str | None' = None) -> 'None'",
    "info": "(body: 'Any') -> 'None'",
    "json": "(obj: 'Any') -> 'None'",
    "line_chart": _sig(
        "(data: 'Any', *, width: 'int | None' = None, ",
        "height: 'int | None' = None) -> 'None'",
    ),
    "markdown": "(body: 'Any') -> 'None'",
    "metric": "(label: 'Any', value: 'Any', delta: 'Any | None' = None) -> 'None'",
    "number_input": _sig(
        "(label: 'str', min_value: 'int | float | None' = None, ",
        "max_value: 'int | float | None' = None, ",
        "value: 'int | float' = 0, step: 'int | float' = 1, *, ",
        "key: 'str | None' = None, disabled: 'bool' = False, ",
        "on_change=None, args: 'tuple[Any, ...] | None' = None, ",
        "kwargs: 'dict[str, Any] | None' = None) -> 'int | float'",
    ),
    "progress": "(value: 'int | float', text: 'Any | None' = None) -> 'None'",
    "radio": _sig(
        "(label: 'str', options, index: 'int' = 0, *, ",
        "key: 'str | None' = None, disabled: 'bool' = False, ",
        "on_change=None, args: 'tuple[Any, ...] | None' = None, ",
        "kwargs: 'dict[str, Any] | None' = None)",
    ),
    "rerun": "() -> 'None'",
    "selectbox": _sig(
        "(label: 'str', options, index: 'int' = 0, *, ",
        "key: 'str | None' = None, disabled: 'bool' = False, ",
        "on_change=None, args: 'tuple[Any, ...] | None' = None, ",
        "kwargs: 'dict[str, Any] | None' = None)",
    ),
    "slider": _sig(
        "(label: 'str', min_value: 'int | float' = 0, ",
        "max_value: 'int | float' = 100, ",
        "value: 'int | float | None' = None, ",
        "step: 'int | float' = 1, *, key: 'str | None' = None, ",
        "help: 'str | None' = None, disabled: 'bool' = False, ",
        "on_change=None, args: 'tuple[Any, ...] | None' = None, ",
        "kwargs: 'dict[str, Any] | None' = None) -> 'int | float'",
    ),
    "stop": "() -> 'None'",
    "subheader": "(body: 'Any', *, key: 'str | None' = None) -> 'None'",
    "success": "(body: 'Any') -> 'None'",
    "table": "(data: 'Any') -> 'None'",
    "text": "(body: 'Any') -> 'None'",
    "text_input": _sig(
        "(label: 'str', value: 'str' = '', *, ",
        "key: 'str | None' = None, placeholder: 'str | None' = None, ",
        "disabled: 'bool' = False, on_change=None, ",
        "args: 'tuple[Any, ...] | None' = None, ",
        "kwargs: 'dict[str, Any] | None' = None) -> 'str'",
    ),
    "title": "(body: 'Any', *, key: 'str | None' = None) -> 'None'",
    "warning": "(body: 'Any') -> 'None'",
    "write": "(*args: 'Any') -> 'None'",
}


def test_public_all_exports_are_intentional() -> None:
    assert st.__all__ == EXPECTED_PUBLIC_EXPORTS


def test_import_stui_as_st_exposes_only_intended_public_exports() -> None:
    for name in EXPECTED_PUBLIC_EXPORTS:
        assert hasattr(st, name), name

    assert "Runtime" not in st.__all__
    assert "TitleElement" not in st.__all__
    assert "StuiApp" not in st.__all__
    assert "snap_value" not in st.__all__


def test_public_api_signatures_are_intentional() -> None:
    signatures = {
        name: str(inspect.signature(getattr(st, name)))
        for name in EXPECTED_PUBLIC_SIGNATURES
    }

    assert signatures == EXPECTED_PUBLIC_SIGNATURES


def test_widget_callback_and_disabled_parameter_names_are_consistent() -> None:
    callback_params = {
        "button": "on_click",
        "form_submit_button": "on_click",
        "checkbox": "on_change",
        "number_input": "on_change",
        "radio": "on_change",
        "selectbox": "on_change",
        "slider": "on_change",
        "text_input": "on_change",
    }

    for name, callback_name in callback_params.items():
        parameters = inspect.signature(getattr(st, name)).parameters
        assert "disabled" in parameters, name
        assert callback_name in parameters, name
        assert "args" in parameters, name
        assert "kwargs" in parameters, name
        assert parameters["disabled"].default is False
        assert parameters[callback_name].default is None
        assert parameters["args"].default is None
        assert parameters["kwargs"].default is None
