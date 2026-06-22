import pytest

from stui.runtime import Runtime
from stui.session_state import SessionState


def write_script(tmp_path, body: str):
    script = tmp_path / "app.py"
    script.write_text(body, encoding="utf-8")
    return script


def test_session_state_supports_dict_access() -> None:
    state = SessionState()

    state["count"] = 3

    assert state["count"] == 3
    assert "count" in state
    assert dict(state.items()) == {"count": 3}


def test_session_state_supports_attribute_access() -> None:
    state = SessionState()

    state.count = 7

    assert state["count"] == 7
    assert state.count == 7


def test_missing_attribute_raises_attribute_error() -> None:
    state = SessionState()

    with pytest.raises(AttributeError):
        _ = state.missing


def test_top_level_session_state_proxy_supports_public_mapping_contract(
    tmp_path,
) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

st.session_state["count"] = st.session_state.get("count", 0) + 1
st.session_state.name = "Ada"
st.session_state["mode"] = "fast"

st.write("count", st.session_state["count"])
st.write("name", st.session_state.name)
st.write("contains", "mode" in st.session_state)
st.write("len", len(st.session_state))
st.write("keys", sorted(st.session_state.keys()))
st.write("values", sorted(str(value) for value in st.session_state.values()))
st.write("items", sorted((key, str(value)) for key, value in st.session_state.items()))
st.write("iter", sorted(iter(st.session_state)))
""",
    )
    runtime = Runtime(script)

    elements = runtime.run_script()
    rendered = [element.text for element in elements]

    assert rendered == [
        "count 1",
        "name Ada",
        "contains True",
        "len 3",
        "keys ['count', 'mode', 'name']",
        "values ['1', 'Ada', 'fast']",
        "items [('count', '1'), ('mode', 'fast'), ('name', 'Ada')]",
        "iter ['count', 'mode', 'name']",
    ]
