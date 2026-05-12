from pathlib import Path

from stui.app import StuiApp, css_for_theme, resolve_theme
from stui.runtime import Runtime


def test_resolve_theme_defaults_for_empty_or_unknown_values() -> None:
    assert resolve_theme("") == "default"
    assert resolve_theme("not-a-theme") == "default"


def test_resolve_theme_accepts_high_contrast_case_insensitively() -> None:
    assert resolve_theme(" HIGH-CONTRAST ") == "high-contrast"


def test_high_contrast_theme_adds_css_overrides() -> None:
    css = css_for_theme("Screen { color: #e8e8ee; }", "high-contrast")

    assert "#ffff00" in css
    assert "Button:focus" in css


def test_app_reads_high_contrast_theme_from_environment(monkeypatch) -> None:
    monkeypatch.setenv("STUI_THEME", "high-contrast")

    app = StuiApp(Runtime(Path("examples/basic.py")))

    assert app.stui_theme == "high-contrast"
    assert "#ffff00" in app.CSS
