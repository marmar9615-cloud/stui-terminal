from importlib import resources
from pathlib import Path

from stui.elements import (
    AlertElement,
    ButtonElement,
    CaptionElement,
    CheckboxElement,
    CodeElement,
    DividerElement,
    ErrorElement,
    ExceptionElement,
    HeaderElement,
    JsonElement,
    MarkdownElement,
    NumberInputElement,
    ProgressElement,
    RadioElement,
    SelectboxElement,
    SubheaderElement,
    TableElement,
    TextElement,
    TextInputElement,
    TitleElement,
    WriteElement,
)
from stui.runtime import Runtime


def test_all_examples_run_without_script_errors() -> None:
    for path in sorted(Path("examples").glob("*.py")):
        runtime = Runtime(path)
        elements = runtime.run_script()

        assert not any(isinstance(element, ErrorElement) for element in elements), path


def test_all_bundled_examples_run_without_script_errors() -> None:
    examples = resources.files("stui.examples")
    bundled = sorted(
        child
        for child in examples.iterdir()
        if child.name.endswith(".py") and child.name != "__init__.py"
    )

    assert bundled

    for example in bundled:
        with resources.as_file(example) as path:
            runtime = Runtime(path)
            elements = runtime.run_script()

        assert not any(isinstance(element, ErrorElement) for element in elements), (
            example.name
        )


def test_kitchen_sink_example_runs_all_stable_apis() -> None:
    runtime = Runtime(Path("examples/kitchen_sink.py"))

    elements = runtime.run_script()

    assert not any(isinstance(element, ErrorElement) for element in elements)
    assert {
        TitleElement,
        CaptionElement,
        HeaderElement,
        SubheaderElement,
        TextElement,
        MarkdownElement,
        CodeElement,
        JsonElement,
        ExceptionElement,
        ProgressElement,
        TableElement,
        DividerElement,
        AlertElement,
        WriteElement,
        ButtonElement,
        TextInputElement,
        CheckboxElement,
        NumberInputElement,
        SelectboxElement,
        RadioElement,
    }.issubset({type(element) for element in elements})
    assert sum(isinstance(element, TableElement) for element in elements) == 2
    assert {
        element.kind for element in elements if isinstance(element, AlertElement)
    } == {"info", "success", "warning", "error"}
    assert runtime.session_state["project"] == "stui"
    assert runtime.session_state["preview"] is True
    assert runtime.session_state["batch"] == 8
    assert runtime.session_state["confidence"] == 70
    assert runtime.session_state["model"] == "base"
    assert runtime.session_state["mode"] == "balanced"
    assert runtime.session_state.runs == 0
