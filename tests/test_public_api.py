from __future__ import annotations

import inspect
import re
from pathlib import Path

import stui as st

ROOT = Path(__file__).resolve().parents[1]


def _sig(*parts: str) -> str:
    return "".join(parts)


EXPECTED_PUBLIC_EXPORTS = [
    "__version__",
    "button",
    "bar_chart",
    "caption",
    "checkbox",
    "code",
    "columns",
    "container",
    "dataframe",
    "divider",
    "error",
    "exception",
    "expander",
    "form",
    "form_submit_button",
    "header",
    "help",
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
    "spinner",
    "stop",
    "subheader",
    "status",
    "table",
    "success",
    "text",
    "text_input",
    "title",
    "warning",
    "write",
]

EXPECTED_API_CLASSIFICATIONS = {
    "__version__": "v1-stable",
    "bar_chart": "pre-v1 experimental",
    "button": "v1-stable",
    "caption": "v1-stable",
    "checkbox": "v1-stable",
    "code": "v1-stable",
    "columns": "pre-v1 experimental",
    "container": "pre-v1 experimental",
    "dataframe": "pre-v1 experimental",
    "divider": "v1-stable",
    "error": "v1-stable",
    "exception": "v1-stable",
    "expander": "pre-v1 experimental",
    "form": "pre-v1 experimental",
    "form_submit_button": "pre-v1 experimental",
    "header": "v1-stable",
    "help": "pre-v1 experimental",
    "info": "v1-stable",
    "json": "pre-v1 experimental",
    "line_chart": "pre-v1 experimental",
    "markdown": "v1-stable",
    "metric": "pre-v1 experimental",
    "number_input": "pre-v1 experimental",
    "progress": "pre-v1 experimental",
    "radio": "pre-v1 experimental",
    "rerun": "pre-v1 experimental",
    "selectbox": "pre-v1 experimental",
    "session_state": "v1-stable",
    "slider": "v1-stable",
    "spinner": "pre-v1 experimental",
    "stop": "pre-v1 experimental",
    "subheader": "v1-stable",
    "status": "pre-v1 experimental",
    "success": "v1-stable",
    "table": "pre-v1 experimental",
    "text": "v1-stable",
    "text_input": "v1-stable",
    "title": "v1-stable",
    "warning": "v1-stable",
    "write": "v1-stable",
}

EXPECTED_STABLE_APIS = {
    api
    for api, classification in EXPECTED_API_CLASSIFICATIONS.items()
    if classification == "v1-stable"
}

EXPECTED_EXPERIMENTAL_APIS = {
    api
    for api, classification in EXPECTED_API_CLASSIFICATIONS.items()
    if classification == "pre-v1 experimental"
}

EXPECTED_EXPERIMENTAL_FREEZE_DECISIONS = {
    "columns",
    "help",
    "spinner",
    "status",
}

EXPECTED_DEFERRED_API_AREAS = [
    "st.sidebar",
    "st.tabs",
    "st.file_uploader",
    "st.cache_data",
    "st.cache_resource",
    "st.components",
    "custom column ratios/gaps",
    "editable dataframes",
    "plotting-library parity",
    "browser/server runtime",
]

