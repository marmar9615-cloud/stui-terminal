import pytest

from stui.session_state import SessionState


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
