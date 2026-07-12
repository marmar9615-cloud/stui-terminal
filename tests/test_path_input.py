from __future__ import annotations

import asyncio
import builtins
import importlib
import importlib.util
import inspect
import os
from pathlib import Path

import pytest

from stui.app import StuiApp
from stui.elements import ErrorElement, PathInputElement, WriteElement
from stui.runtime import Runtime

app_module = importlib.import_module("stui.app")
path_input_module = importlib.import_module("stui.path_input")


def write_script(tmp_path: Path, body: str) -> Path:
    script = tmp_path / "app.py"
    script.write_text(body, encoding="utf-8")
    return script


def path_input_elements(runtime: Runtime) -> list[PathInputElement]:
    return [
        element
        for element in runtime.elements
        if isinstance(element, PathInputElement)
    ]


def rendered_texts(runtime: Runtime) -> list[str]:
    return [
        element.text
        for element in runtime.elements
        if isinstance(element, WriteElement)
    ]


def test_path_input_module_exists() -> None:
    assert importlib.util.find_spec("stui.path_input") is not None


def test_path_input_signature_keeps_the_experimental_contract() -> None:
    path_input = getattr(path_input_module, "path_input", None)

    assert callable(path_input)
    signature = inspect.signature(path_input)
    assert list(signature.parameters) == [
        "label",
        "value",
        "root",
        "kind",
        "must_exist",
        "extensions",
        "browse",
        "key",
        "disabled",
        "on_change",
        "args",
        "kwargs",
    ]
    assert signature.parameters["value"].default == ""
    assert signature.parameters["root"].default is None
    assert signature.parameters["kind"].default == "any"
    assert signature.parameters["must_exist"].default is False
    assert signature.parameters["extensions"].default is None
    assert signature.parameters["browse"].default is True


def test_relative_value_and_root_resolve_from_the_app_script_directory(
    tmp_path: Path,
) -> None:
    workspace = tmp_path / "workspace"
    target = workspace / "space λ" / "report.TXT"
    target.parent.mkdir(parents=True)
    target.touch()
    script = write_script(
        tmp_path,
        '''
import stui as st
from stui.path_input import path_input

value = path_input(
    "Artifact",
    "space λ/./report.TXT",
    root="workspace",
    kind="file",
    must_exist=True,
    extensions=["txt"],
    browse=False,
    key="artifact",
)
st.write(value)
''',
    )
    runtime = Runtime(script)

    runtime.run_script()

    expected = str(target)
    assert runtime.session_state["artifact"] == expected
    assert rendered_texts(runtime) == [expected]
    element = path_input_elements(runtime)[0]
    assert element.label == "Artifact"
    assert element.value == expected
    assert element.root == str(workspace)
    assert element.kind == "file"
    assert element.must_exist is True
    assert element.extensions == (".txt",)
    assert element.browse is False
    assert element.validation_error is None