PRIVATE_INTERNAL_NAMES = [
    "ApiUsageError",
    "ButtonElement",
    "DuplicateWidgetKeyError",
    "RerunException",
    "Runtime",
    "SessionState",
    "SessionStateProxy",
    "StopException",
    "StuiApp",
    "StuiSlider",
    "TitleElement",
    "get_current_runtime",
    "snap_value",
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
    "columns": "(count: 'int')",
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
    "help": "(obj_or_text: 'Any') -> 'None'",
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
    "spinner": "(text: 'str' = 'Working...')",
    "stop": "() -> 'None'",
    "subheader": "(body: 'Any', *, key: 'str | None' = None) -> 'None'",
    "status": _sig(
        "(label: 'Any', state: 'str' = 'running', ",
        "expanded: 'bool' = False)",
    ),
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


def _documented_api_classifications(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    start = "<!-- API_CLASSIFICATION_START -->"
    end = "<!-- API_CLASSIFICATION_END -->"
    table = text.split(start, 1)[1].split(end, 1)[0]
    classifications: dict[str, str] = {}

    for line in table.splitlines():
        if not line.startswith("| `"):
            continue
        columns = [column.strip() for column in line.strip("|").split("|")]
        api = columns[0].strip("`")
        classifications[api] = columns[1]

    return classifications


def _documented_deferred_api_areas(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    start = "<!-- API_DEFERRED_START -->"
    end = "<!-- API_DEFERRED_END -->"
    table = text.split(start, 1)[1].split(end, 1)[0]
    deferred: list[str] = []

    for line in table.splitlines():
        if not line.startswith("| ") or line.startswith("| ---"):
            continue
        columns = [column.strip() for column in line.strip("|").split("|")]
        if columns[0] == "API or area":
            continue
        deferred.append(columns[0].strip("`"))

    return deferred


def _v1_stable_candidate_apis(path: Path) -> set[str]:
    text = path.read_text(encoding="utf-8")
    start = "## Stable API Candidate"
    end = "The pre-v1 experimental API is public"
    table = text.split(start, 1)[1].split(end, 1)[0]
    return set(re.findall(r"`st\.([a-z_]+|__version__)`", table))


def _v1_experimental_mentions(path: Path) -> set[str]:
    text = path.read_text(encoding="utf-8")
    start = "Experimental or intentionally modest before v1:"
    end = "## Stable API Candidate"
    section = text.split(start, 1)[1].split(end, 1)[0]
    return set(re.findall(r"`st\.([a-z_]+)`", section))


def _readme_api_rows(path: Path) -> list[tuple[list[str], str]]:
    text = path.read_text(encoding="utf-8")
    table_match = re.search(
        r"\| Area \| APIs \| Status in v[0-9.]+ \|(?P<table>.*?)"
        r"Inputs support stable `key` values",
        text,
        flags=re.S,
    )
    assert table_match is not None
    table = table_match.group("table")
    rows: list[tuple[list[str], str]] = []

    for line in table.splitlines():
        if not line.startswith("| ") or line.startswith("| ---"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != 3:
            continue
        apis = [
            name.removeprefix("st.")
            for name in re.findall(r"`st\.([a-z_]+)`", cells[1])
        ]
        if apis:
            rows.append((apis, cells[2].lower()))

    return rows


def test_public_all_exports_are_intentional() -> None:
    assert st.__all__ == EXPECTED_PUBLIC_EXPORTS


def test_import_stui_as_st_exposes_only_intended_public_exports() -> None:
    for name in EXPECTED_PUBLIC_EXPORTS:
        assert hasattr(st, name), name

    for name in PRIVATE_INTERNAL_NAMES:
        assert name not in st.__all__, name

    for name in st.__all__:
        obj = getattr(st, name)
        assert not inspect.isclass(obj), name


def test_star_import_only_exports_public_contract() -> None:
    namespace: dict[str, object] = {}
    exec("from stui import *", namespace)

    assert set(namespace) - {"__builtins__"} == set(EXPECTED_PUBLIC_EXPORTS)


def test_public_exports_match_documented_api_classification() -> None:
    stability_doc = _documented_api_classifications(ROOT / "docs/api-stability.md")
    reference_doc = _documented_api_classifications(ROOT / "docs/api-reference.md")

    assert stability_doc == EXPECTED_API_CLASSIFICATIONS
    assert reference_doc == EXPECTED_API_CLASSIFICATIONS
    assert set(st.__all__) == set(stability_doc)


def test_v1_readiness_stable_table_matches_stable_classification() -> None:
    stable_candidates = _v1_stable_candidate_apis(ROOT / "docs/v1-readiness.md")

    assert stable_candidates == EXPECTED_STABLE_APIS
    assert stable_candidates.isdisjoint(EXPECTED_EXPERIMENTAL_APIS)


def test_experimental_freeze_decisions_are_documented() -> None:
    readiness_mentions = _v1_experimental_mentions(ROOT / "docs/v1-readiness.md")

    assert EXPECTED_EXPERIMENTAL_FREEZE_DECISIONS <= EXPECTED_EXPERIMENTAL_APIS
    assert EXPECTED_EXPERIMENTAL_FREEZE_DECISIONS <= readiness_mentions


def test_deferred_v1_api_areas_are_explicit() -> None:
    deferred = _documented_deferred_api_areas(ROOT / "docs/api-stability.md")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    reference = (ROOT / "docs/api-reference.md").read_text(encoding="utf-8")
    readiness = (ROOT / "docs/v1-readiness.md").read_text(encoding="utf-8")

    assert deferred == EXPECTED_DEFERRED_API_AREAS
    for area in EXPECTED_DEFERRED_API_AREAS:
        assert area in readme
        assert area in reference
        assert area in readiness


def test_readme_api_table_matches_public_api_stability_labels() -> None:
    rows = _readme_api_rows(ROOT / "README.md")
    documented = {api for apis, _status in rows for api in apis}
    assert documented == set(st.__all__)

    for apis, status in rows:
        classifications = {EXPECTED_API_CLASSIFICATIONS[api] for api in apis}
        if "pre-v1 experimental" in classifications:
            assert "experimental" in status, apis
        if classifications == {"v1-stable"}:
            assert "v1-stable" in status, apis


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
