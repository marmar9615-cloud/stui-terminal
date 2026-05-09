import pytest

from stui.widgets.slider import snap_value


def test_snap_value_uses_default_int_shape() -> None:
    assert snap_value(10, 0, 100, 1) == 10


def test_snap_value_clamps_to_min_and_max() -> None:
    assert snap_value(-5, 0, 100, 1) == 0
    assert snap_value(105, 0, 100, 1) == 100


def test_snap_value_snaps_to_nearest_step() -> None:
    assert snap_value(13, 0, 100, 5) == 15
    assert snap_value(12, 0, 100, 5) == 10


def test_snap_value_supports_float_steps() -> None:
    assert snap_value(0.26, 0.0, 1.0, 0.1) == pytest.approx(0.3)
    assert snap_value(0.24, 0.0, 1.0, 0.1) == pytest.approx(0.2)


def test_snap_value_rejects_invalid_step() -> None:
    with pytest.raises(ValueError):
        snap_value(1, 0, 10, 0)
