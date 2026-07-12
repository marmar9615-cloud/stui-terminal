from __future__ import annotations

import inspect
import re
import tomllib
from pathlib import Path

import stui as st

ROOT = Path(__file__).resolve().parents[1]


def _sig(*parts: str) -> str:
    return "".join(parts)


EXPECTED_PUBLIC_EXPORTS = [
    "__version__",
    "button",
    "bar_chart",
    "cache_data",
    "cache_resource",
    "caption",
    "checkbox",
    "code",
    "columns",
    "container",
    "data_table",
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
    "multiselect",
    "number_input",
    "path_input",
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
    "tabs",
    "table",
    "success",
    "text",
    "text_area",
    "text_input",
    "title",
    "toast",
    "toggle",
    "warning",
    "write",
]

EXPECTED_API_CLASSIFICATIONS = {
    "__version__": "v1-stable",
    "bar_chart": "v1-stable",
    "button": "v1-stable",
    "cache_data": "v1-stable",
    "cache_resource": "v1-stable",
    "caption": "v1-stable",
    "checkbox": "v1-stable",
    "code": "v1-stable",
    "columns": "v1-stable",
    "container": "v1-stable",
    "data_table": "post-v2 experimental",
    "dataframe": "v1-stable",
    "divider": "v1-stable",
    "error": "v1-stable",
    "exception": "v1-stable",
    "expander": "v1-stable",
    "form": "v1-stable",
    "form_submit_button": "v1-stable",
    "header": "v1-stable",
    "help": "post-v1 experimental",
    "info": "v1-stable",
    "json": "v1-stable",
    "line_chart": "v1-stable",
    "markdown": "v1-stable",
    "metric": "v1-stable",
    "multiselect": "post-v2 experimental",
    "number_input": "v1-stable",
    "path_input": "post-v2 experimental",
    "progress": "v1-stable",
    "radio": "v1-stable",
    "rerun": "v1-stable",
    "selectbox": "v1-stable",
    "session_state": "v1-stable",
    "slider": "v1-stable",
    "spinner": "post-v1 experimental",
    "stop": "v1-stable",
    "subheader": "v1-stable",
    "status": "post-v1 experimental",
    "tabs": "post-v2 experimental",
    "success": "v1-stable",
    "table": "v1-stable",
    "text": "v1-stable",
    "text_area": "v1-stable",
    "text_input": "v1-stable",
    "title": "v1-stable",
    "toast": "post-v2 experimental",
    "toggle": "v1-stable",
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
    if classification.endswith("experimental")
}

EXPECTED_EXPERIMENTAL_FREEZE_DECISIONS = {
    "help",
    "spinner",
    "status",
}

