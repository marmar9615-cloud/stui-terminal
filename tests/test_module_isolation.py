from __future__ import annotations

import importlib
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

import stui.runtime as runtime_module
from stui.elements import TextElement
from stui.runtime import Runtime

MODULE_NAME = "shared_v220_helper"
APP_HELPER_MODULE_NAME = "app_helper_v220"
HOST_MODULE_NAME = "host_core_v220"
OWNED_MODULE_NAME = "owned_helper_v220"
COLLIDING_HOST_MODULE_NAME = "colliding_host_v220"


@pytest.fixture(autouse=True)
def clear_test_module() -> None:
    module_names = {
        MODULE_NAME,
        APP_HELPER_MODULE_NAME,
        HOST_MODULE_NAME,
        OWNED_MODULE_NAME,
        COLLIDING_HOST_MODULE_NAME,
        "plugins",
        "plugins.secrets",
    }
    for module_name in module_names:
        sys.modules.pop(module_name, None)
    yield
    for module_name in module_names:
        sys.modules.pop(module_name, None)


def _rendered_text(runtime: Runtime) -> list[str]:
    return [
        element.body
        for element in runtime.run_script()
        if isinstance(element, TextElement)
    ]


def _write_app(root: Path, value: str) -> Path:
    (root / f"{MODULE_NAME}.py").write_text(
        f"VALUE = {value!r}\n",
        encoding="utf-8",
    )
    script = root / "app.py"
    script.write_text(
        "import stui as st\n"
        f"from {MODULE_NAME} import VALUE\n"
        "st.text(VALUE)\n",
        encoding="utf-8",
    )
    return script


def _write_nested_project_app(root: Path, value: str) -> tuple[Path, Path]:
    root.mkdir()
    (root / "pyproject.toml").write_text(
        "[project]\nname = 'nested-app'\nversion = '0.0.0'\n",
        encoding="utf-8",
    )
    helper = root / f"{MODULE_NAME}.py"
    helper.write_text(f"VALUE = {value!r}\n", encoding="utf-8")
    app_dir = root / "apps"
    app_dir.mkdir()
    script = app_dir / "app.py"
    script.write_text(
        "import sys\n"
        "from pathlib import Path\n"
        "sys.path.insert(0, str(Path(__file__).parent.parent))\n"
        "import stui as st\n"
        f"from {MODULE_NAME} import VALUE\n"
        "st.text(VALUE)\n",
        encoding="utf-8",
    )
    return script, helper


def _write_package_app(root: Path, value: str, *, namespace: bool) -> Path:
    package = root / "plugins"
    package.mkdir()
    if not namespace:
        (package / "__init__.py").write_text("", encoding="utf-8")
    (package / "secrets.py").write_text(
        f"VALUE = {value!r}\n",
        encoding="utf-8",
    )
    script = root / "app.py"
    script.write_text(
        "import stui as st\n"
        "from plugins.secrets import VALUE\n"
        "st.text(VALUE)\n",
        encoding="utf-8",
    )
    return script


def test_separate_apps_do_not_reuse_same_named_local_module(tmp_path: Path) -> None:
    first_root = tmp_path / "first"
    second_root = tmp_path / "second"
    first_root.mkdir()
    second_root.mkdir()
    first = Runtime(_write_app(first_root, "first"))
    second = Runtime(_write_app(second_root, "second"))

    assert _rendered_text(first) == ["first"]
    assert _rendered_text(second) == ["second"]
    assert _rendered_text(first) == ["first"]


def test_nested_apps_in_separate_projects_use_their_root_module(
    tmp_path: Path,
) -> None:
    first_script, first_helper = _write_nested_project_app(
        tmp_path / "first-project",
        "first project",
    )
    second_script, second_helper = _write_nested_project_app(
        tmp_path / "second-project",
        "second project",
    )
    first = Runtime(first_script)
    second = Runtime(second_script)

    assert _rendered_text(first) == ["first project"]
    assert Path(sys.modules[MODULE_NAME].__file__).resolve() == first_helper.resolve()
    assert _rendered_text(second) == ["second project"]
    assert Path(sys.modules[MODULE_NAME].__file__).resolve() == second_helper.resolve()


