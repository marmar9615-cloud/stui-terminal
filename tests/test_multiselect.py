from pathlib import Path

from stui.elements import MultiselectElement, WriteElement
from stui.runtime import Runtime


def write_script(tmp_path: Path, body: str) -> Path:
    script = tmp_path / "app.py"
    script.write_text(body, encoding="utf-8")
    return script


def multiselect_elements(runtime: Runtime) -> list[MultiselectElement]:
    return [
        element
        for element in runtime.elements
        if isinstance(element, MultiselectElement)
    ]


def test_multiselect_defaults_to_empty_selection(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

tags = st.multiselect("Tags", ["alpha", "beta", "gamma"])
st.write("tags =", tags)
""",
    )
    runtime = Runtime(script)

    runtime.run_script()

    assert runtime.session_state["multiselect:Tags:0"] == ()
    element = multiselect_elements(runtime)[0]
    assert element.options == ("alpha", "beta", "gamma")
    assert element.selected == ()


def test_multiselect_accepts_list_and_single_default(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

many = st.multiselect("Many", ["a", "b", "c"], default=["c", "a"])
one = st.multiselect("One", ["a", "b", "c"], default="b")
st.write(many, one)
""",
    )
    runtime = Runtime(script)

    runtime.run_script()

    assert runtime.session_state["multiselect:Many:0"] == ("a", "c")
    assert runtime.session_state["multiselect:One:0"] == ("b",)


def test_multiselect_selection_persists_and_keeps_options_order(
    tmp_path: Path,
) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

tags = st.multiselect("Tags", ["alpha", "beta", "gamma"])
st.write("tags =", tags)
""",
    )
    runtime = Runtime(script)

    runtime.run_script()
    runtime.set_widget_value("multiselect:Tags:0", ("gamma", "alpha"))
    runtime.run_script()

    assert runtime.session_state["multiselect:Tags:0"] == ("alpha", "gamma")
    write = [
        element
        for element in runtime.elements
        if isinstance(element, WriteElement)
    ][0]
    assert "('alpha', 'gamma')" in write.text


def test_multiselect_drops_values_missing_from_options(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

tags = st.multiselect("Tags", ["alpha", "beta"], default=["alpha", "stale"])
st.write("tags =", tags)
""",
    )
    runtime = Runtime(script)

    runtime.run_script()
    assert runtime.session_state["multiselect:Tags:0"] == ("alpha",)

    runtime.set_widget_value("multiselect:Tags:0", ("beta", "missing"))
    runtime.run_script()
    assert runtime.session_state["multiselect:Tags:0"] == ("beta",)


def test_multiselect_disabled_ignores_pending_changes(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

tags = st.multiselect("Tags", ["alpha", "beta"], default=["alpha"], disabled=True)
st.write("tags =", tags)
""",
    )
    runtime = Runtime(script)

    runtime.run_script()
    runtime.set_widget_value("multiselect:Tags:0", ("beta",))
    runtime.run_script()

    assert runtime.session_state["multiselect:Tags:0"] == ("alpha",)


def test_multiselect_allows_empty_options(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

tags = st.multiselect("Tags", [])
st.write("tags =", tags)
""",
    )
    runtime = Runtime(script)

    runtime.run_script()

    element = multiselect_elements(runtime)[0]
    assert element.options == ()
    assert element.selected == ()
    assert runtime.session_state["multiselect:Tags:0"] == ()


def test_multiselect_on_change_fires_only_on_change(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

if "calls" not in st.session_state:
    st.session_state.calls = 0

def bump():
    st.session_state.calls += 1

tags = st.multiselect("Tags", ["a", "b"], on_change=bump)
st.write(tags)
""",
    )
    runtime = Runtime(script)

    runtime.run_script()
    assert runtime.session_state.calls == 0

    runtime.set_widget_value("multiselect:Tags:0", ("b",))
    runtime.run_script()
    assert runtime.session_state.calls == 1

    runtime.run_script()
    assert runtime.session_state.calls == 1


def test_multiselect_inside_form_defers_until_submit(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

with st.form("prefs"):
    tags = st.multiselect("Tags", ["a", "b", "c"])
    submitted = st.form_submit_button("Save")

st.write("tags =", tags)
""",
    )
    runtime = Runtime(script)

    runtime.run_script()
    runtime.set_widget_value("multiselect:Tags:0", ("b", "c"))
    runtime.run_script()

    assert runtime.session_state.get("multiselect:Tags:0") is None

    runtime.press_button("form_submit_button:prefs:Save:0")
    runtime.run_script()

    assert runtime.session_state["multiselect:Tags:0"] == ("b", "c")