EXPECTED_DEFERRED_API_AREAS = [
    "st.sidebar",
    "st.file_uploader",
    "st.components",
    "st.empty",
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
    "cache_data": _sig(
        "(func: 'Callable[P, T] | None' = None, *, ",
        "ttl: 'int | float | None' = None, ",
        "max_entries: 'int | None' = None)",
    ),
    "cache_resource": _sig(
        "(func: 'Callable[P, T] | None' = None, *, ",
        "ttl: 'int | float | None' = None, ",
        "max_entries: 'int | None' = None)",
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
    "data_table": _sig(
        "(data: 'Any', *, selection_mode: 'str | None' = None, ",
        "key: 'str | None' = None, disabled: 'bool' = False, ",
        "on_select=None, args: 'tuple[Any, ...] | None' = None, ",
        "kwargs: 'dict[str, Any] | None' = None, ",
        "max_rows: 'int | None' = None, max_cols: 'int | None' = None, ",
        "height: 'int | None' = None, show_index: 'bool' = False) ",
        "-> 'int | None'",
    ),
    "dataframe": _sig(
        "(data: 'Any', *, max_rows: 'int | None' = None, ",
        "max_cols: 'int | None' = None) -> 'None'",
    ),
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
    "multiselect": _sig(
        "(label: 'str', options, default: 'Any' = None, *, ",
        "key: 'str | None' = None, disabled: 'bool' = False, ",
        "on_change=None, args: 'tuple[Any, ...] | None' = None, ",
        "kwargs: 'dict[str, Any] | None' = None) -> 'tuple[Any, ...]'",
    ),
    "number_input": _sig(
        "(label: 'str', min_value: 'int | float | None' = None, ",
        "max_value: 'int | float | None' = None, ",
        "value: 'int | float' = 0, step: 'int | float' = 1, *, ",
        "key: 'str | None' = None, disabled: 'bool' = False, ",
        "on_change=None, args: 'tuple[Any, ...] | None' = None, ",
        "kwargs: 'dict[str, Any] | None' = None) -> 'int | float'",
    ),
    "path_input": _sig(
        "(label: 'str', value: 'str' = '', *, ",
        "root: 'str | PathLike[str] | None' = None, ",
        "kind: 'PathKind' = 'any', must_exist: 'bool' = False, ",
        "extensions: 'str | Iterable[str] | None' = None, ",
        "browse: 'bool' = True, key: 'str | None' = None, ",
        "disabled: 'bool' = False, ",
        "on_change: 'Callable[..., Any] | None' = None, ",
        "args: 'tuple[Any, ...] | None' = None, ",
        "kwargs: 'dict[str, Any] | None' = None) -> 'str'",
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
    "tabs": _sig(
        "(labels: 'Sequence[str]', *, key: 'str | None' = None, ",
        "default: 'int' = 0, on_change: 'Callable[..., Any] | None' = None, ",
        "args: 'tuple[Any, ...] | None' = None, ",
        "kwargs: 'dict[str, Any] | None' = None) ",
        "-> 'tuple[ElementBlock, ...]'",
    ),
    "success": "(body: 'Any') -> 'None'",
    "table": _sig(
        "(data: 'Any', *, max_rows: 'int | None' = None, ",
        "max_cols: 'int | None' = None) -> 'None'",
    ),
    "text": "(body: 'Any') -> 'None'",
    "text_area": _sig(
        "(label: 'str', value: 'str' = '', *, height: 'int' = 6, ",
        "key: 'str | None' = None, placeholder: 'str | None' = None, ",
        "disabled: 'bool' = False, max_chars: 'int | None' = None, ",
        "on_change=None, args: 'tuple[Any, ...] | None' = None, ",
        "kwargs: 'dict[str, Any] | None' = None) -> 'str'",
    ),
    "text_input": _sig(
        "(label: 'str', value: 'str' = '', *, ",
        "key: 'str | None' = None, placeholder: 'str | None' = None, ",
        "disabled: 'bool' = False, on_change=None, ",
        "args: 'tuple[Any, ...] | None' = None, ",
        "kwargs: 'dict[str, Any] | None' = None) -> 'str'",
    ),
    "title": "(body: 'Any', *, key: 'str | None' = None) -> 'None'",
    "toast": "(body: 'Any') -> 'None'",
    "toggle": _sig(
        "(label: 'str', value: 'bool' = False, *, ",
        "key: 'str | None' = None, disabled: 'bool' = False, ",
        "on_change=None, args: 'tuple[Any, ...] | None' = None, ",
        "kwargs: 'dict[str, Any] | None' = None) -> 'bool'",
    ),
    "warning": "(body: 'Any') -> 'None'",
    "write": "(*args: 'Any') -> 'None'",
}

EXPECTED_REFERENCE_SIGNATURES = {
    "bar_chart": "st.bar_chart(data, *, width=None, height=None) -> None",
    "button": _sig(
        "st.button(\n    label,\n    key=None,\n    help=None,\n    disabled=False,\n",
        "    on_click=None,\n    args=None,\n    kwargs=None,\n) -> bool",
    ),
    "cache_data": "st.cache_data(func=None, *, ttl=None, max_entries=None)",
    "cache_resource": "st.cache_resource(func=None, *, ttl=None, max_entries=None)",
    "caption": "st.caption(body) -> None",
    "checkbox": _sig(
        "st.checkbox(\n    label,\n    value=False,\n    *,\n    key=None,\n",
        "    disabled=False,\n    on_change=None,\n    args=None,\n",
        "    kwargs=None,\n) -> bool",
    ),
    "code": "st.code(body, language=None) -> None",
    "columns": "st.columns(count)",
    "container": "st.container()",
    "data_table": _sig(
        "st.data_table(\n    data,\n    *,\n    selection_mode=None,\n",
        "    key=None,\n    disabled=False,\n    on_select=None,\n",
        "    args=None,\n    kwargs=None,\n    max_rows=None,\n",
        "    max_cols=None,\n    height=None,\n    show_index=False,\n",
        ") -> int | None",
    ),
    "dataframe": "st.dataframe(data, *, max_rows=None, max_cols=None) -> None",
    "divider": "st.divider() -> None",
    "error": "st.error(body) -> None",
    "exception": "st.exception(exc) -> None",
    "expander": "st.expander(label, expanded=False, *, key=None)",
    "form": "st.form(key)",
    "form_submit_button": _sig(
        "st.form_submit_button(\n    label=\"Submit\",\n    *,\n",
        "    disabled=False,\n    on_click=None,\n    args=None,\n",
        "    kwargs=None,\n) -> bool",
    ),
    "header": "st.header(body, *, key=None) -> None",
    "help": "st.help(obj_or_text) -> None",
    "info": "st.info(body) -> None",
    "json": "st.json(obj) -> None",
    "line_chart": "st.line_chart(data, *, width=None, height=None) -> None",
    "markdown": "st.markdown(body) -> None",
    "metric": "st.metric(label, value, delta=None) -> None",
    "multiselect": _sig(
        "st.multiselect(\n    label,\n    options,\n    default=None,\n    *,\n",
        "    key=None,\n    disabled=False,\n    on_change=None,\n",
        "    args=None,\n    kwargs=None,\n) -> tuple",
    ),
    "number_input": _sig(
        "st.number_input(\n    label,\n    min_value=None,\n    max_value=None,\n",
        "    value=0,\n    step=1,\n    *,\n    key=None,\n",
        "    disabled=False,\n    on_change=None,\n    args=None,\n",
        "    kwargs=None,\n) -> int | float",
    ),
    "path_input": _sig(
        "st.path_input(\n    label,\n    value=\"\",\n    *,\n    root=None,\n",
        "    kind=\"any\",\n    must_exist=False,\n    extensions=None,\n",
        "    browse=True,\n    key=None,\n    disabled=False,\n",
        "    on_change=None,\n    args=None,\n    kwargs=None,\n) -> str",
    ),
    "progress": "st.progress(value, text=None) -> None",
    "radio": _sig(
        "st.radio(\n    label,\n    options,\n    index=0,\n    *,\n",
        "    key=None,\n    disabled=False,\n    on_change=None,\n",
        "    args=None,\n    kwargs=None,\n)",
    ),
    "rerun": "st.rerun() -> None",
    "selectbox": _sig(
        "st.selectbox(\n    label,\n    options,\n    index=0,\n    *,\n",
        "    key=None,\n    disabled=False,\n    on_change=None,\n",
        "    args=None,\n    kwargs=None,\n)",
    ),
    "slider": _sig(
        "st.slider(\n    label,\n    min_value=0,\n    max_value=100,\n",
        "    value=None,\n    step=1,\n    *,\n    key=None,\n",
        "    help=None,\n    disabled=False,\n    on_change=None,\n",
        "    args=None,\n    kwargs=None,\n) -> int | float",
    ),
    "spinner": "st.spinner(text=\"Working...\")",
    "stop": "st.stop() -> None",
    "subheader": "st.subheader(body, *, key=None) -> None",
    "status": "st.status(label, state=\"running\", expanded=False)",
    "tabs": _sig(
        "st.tabs(\n    labels,\n    *,\n    key=None,\n    default=0,\n",
        "    on_change=None,\n    args=None,\n    kwargs=None,\n)",
    ),
    "success": "st.success(body) -> None",
    "table": "st.table(data, *, max_rows=None, max_cols=None) -> None",
    "text": "st.text(body) -> None",
    "text_area": _sig(
        "st.text_area(\n    label,\n    value=\"\",\n    *,\n    height=6,\n",
        "    key=None,\n    placeholder=None,\n    disabled=False,\n",
        "    max_chars=None,\n    on_change=None,\n    args=None,\n",
        "    kwargs=None,\n) -> str",
    ),
    "text_input": _sig(
        "st.text_input(\n    label,\n    value=\"\",\n    *,\n",
        "    key=None,\n    placeholder=None,\n    disabled=False,\n",
        "    on_change=None,\n    args=None,\n    kwargs=None,\n) -> str",
    ),
    "title": "st.title(body, *, key=None) -> None",
    "toast": "st.toast(body) -> None",
    "toggle": _sig(
        "st.toggle(\n    label,\n    value=False,\n    *,\n    key=None,\n",
        "    disabled=False,\n    on_change=None,\n    args=None,\n",
        "    kwargs=None,\n) -> bool",
    ),
    "warning": "st.warning(body) -> None",
    "write": "st.write(*args) -> None",
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
    start = "## Stable API"
    end = "The experimental API is public"
    table = text.split(start, 1)[1].split(end, 1)[0]
    return set(re.findall(r"`st\.([a-z_]+|__version__)`", table))


def _api_mentions_between(path: Path, start: str, end: str) -> set[str]:
    text = path.read_text(encoding="utf-8")
    section = text.split(start, 1)[1].split(end, 1)[0]
    return set(re.findall(r"`st\.([a-z_]+|__version__)`", section))


def _v2_stable_candidate_apis(path: Path) -> set[str]:
    return _api_mentions_between(
        path,
        "## Stable API",
        "## Experimental APIs",
    )


def _v1_experimental_mentions(path: Path) -> set[str]:
    return _api_mentions_between(
        path,
        "Experimental in v1:",
        "## Stable API",
    )


def _v2_experimental_mentions(path: Path) -> set[str]:
    return _api_mentions_between(
        path,
        "## Experimental APIs",
        "## Deferred Roadmap",
    )


def _project_version() -> str:
    data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    return str(data["project"]["version"])


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


def test_top_level_internal_modules_are_not_public_exports() -> None:
    for name in ["api", "app", "cli", "elements", "runtime", "widgets"]:
        assert name not in st.__all__, name


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


def test_v1_readiness_status_list_matches_stable_classification() -> None:
    stable_mentions = _api_mentions_between(
        ROOT / "docs/v1-readiness.md",
        "Stable in v1:",
        "Experimental in v1:",
    )

    assert stable_mentions == EXPECTED_STABLE_APIS
    assert stable_mentions.isdisjoint(EXPECTED_EXPERIMENTAL_APIS)


def test_v2_readiness_matches_public_api_classification() -> None:
    readiness = ROOT / "docs/v2-readiness.md"

    assert _v2_stable_candidate_apis(readiness) == EXPECTED_STABLE_APIS
    assert _v2_experimental_mentions(readiness) == EXPECTED_EXPERIMENTAL_APIS


def test_experimental_freeze_decisions_are_documented() -> None:
    readiness_mentions = _v1_experimental_mentions(ROOT / "docs/v1-readiness.md")
    v2_mentions = _v2_experimental_mentions(ROOT / "docs/v2-readiness.md")

    assert EXPECTED_EXPERIMENTAL_FREEZE_DECISIONS <= EXPECTED_EXPERIMENTAL_APIS
    assert EXPECTED_EXPERIMENTAL_FREEZE_DECISIONS <= readiness_mentions
    assert EXPECTED_EXPERIMENTAL_FREEZE_DECISIONS <= v2_mentions


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
        if any(label.endswith("experimental") for label in classifications):
            assert "experimental" in status, apis
        if classifications == {"v1-stable"}:
            assert "v1-stable" in status, apis


def test_current_release_labels_match_project_version() -> None:
    version = _project_version()
    major_minor = ".".join(version.split(".")[:2])
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    reference = (ROOT / "docs/api-reference.md").read_text(encoding="utf-8")
    stability = (ROOT / "docs/api-stability.md").read_text(encoding="utf-8")
    readiness = (ROOT / "docs/v1-readiness.md").read_text(encoding="utf-8")
    release_notes = (
        ROOT / f"docs/releases/RELEASE_NOTES_v{version}.md"
    ).read_text(encoding="utf-8")

    assert f"Status in v{version}" in readme
    assert f"## v{major_minor} Stable Status" in reference
    assert f"`stui` v{version}" in stability
    assert f"`stui` v{version}" in readiness
    assert f"# stui v{version}" in release_notes


def test_public_api_signatures_are_intentional() -> None:
    signatures = {
        name: str(inspect.signature(getattr(st, name)))
        for name in EXPECTED_PUBLIC_SIGNATURES
    }

    assert signatures == EXPECTED_PUBLIC_SIGNATURES


def test_api_reference_documents_every_frozen_signature() -> None:
    reference = (ROOT / "docs/api-reference.md").read_text(encoding="utf-8")

    assert set(EXPECTED_REFERENCE_SIGNATURES) == set(EXPECTED_PUBLIC_SIGNATURES)
    for name, signature in EXPECTED_REFERENCE_SIGNATURES.items():
        assert signature in reference, name


def test_widget_callback_and_disabled_parameter_names_are_consistent() -> None:
    callback_params = {
        "button": "on_click",
        "form_submit_button": "on_click",
        "checkbox": "on_change",
        "multiselect": "on_change",
        "number_input": "on_change",
        "radio": "on_change",
        "selectbox": "on_change",
        "slider": "on_change",
        "text_area": "on_change",
        "text_input": "on_change",
        "toggle": "on_change",
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