def test_project_marker_extends_local_watch_boundary(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\nname='demo'\n")
    helper = tmp_path / f"{MODULE_NAME}.py"
    helper.write_text("VALUE = 'root helper'\n", encoding="utf-8")
    app_dir = tmp_path / "apps"
    app_dir.mkdir()
    script = app_dir / "app.py"
    script.write_text(
        "import sys\n"
        "from pathlib import Path\n"
        "sys.path.insert(0, str(Path(__file__).parent.parent))\n"
        "import stui as st\n"
        f"from {MODULE_NAME} import VALUE\n"
        "st.text(VALUE)\n",
        encoding="utf-8",
    )
    runtime = Runtime(script)

    assert _rendered_text(runtime) == ["root helper"]
    assert runtime.project_root == tmp_path.resolve()
    assert helper.resolve() in runtime.watched_source_paths


def test_sibling_apps_under_one_project_do_not_share_local_modules(
    tmp_path: Path,
) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\nname='demo'\n")
    first_root = tmp_path / "first"
    second_root = tmp_path / "second"
    first_root.mkdir()
    second_root.mkdir()
    first = Runtime(_write_app(first_root, "first"))
    second = Runtime(_write_app(second_root, "second"))

    assert first.project_root == tmp_path.resolve()
    assert second.project_root == tmp_path.resolve()
    assert _rendered_text(first) == ["first"]
    assert _rendered_text(second) == ["second"]


def test_separate_apps_do_not_reuse_same_named_namespace_package(
    tmp_path: Path,
) -> None:
    first_root = tmp_path / "first"
    second_root = tmp_path / "second"
    first_root.mkdir()
    second_root.mkdir()
    first = Runtime(
        _write_package_app(first_root, "first namespace", namespace=True)
    )
    second = Runtime(
        _write_package_app(second_root, "second namespace", namespace=True)
    )

    assert _rendered_text(first) == ["first namespace"]
    assert _rendered_text(second) == ["second namespace"]
    assert _rendered_text(first) == ["first namespace"]


def test_regular_packages_keep_existing_cross_app_isolation(tmp_path: Path) -> None:
    first_root = tmp_path / "first"
    second_root = tmp_path / "second"
    first_root.mkdir()
    second_root.mkdir()
    first = Runtime(_write_package_app(first_root, "first package", namespace=False))
    second = Runtime(
        _write_package_app(second_root, "second package", namespace=False)
    )

    assert _rendered_text(first) == ["first package"]
    assert _rendered_text(second) == ["second package"]


def test_unrelated_third_party_module_is_not_evicted(tmp_path: Path) -> None:
    root = tmp_path / "app"
    root.mkdir()
    runtime = Runtime(_write_app(root, "ready"))
    pytest_module = sys.modules["pytest"]

    assert _rendered_text(runtime) == ["ready"]
    assert sys.modules["pytest"] is pytest_module


def test_runtime_does_not_claim_or_evict_preloaded_host_module(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = tmp_path / "project"
    app_dir = project / "apps"
    app_dir.mkdir(parents=True)
    (project / "pyproject.toml").write_text(
        "[project]\nname = 'embedded-app'\nversion = '0.0.0'\n",
        encoding="utf-8",
    )
    host_path = project / f"{HOST_MODULE_NAME}.py"
    host_path.write_text(
        "STATE = {'bootstrap'}\nSINGLETON = object()\n",
        encoding="utf-8",
    )
    helper_path = app_dir / f"{APP_HELPER_MODULE_NAME}.py"
    helper_path.write_text("VALUE = 'before'\n", encoding="utf-8")
    app_path = app_dir / "app.py"
    app_path.write_text(
        "import stui as st\n"
        f"from {APP_HELPER_MODULE_NAME} import VALUE\n"
        "st.text(VALUE)\n",
        encoding="utf-8",
    )
    monkeypatch.syspath_prepend(str(project))
    host_module = importlib.import_module(HOST_MODULE_NAME)
    host_module.STATE.add("live")
    host_singleton = host_module.SINGLETON
    runtime = Runtime(app_path)

    assert _rendered_text(runtime) == ["before"]
    assert host_path.resolve() not in runtime.watched_source_paths
    assert helper_path.resolve() in runtime.watched_source_paths

    helper_path.write_text("VALUE = 'after'\n", encoding="utf-8")
    evicted = runtime.prepare_source_reload(runtime.poll_source_changes())

    assert evicted == (APP_HELPER_MODULE_NAME,)
    assert sys.modules[HOST_MODULE_NAME] is host_module
    assert importlib.import_module(HOST_MODULE_NAME).SINGLETON is host_singleton
    assert host_module.STATE == {"bootstrap", "live"}


def test_runtime_restores_preloaded_host_module_after_local_name_collision(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    host_root = tmp_path / "host"
    app_root = tmp_path / "app"
    host_root.mkdir()
    app_root.mkdir()
    host_path = host_root / f"{COLLIDING_HOST_MODULE_NAME}.py"
    host_path.write_text("VALUE = 'host'\nTOKEN = object()\n", encoding="utf-8")
    local_path = app_root / f"{COLLIDING_HOST_MODULE_NAME}.py"
    local_path.write_text("VALUE = 'local'\n", encoding="utf-8")
    app_path = app_root / "app.py"
    app_path.write_text(
        "import stui as st\n"
        f"from {COLLIDING_HOST_MODULE_NAME} import VALUE\n"
        "st.text(VALUE)\n",
        encoding="utf-8",
    )
    monkeypatch.syspath_prepend(str(host_root))
    host_module = importlib.import_module(COLLIDING_HOST_MODULE_NAME)
    host_token = host_module.TOKEN
    runtime = Runtime(app_path)

    assert _rendered_text(runtime) == ["local"]
    assert sys.modules[COLLIDING_HOST_MODULE_NAME] is host_module
    assert importlib.import_module(COLLIDING_HOST_MODULE_NAME).TOKEN is host_token
    assert local_path.resolve() in runtime.watched_source_paths
    assert _rendered_text(runtime) == ["local"]
    assert sys.modules[COLLIDING_HOST_MODULE_NAME] is host_module


def test_runtime_claims_module_introduced_by_app_execution(tmp_path: Path) -> None:
    helper_path = tmp_path / f"{APP_HELPER_MODULE_NAME}.py"
    helper_path.write_text("VALUE = 'app owned'\n", encoding="utf-8")
    app_path = tmp_path / "app.py"
    app_path.write_text(
        "import stui as st\n"
        f"from {APP_HELPER_MODULE_NAME} import VALUE\n"
        "st.text(VALUE)\n",
        encoding="utf-8",
    )
    runtime = Runtime(app_path)

    assert _rendered_text(runtime) == ["app owned"]
    assert helper_path.resolve() in runtime.watched_source_paths

    helper_path.write_text("VALUE = 'updated'\n", encoding="utf-8")
    changed = runtime.poll_source_changes()
    assert runtime.prepare_source_reload(changed) == (APP_HELPER_MODULE_NAME,)
    assert _rendered_text(runtime) == ["updated"]


def test_runtime_preserves_owned_module_across_ordinary_reruns(
    tmp_path: Path,
) -> None:
    helper_path = tmp_path / f"{OWNED_MODULE_NAME}.py"
    helper_path.write_text("VALUE = 'first'\n", encoding="utf-8")
    app_path = tmp_path / "app.py"
    app_path.write_text(
        "import stui as st\n"
        f"from {OWNED_MODULE_NAME} import VALUE\n"
        "st.text(VALUE)\n",
        encoding="utf-8",
    )
    runtime = Runtime(app_path)

    assert _rendered_text(runtime) == ["first"]
    owned_module = sys.modules[OWNED_MODULE_NAME]
    assert _rendered_text(runtime) == ["first"]
    assert sys.modules[OWNED_MODULE_NAME] is owned_module
    assert helper_path.resolve() in runtime.watched_source_paths

    helper_path.write_text("VALUE = 'second'\n", encoding="utf-8")
    assert runtime.prepare_source_reload(runtime.poll_source_changes()) == (
        OWNED_MODULE_NAME,
    )
    assert _rendered_text(runtime) == ["second"]


def test_prepare_source_reload_waits_for_active_script_execution(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "app"
    root.mkdir()
    runtime = Runtime(_write_app(root, "ready"))
    assert _rendered_text(runtime) == ["ready"]

    original_run_path = runtime_module.runpy.run_path
    run_entered = threading.Event()
    release_run = threading.Event()
    reload_started = threading.Event()

    def blocked_run_path(*args: object, **kwargs: object) -> dict[str, object]:
        run_entered.set()
        assert release_run.wait(timeout=2)
        return original_run_path(*args, **kwargs)

    def reload_source() -> tuple[str, ...]:
        reload_started.set()
        return runtime.prepare_source_reload((root / f"{MODULE_NAME}.py",))

    monkeypatch.setattr(runtime_module.runpy, "run_path", blocked_run_path)

    with ThreadPoolExecutor(max_workers=2) as executor:
        run_result = executor.submit(_rendered_text, runtime)
        assert run_entered.wait(timeout=2)
        reload_result = executor.submit(reload_source)
        assert reload_started.wait(timeout=2)
        assert not reload_result.done()
        assert MODULE_NAME in sys.modules

        release_run.set()
        assert run_result.result(timeout=2) == ["ready"]
        assert reload_result.result(timeout=2) == (MODULE_NAME,)

    assert MODULE_NAME not in sys.modules


def test_concurrent_runtimes_serialize_import_state_and_runpy(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    first_root = tmp_path / "first"
    second_root = tmp_path / "second"
    first_root.mkdir()
    second_root.mkdir()
    first = Runtime(_write_app(first_root, "first"))
    second = Runtime(_write_app(second_root, "second"))

    original_run_path = runtime_module.runpy.run_path
    first_entered = threading.Event()
    second_entered = threading.Event()
    release_first = threading.Event()
    state_lock = threading.Lock()
    active_runs = 0
    overlap_detected = False

    def observed_run_path(*args: object, **kwargs: object) -> dict[str, object]:
        nonlocal active_runs, overlap_detected
        with state_lock:
            active_runs += 1
            overlap_detected = overlap_detected or active_runs > 1
            is_first = not first_entered.is_set()
            first_entered.set()
            if not is_first:
                second_entered.set()
        if is_first:
            assert release_first.wait(timeout=2)
        try:
            return original_run_path(*args, **kwargs)
        finally:
            with state_lock:
                active_runs -= 1

    monkeypatch.setattr(runtime_module.runpy, "run_path", observed_run_path)

    with ThreadPoolExecutor(max_workers=2) as executor:
        first_result = executor.submit(_rendered_text, first)
        assert first_entered.wait(timeout=2)
        second_result = executor.submit(_rendered_text, second)
        assert not second_entered.wait(timeout=0.2)
        assert not overlap_detected
        release_first.set()

        assert first_result.result(timeout=2) == ["first"]
        assert second_result.result(timeout=2) == ["second"]

    assert not overlap_detected