def test_tilde_expands_but_environment_variables_remain_literal(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("STUI_PATH_ROOT", "expanded-by-mistake")
    script = write_script(
        tmp_path,
        '''
import stui as st
from stui.path_input import path_input

home_value = path_input("Home", "~/notes.txt", root="ignored", key="home")
literal_value = path_input(
    "Literal env",
    "$STUI_PATH_ROOT/report.txt",
    root="workspace",
    key="literal",
)
st.write(home_value)
st.write(literal_value)
''',
    )
    runtime = Runtime(script)

    runtime.run_script()

    assert rendered_texts(runtime) == [
        str(home / "notes.txt"),
        str(tmp_path / "workspace" / "$STUI_PATH_ROOT" / "report.txt"),
    ]


def test_absolute_values_tilde_roots_and_literal_environment_roots(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    home = tmp_path / "home"
    home.mkdir()
    absolute = tmp_path / "absolute.txt"
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("STUI_PATH_ROOT", "expanded-by-mistake")
    runtime = Runtime(
        write_script(
            tmp_path,
            f'''
import stui as st
from pathlib import Path
from stui.path_input import path_input

st.write(path_input("Absolute", {str(absolute)!r}, root="ignored"))
st.write(path_input("Home root", "report.txt", root=Path("~/workspace")))
st.write(path_input("Literal root", "report.txt", root="$STUI_PATH_ROOT"))
''',
        )
    )

    runtime.run_script()

    assert rendered_texts(runtime) == [
        str(absolute),
        str(home / "workspace" / "report.txt"),
        str(tmp_path / "$STUI_PATH_ROOT" / "report.txt"),
    ]


def test_generated_keys_are_stable_and_escape_label_controls(
    tmp_path: Path,
) -> None:
    runtime = Runtime(
        write_script(
            tmp_path,
            r'''
from stui.path_input import path_input

path_input("Artifact\n")
path_input("Artifact\n")
''',
        )
    )

    first = runtime.run_script()
    second = runtime.run_script()

    assert [
        element.key for element in first if isinstance(element, PathInputElement)
    ] == [
        "path_input:Artifact\\x0a:0",
        "path_input:Artifact\\x0a:1",
    ]
    assert [
        element.key for element in second if isinstance(element, PathInputElement)
    ] == [
        "path_input:Artifact\\x0a:0",
        "path_input:Artifact\\x0a:1",
    ]


def test_root_is_a_resolution_base_not_a_sandbox(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        '''
import stui as st
from stui.path_input import path_input

value = path_input(
    "Outside",
    "../../outside.txt",
    root="workspace/inside",
    key="outside",
)
st.write(value)
''',
    )
    runtime = Runtime(script)

    runtime.run_script()

    assert runtime.session_state["outside"] == str(tmp_path / "outside.txt")
    assert rendered_texts(runtime) == [str(tmp_path / "outside.txt")]


def test_empty_and_missing_paths_have_readable_validation_states(
    tmp_path: Path,
) -> None:
    script = write_script(
        tmp_path,
        '''
from stui.path_input import path_input

path_input("Optional", key="optional")
path_input("Required", must_exist=True, key="required")
path_input("Missing", "missing.txt", must_exist=True, key="missing")
path_input(
    "Allowed missing",
    "future.txt",
    kind="file",
    must_exist=False,
    extensions="TXT",
    key="future",
)
''',
    )
    runtime = Runtime(script)

    runtime.run_script()

    elements = path_input_elements(runtime)
    assert [element.value for element in elements] == [
        "",
        "",
        str(tmp_path / "missing.txt"),
        str(tmp_path / "future.txt"),
    ]
    assert [element.validation_error for element in elements] == [
        None,
        "Path is required.",
        "Path does not exist.",
        None,
    ]


@pytest.mark.parametrize(
    ("kind", "value_name", "extensions", "expected_error"),
    [
        ("file", "folder", None, "Path must be a file."),
        ("directory", "report.txt", None, "Path must be a directory."),
        (
            "file",
            "report.txt",
            ["md", "rst"],
            "File extension must be one of: .md, .rst.",
        ),
    ],
)
def test_existing_paths_validate_kind_and_extensions(
    tmp_path: Path,
    kind: str,
    value_name: str,
    extensions: list[str] | None,
    expected_error: str,
) -> None:
    (tmp_path / "folder").mkdir()
    (tmp_path / "report.txt").touch()
    script = write_script(
        tmp_path,
        f'''
from stui.path_input import path_input

path_input(
    "Target",
    {value_name!r},
    kind={kind!r},
    must_exist=True,
    extensions={extensions!r},
)
''',
    )
    runtime = Runtime(script)

    runtime.run_script()

    assert path_input_elements(runtime)[0].validation_error == expected_error


def test_extensions_are_case_insensitive_deduplicated_and_portable(
    tmp_path: Path,
) -> None:
    target = tmp_path / "REPORT.TXT"
    target.touch()
    script = write_script(
        tmp_path,
        '''
from stui.path_input import path_input

path_input(
    "Report",
    "REPORT.TXT",
    kind="file",
    extensions=["TXT", "*.md", ".txt"],
)
''',
    )
    runtime = Runtime(script)

    runtime.run_script()

    element = path_input_elements(runtime)[0]
    assert element.extensions == (".txt", ".md")
    assert element.validation_error is None
    assert (
        path_input_module._validation_error(
            r"C:\Users\Ada\REPORT.TXT",
            kind="file",
            must_exist=False,
            extensions=(".txt",),
        )
        is None
    )


def test_any_kind_does_not_apply_file_extensions_to_directories(
    tmp_path: Path,
) -> None:
    (tmp_path / "folder.txt").mkdir()
    runtime = Runtime(
        write_script(
            tmp_path,
            '''
from stui.path_input import path_input

path_input("Folder", "folder.txt", kind="any", extensions=["md"])
''',
        )
    )

    runtime.run_script()

    assert path_input_elements(runtime)[0].validation_error is None


def test_symlink_text_is_preserved_and_deleted_targets_revalidate(
    tmp_path: Path,
) -> None:
    target = tmp_path / "target.txt"
    target.touch()
    link = tmp_path / "link.txt"
    try:
        link.symlink_to(target)
    except (NotImplementedError, OSError):
        pytest.skip("symlinks are unavailable on this platform")
    runtime = Runtime(
        write_script(
            tmp_path,
            '''
from stui.path_input import path_input

path_input("Link", "link.txt", kind="file", must_exist=True, key="link")
''',
        )
    )

    runtime.run_script()

    element = path_input_elements(runtime)[0]
    assert element.value == str(link)
    assert element.validation_error is None

    target.unlink()
    runtime.run_script()

    element = path_input_elements(runtime)[0]
    assert element.value == str(link)
    assert element.validation_error == "Path does not exist."


def test_unreadable_paths_have_an_inline_validation_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = tmp_path / "private.txt"
    target.touch()
    real_access = os.access

    def fake_access(path: object, mode: int) -> bool:
        if os.fspath(path) == str(target):
            return False
        return real_access(path, mode)

    monkeypatch.setattr(path_input_module.os, "access", fake_access)
    runtime = Runtime(
        write_script(
            tmp_path,
            '''
from stui.path_input import path_input

path_input("Private", "private.txt", must_exist=True)
''',
        )
    )

    runtime.run_script()

    assert path_input_elements(runtime)[0].validation_error == (
        "Path is not readable."
    )


@pytest.mark.parametrize(
    ("call", "message"),
    [
        (
            'path_input("Bad kind", kind="device")',
            "st.path_input kind must be 'file', 'directory', or 'any'.",
        ),
        (
            'path_input("Bad extensions", extensions=["txt", 3])',
            "st.path_input extensions must contain file extensions.",
        ),
        (
            'path_input("Bad browse", browse="yes")',
            "st.path_input browse must be a boolean.",
        ),
        (
            'path_input("Bad existence", must_exist="yes")',
            "st.path_input must_exist must be a boolean.",
        ),
    ],
)
def test_invalid_configuration_renders_a_readable_api_error(
    tmp_path: Path,
    call: str,
    message: str,
) -> None:
    runtime = Runtime(
        write_script(
            tmp_path,
            f'''from stui.path_input import path_input

{call}
''',
        )
    )

    runtime.run_script()

    assert runtime.elements == [ErrorElement(message)]


def test_callback_receives_normalized_state_before_it_runs(tmp_path: Path) -> None:
    runtime = Runtime(
        write_script(
            tmp_path,
            '''
import stui as st
from stui.path_input import path_input

if "events" not in st.session_state:
    st.session_state.events = []

def record(key, *, prefix):
    st.session_state.events.append(f"{prefix}:{st.session_state[key]}")

value = path_input(
    "Report",
    "first.txt",
    key="report",
    on_change=record,
    args=("report",),
    kwargs={"prefix": "path"},
)
st.write(value)
''',
        )
    )
    runtime.run_script()

    runtime.set_widget_value("report", "nested/../second.txt")
    runtime.run_script()

    expected = str(tmp_path / "second.txt")
    assert runtime.session_state["report"] == expected
    assert runtime.session_state["events"] == [f"path:{expected}"]
    assert rendered_texts(runtime) == [expected]


def test_disabled_path_input_ignores_pending_changes(tmp_path: Path) -> None:
    runtime = Runtime(
        write_script(
            tmp_path,
            '''
import stui as st
from stui.path_input import path_input

if "events" not in st.session_state:
    st.session_state.events = []

value = path_input(
    "Locked",
    "initial.txt",
    key="locked",
    disabled=True,
    on_change=lambda: st.session_state.events.append("changed"),
)
st.write(value)
''',
        )
    )
    runtime.run_script()
    expected = str(tmp_path / "initial.txt")

    runtime.set_widget_value("locked", "ignored.txt")
    runtime.run_script()

    assert runtime.session_state["locked"] == expected
    assert runtime.session_state["events"] == []
    assert rendered_texts(runtime) == [expected]
    assert path_input_elements(runtime)[0].disabled is True


def test_form_value_and_callback_remain_pending_until_submit(
    tmp_path: Path,
) -> None:
    runtime = Runtime(
        write_script(
            tmp_path,
            '''
import stui as st
from stui.path_input import path_input

if "events" not in st.session_state:
    st.session_state.events = []

def record(key):
    st.session_state.events.append(st.session_state[key])

with st.form("workspace"):
    value = path_input(
        "Artifact",
        "draft.txt",
        key="artifact",
        on_change=record,
        args=("artifact",),
    )
    submitted = st.form_submit_button("Save")

st.write(value)
st.write(submitted)
''',
        )
    )
    runtime.run_script()

    runtime.set_widget_value("artifact", "nested/../final.txt")
    runtime.run_script()

    expected = str(tmp_path / "final.txt")
    assert rendered_texts(runtime) == [expected, "False"]
    assert "artifact" not in runtime.session_state
    assert runtime.session_state["events"] == []

    runtime.press_button("form_submit_button:workspace:Save:0")
    runtime.run_script()

    assert runtime.session_state["artifact"] == expected
    assert runtime.session_state["events"] == [expected]
    assert rendered_texts(runtime) == [expected, "True"]


def test_controls_are_neutralized_before_state_and_callbacks(tmp_path: Path) -> None:
    runtime = Runtime(
        write_script(
            tmp_path,
            r'''
import stui as st
from stui.path_input import path_input

if "events" not in st.session_state:
    st.session_state.events = []

def record():
    st.session_state.events.append(st.session_state["path"])

path_input("Path\x1b[2J\n\t", key="path", on_change=record)
''',
        )
    )
    runtime.run_script()
    raw_value = "safe\x1b[2J\n\t\x9b0m\x7f.txt"

    runtime.set_widget_value("path", raw_value)
    runtime.run_script()

    expected = str(tmp_path / "safe\\x1b[2J\\x0a\\x09\\x9b0m\\x7f.txt")
    element = path_input_elements(runtime)[0]
    assert runtime.session_state["path"] == expected
    assert runtime.session_state["events"] == [expected]
    assert element.label == "Path\\x1b[2J\\x0a\\x09"
    assert element.value == expected
    controls = ("\x1b", "\n", "\t", "\x9b", "\x7f")
    assert all(control not in element.value for control in controls)


def test_validation_never_opens_the_selected_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = tmp_path / "artifact.txt"
    target.touch()

    def fail_open(*args: object, **kwargs: object) -> object:
        raise AssertionError("path validation must not open file content")

    monkeypatch.setattr(builtins, "open", fail_open)

    assert (
        path_input_module._validation_error(
            str(target),
            kind="file",
            must_exist=True,
            extensions=(".txt",),
        )
        is None
    )


def test_text_renderer_is_safe_editable_and_bounded_in_a_narrow_terminal(
    tmp_path: Path,
) -> None:
    target = tmp_path / "initial.txt"
    target.touch()
    runtime = Runtime(
        write_script(
            tmp_path,
            '''
from stui.path_input import path_input

path_input(
    "Workspace artifact with a deliberately long label",
    "initial.txt",
    kind="file",
    must_exist=True,
    key="artifact",
)
''',
        )
    )
    widget_type = getattr(app_module, "StuiPathInput", None)

    assert widget_type is not None

    async def scenario() -> None:
        app = StuiApp(runtime)
        async with app.run_test(headless=True, size=(24, 14)) as pilot:
            await pilot.pause()
            path_widget = app.query_one(widget_type)
            assert path_widget.value == str(target)
            assert path_widget.region.right <= app.size.width

            osc52 = "\x1b]52;c;U1RVSS1QQVRI\x1b\\"
            path_widget.replace(osc52, 0, len(path_widget.value))
            assert osc52 not in path_widget.value
            assert path_widget.value == "\\x1b]52;c;U1RVSS1QQVRI\\x1b\\"

            path_widget.value = "nested/../missing.txt"
            app.set_focus(path_widget)
            await pilot.press("enter")
            await pilot.pause()

            expected = str(tmp_path / "missing.txt")
            restored = app.query_one(widget_type)
            error = app.query_one(".stui-path-error")
            assert runtime.session_state["artifact"] == expected
            assert restored.value == expected
            assert app.focused is restored
            assert restored.region.right <= app.size.width
            assert "Path does not exist." in str(error.content)

    asyncio.run(scenario())
