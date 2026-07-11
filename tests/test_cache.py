from __future__ import annotations

import gc
import sys
import threading
import types
import weakref
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

import stui.cache as cache_module
from stui.cache import CacheSerializationError, cache_data, cache_resource
from stui.elements import WriteElement
from stui.runtime import Runtime, _current_runtime


@pytest.fixture(autouse=True)
def clear_caches() -> None:
    cache_data.clear()
    cache_resource.clear()
    yield
    cache_data.clear()
    cache_resource.clear()


def test_cache_data_supports_bare_decorator() -> None:
    calls = 0

    @cache_data
    def load(value: int) -> int:
        nonlocal calls
        calls += 1
        return value * 2

    assert load(3) == 6
    assert load(3) == 6
    assert calls == 1


def test_cache_data_supports_parameterized_decorator() -> None:
    calls = 0

    @cache_data(ttl=30, max_entries=4)
    def load(value: int) -> int:
        nonlocal calls
        calls += 1
        return value

    assert load(1) == 1
    assert load(1) == 1
    assert calls == 1


def test_argument_binding_normalizes_keyword_order_and_call_style() -> None:
    calls = 0

    @cache_data
    def load(a: int, b: int = 2, **metadata: int) -> int:
        nonlocal calls
        calls += 1
        return a + b + sum(metadata.values())

    assert load(1, b=3, left=4, right=5) == 13
    assert load(a=1, right=5, left=4, b=3) == 13
    assert calls == 1


def test_different_arguments_create_different_entries() -> None:
    calls = 0

    @cache_data
    def load(value: int) -> int:
        nonlocal calls
        calls += 1
        return value

    assert load(1) == 1
    assert load(2) == 2
    assert load(1) == 1
    assert calls == 2


def test_cache_data_survives_runtime_reruns(tmp_path: Path) -> None:
    counter = tmp_path / "calls.txt"
    counter.write_text("0", encoding="utf-8")
    script = tmp_path / "app.py"
    script.write_text(
        f"""
import stui as st
from stui.cache import cache_data
from pathlib import Path

counter = Path({str(counter)!r})

@cache_data
def load():
    value = int(counter.read_text()) + 1
    counter.write_text(str(value))
    return value

st.write("value =", load())
""",
        encoding="utf-8",
    )
    runtime = Runtime(script)

    first = runtime.run_script()
    second = runtime.run_script()

    assert isinstance(first[0], WriteElement)
    assert isinstance(second[0], WriteElement)
    assert first[0].text == "value = 1"
    assert second[0].text == "value = 1"
    assert counter.read_text(encoding="utf-8") == "1"


def test_cache_is_isolated_between_app_scripts(tmp_path: Path) -> None:
    calls = 0

    @cache_data
    def load() -> int:
        nonlocal calls
        calls += 1
        return calls

    runtime_a = Runtime(tmp_path / "app_a.py")
    runtime_b = Runtime(tmp_path / "app_b.py")

    token = _current_runtime.set(runtime_a)
    try:
        assert load() == 1
        assert load() == 1
    finally:
        _current_runtime.reset(token)

    token = _current_runtime.set(runtime_b)
    try:
        assert load() == 2
        assert load() == 2
    finally:
        _current_runtime.reset(token)

    assert calls == 2


def test_cache_is_isolated_between_runtime_instances_for_same_script(
    tmp_path: Path,
) -> None:
    calls = 0

    @cache_data
    def load() -> int:
        nonlocal calls
        calls += 1
        return calls

    script = tmp_path / "app.py"
    runtime_a = Runtime(script)
    runtime_b = Runtime(script)

    token = _current_runtime.set(runtime_a)
    try:
        assert load() == 1
        assert load() == 1
    finally:
        _current_runtime.reset(token)

    token = _current_runtime.set(runtime_b)
    try:
        assert load() == 2
        assert load() == 2
    finally:
        _current_runtime.reset(token)

    assert calls == 2


def test_worker_cache_is_isolated_between_runtime_instances(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    state = {"calls": 0, "value": ""}

    shared_module = types.ModuleType("stui_test_shared_worker_cache")
    shared_module.state = state
    monkeypatch.setitem(sys.modules, shared_module.__name__, shared_module)

    def write_script(path: Path, value: str) -> None:
        path.write_text(
            f'''\
import threading
import stui as st
import stui_test_shared_worker_cache as shared
from stui.cache import cache_data

@cache_data
def load():
    shared.state["calls"] += 1
    return shared.state["value"]

shared.state["value"] = {value!r}
result = []
worker = threading.Thread(target=lambda: result.append(load()))
worker.start()
worker.join()
st.write(result[0])
''',
            encoding="utf-8",
        )

    script_a = tmp_path / "app_a.py"
    script_b = tmp_path / "app_b.py"
    write_script(script_a, "runtime-a")
    write_script(script_b, "runtime-b")

    first = Runtime(script_a).run_script()
    second = Runtime(script_b).run_script()

    assert first[0].text == "runtime-a"
    assert second[0].text == "runtime-b"
    assert state["calls"] == 2


def test_long_lived_worker_keeps_decoration_runtime_during_another_run(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    shared_module = types.ModuleType("stui_test_long_lived_worker_cache")
    shared_module.calls = 0
    shared_module.value = ""
    shared_module.release = threading.Event()
    shared_module.results = []
    monkeypatch.setitem(sys.modules, shared_module.__name__, shared_module)

    script_a = tmp_path / "app_a.py"
    script_a.write_text(
        '''\
import threading
import stui as st
import stui_test_long_lived_worker_cache as shared
from stui.cache import cache_data

@cache_data
def load():
    shared.calls += 1
    return shared.value

def work():
    shared.release.wait()
    shared.results.append(load())

shared.load = load
shared.worker = threading.Thread(target=work)
shared.worker.start()
st.write("started")
''',
        encoding="utf-8",
    )
    script_b = tmp_path / "app_b.py"
    script_b.write_text(
        '''\
import stui as st
import stui_test_long_lived_worker_cache as shared

shared.value = "worker-a"
shared.release.set()
shared.worker.join()
st.write(shared.results[0])
shared.value = "runtime-b"
st.write(shared.load())
''',
        encoding="utf-8",
    )
    runtime_a = Runtime(script_a)
    runtime_b = Runtime(script_b)

    first = runtime_a.run_script()
    second = runtime_b.run_script()

    assert first[0].text == "started"
    assert [element.text for element in second] == ["worker-a", "runtime-b"]
    assert shared_module.calls == 2


def test_contextless_worker_rejects_shared_unowned_decorator_during_run(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    @cache_data
    def load() -> str:
        return "unexpected"

    shared_module = types.ModuleType("stui_test_unowned_worker_cache")
    shared_module.load = load
    monkeypatch.setitem(sys.modules, shared_module.__name__, shared_module)
    script = tmp_path / "app.py"
    script.write_text(
        '''\
import threading
import stui as st
import stui_test_unowned_worker_cache as shared

errors = []

def work():
    try:
        shared.load()
    except RuntimeError as exc:
        errors.append(str(exc))

worker = threading.Thread(target=work)
worker.start()
worker.join()
st.write(errors[0] if errors else "no error")
''',
        encoding="utf-8",
    )

    result = Runtime(script).run_script()

    assert "contextless worker" in result[0].text


def test_source_change_invalidates_only_changed_runtime_scope(tmp_path: Path) -> None:
    data_calls = 0
    resource_calls = 0

    @cache_data
    def load_data() -> int:
        nonlocal data_calls
        data_calls += 1
        return data_calls

    @cache_resource
    def load_resource() -> object:
        nonlocal resource_calls
        resource_calls += 1
        return object()

    runtime_a = Runtime(tmp_path / "app_a.py")
    runtime_b = Runtime(tmp_path / "app_b.py")

    token = _current_runtime.set(runtime_a)
    try:
        assert load_data() == 1
        resource_a = load_resource()
    finally:
        _current_runtime.reset(token)

    token = _current_runtime.set(runtime_b)
    try:
        assert load_data() == 2
        resource_b = load_resource()
    finally:
        _current_runtime.reset(token)

    runtime_a.prepare_source_reload([runtime_a.script_path])

    token = _current_runtime.set(runtime_a)
    try:
        assert load_data() == 3
        assert load_resource() is not resource_a
    finally:
        _current_runtime.reset(token)

    token = _current_runtime.set(runtime_b)
    try:
        assert load_data() == 2
        assert load_resource() is resource_b
    finally:
        _current_runtime.reset(token)

    assert data_calls == 3
    assert resource_calls == 3


def test_lazy_source_change_hook_does_not_retain_runtime(tmp_path: Path) -> None:
    @cache_data
    def load() -> int:
        return 1

    runtime = Runtime(tmp_path / "app.py")
    runtime_reference = weakref.ref(runtime)
    token = _current_runtime.set(runtime)
    try:
        assert load() == 1
    finally:
        _current_runtime.reset(token)
    del token
    del runtime

    gc.collect()

    assert runtime_reference() is None


def test_cache_resource_backreference_does_not_retain_runtime(tmp_path: Path) -> None:
    runtime = Runtime(tmp_path / "app.py")
    runtime_reference = weakref.ref(runtime)
    token = _current_runtime.set(runtime)
    try:

        @cache_resource
        def load_runtime() -> Runtime:
            cached_runtime = runtime_reference()
            assert cached_runtime is not None
            return cached_runtime

        assert load_runtime() is runtime
    finally:
        _current_runtime.reset(token)
    del token
    del load_runtime
    del runtime

    gc.collect()

    assert runtime_reference() is None


def test_code_fingerprint_invalidates_old_entries() -> None:
    namespace_one: dict[str, object] = {}
    namespace_two: dict[str, object] = {}
    exec(compile("def load():\n    return 1\n", "same_app.py", "exec"), namespace_one)
    exec(compile("def load():\n    return 2\n", "same_app.py", "exec"), namespace_two)
    first = cache_data(namespace_one["load"])
    second = cache_data(namespace_two["load"])

    assert first() == 1
    assert second() == 2


def test_unpickleable_closure_values_do_not_collide() -> None:
    def make_loader(secret: str):
        marker = threading.Lock()

        @cache_data
        def load() -> str:
            assert not marker.locked()
            return secret

        return load

    first = make_loader("FIRST_SECRET")
    second = make_loader("SECOND_SECRET")

    assert first() == "FIRST_SECRET"
    assert second() == "SECOND_SECRET"
    assert first() == "FIRST_SECRET"


def test_module_source_change_invalidates_global_dependency(tmp_path: Path) -> None:
    source_path = tmp_path / "loader.py"
    first_source = "VALUE = 1\n\ndef load():\n    return VALUE\n"
    second_source = "VALUE = 2\n\ndef load():\n    return VALUE\n"
    source_path.write_text(first_source, encoding="utf-8")

    first_namespace: dict[str, object] = {}
    exec(compile(first_source, str(source_path), "exec"), first_namespace)
    first = cache_data(first_namespace["load"])
    assert first() == 1

    source_path.write_text(second_source, encoding="utf-8")
    second_namespace: dict[str, object] = {}
    exec(compile(second_source, str(source_path), "exec"), second_namespace)
    second = cache_data(second_namespace["load"])

    assert second() == 2


def test_fallback_cache_isolated_for_same_source_with_different_globals() -> None:
    source = (
        "def load():\n"
        "    global CALLS\n"
        "    CALLS += 1\n"
        "    return VALUE\n"
    )

    def load_from_namespace(value: int):
        namespace: dict[str, object] = {"CALLS": 0, "VALUE": value}
        exec(compile(source, "shared_loader.py", "exec"), namespace)
        return cache_data(namespace["load"]), namespace

    first, first_namespace = load_from_namespace(1)
    second, second_namespace = load_from_namespace(2)

    assert first() == 1
    assert second() == 2
    assert first() == 1
    assert second() == 2
    assert first_namespace["CALLS"] == 1
    assert second_namespace["CALLS"] == 1


def test_fallback_function_clear_only_clears_its_function_instance() -> None:
    source = "def load():\n    global CALLS\n    CALLS += 1\n    return VALUE, CALLS\n"

    def load_from_namespace(value: int):
        namespace: dict[str, object] = {"CALLS": 0, "VALUE": value}
        exec(compile(source, "shared_loader.py", "exec"), namespace)
        return cache_data(namespace["load"])

    first = load_from_namespace(1)
    second = load_from_namespace(2)

    assert first() == (1, 1)
    assert second() == (2, 1)
    first.clear()

    assert first() == (1, 2)
    assert second() == (2, 1)


def test_ttl_expiration_uses_monotonic_time(monkeypatch: pytest.MonkeyPatch) -> None:
    now = 10.0
    calls = 0
    monkeypatch.setattr(cache_module, "_monotonic", lambda: now)

    @cache_data(ttl=5)
    def load() -> int:
        nonlocal calls
        calls += 1
        return calls

    assert load() == 1
    now = 14.999
    assert load() == 1
    now = 15.0
    assert load() == 2


def test_cache_resource_ttl_preserves_then_replaces_identity(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    now = 20.0
    monkeypatch.setattr(cache_module, "_monotonic", lambda: now)

    @cache_resource(ttl=3)
    def load() -> object:
        return object()

    first = load()
    now = 22.999
    assert load() is first
    now = 23.0
    assert load() is not first


def test_max_entries_uses_lru_eviction() -> None:
    calls: list[int] = []

    @cache_data(max_entries=2)
    def load(value: int) -> int:
        calls.append(value)
        return value

    assert load(1) == 1
    assert load(2) == 2
    assert load(1) == 1
    assert load(3) == 3
    assert load(2) == 2
    assert calls == [1, 2, 3, 2]


def test_exceptions_are_not_cached() -> None:
    calls = 0

    @cache_data
    def fail() -> None:
        nonlocal calls
        calls += 1
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError, match="boom"):
        fail()
    with pytest.raises(RuntimeError, match="boom"):
        fail()
    assert calls == 2


def test_cache_data_returns_mutation_isolated_values() -> None:
    calls = 0

    @cache_data
    def load() -> dict[str, list[int]]:
        nonlocal calls
        calls += 1
        return {"values": [1]}

    first = load()
    first["values"].append(2)

    assert load() == {"values": [1]}
    assert calls == 1


def test_cache_resource_preserves_object_identity() -> None:
    calls = 0

    @cache_resource
    def load() -> object:
        nonlocal calls
        calls += 1
        return object()

    first = load()
    assert load() is first
    assert calls == 1


def test_per_function_clear_only_clears_that_function() -> None:
    first_calls = 0
    second_calls = 0

    @cache_data
    def first() -> int:
        nonlocal first_calls
        first_calls += 1
        return first_calls

    @cache_data
    def second() -> int:
        nonlocal second_calls
        second_calls += 1
        return second_calls

    assert first() == 1
    assert second() == 1
    first.clear()
    assert first() == 2
    assert second() == 1


def test_namespace_clear_is_separate_for_data_and_resources() -> None:
    data_calls = 0
    resource_calls = 0

    @cache_data
    def data() -> int:
        nonlocal data_calls
        data_calls += 1
        return data_calls

    @cache_resource
    def resource() -> object:
        nonlocal resource_calls
        resource_calls += 1
        return object()

    first_resource = resource()
    assert data() == 1
    cache_data.clear()
    assert data() == 2
    assert resource() is first_resource
    cache_resource.clear()
    assert resource() is not first_resource


def test_clear_apis_remove_runtime_scoped_entries(tmp_path: Path) -> None:
    data_calls = 0
    resource_calls = 0

    @cache_data
    def data() -> int:
        nonlocal data_calls
        data_calls += 1
        return data_calls

    @cache_resource
    def resource() -> object:
        nonlocal resource_calls
        resource_calls += 1
        return object()

    runtime = Runtime(tmp_path / "app.py")
    token = _current_runtime.set(runtime)
    try:
        assert data() == 1
        first_resource = resource()

        data.clear()
        assert data() == 2
        assert resource() is first_resource

        cache_resource.clear()
        assert resource() is not first_resource
    finally:
        _current_runtime.reset(token)

    assert data_calls == 2
    assert resource_calls == 2


@pytest.mark.parametrize(
    ("decorator", "message"),
    [
        (lambda: cache_data(ttl=0), "ttl"),
        (lambda: cache_data(ttl=-1), "ttl"),
        (lambda: cache_data(ttl=True), "ttl"),
        (lambda: cache_data(ttl=float("inf")), "ttl"),
        (lambda: cache_data(ttl=float("nan")), "ttl"),
        (lambda: cache_resource(ttl="30"), "ttl"),
        (lambda: cache_data(max_entries=0), "max_entries"),
        (lambda: cache_data(max_entries=-1), "max_entries"),
        (lambda: cache_data(max_entries=True), "max_entries"),
        (lambda: cache_data(max_entries=1.5), "max_entries"),
        (lambda: cache_resource(max_entries="4"), "max_entries"),
    ],
)
def test_invalid_cache_parameters_are_rejected(decorator, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        decorator()


def test_unserializable_arguments_raise_readable_error() -> None:
    calls = 0

    class Unserializable:
        def __reduce__(self):
            raise TypeError("not serializable")

    @cache_data
    def load(value: object) -> str:
        nonlocal calls
        calls += 1
        return "ok"

    with pytest.raises(CacheSerializationError, match="cache key"):
        load(Unserializable())
    assert calls == 0


def test_unserializable_cache_data_return_raises_readable_error() -> None:
    calls = 0

    @cache_data
    def load():
        nonlocal calls
        calls += 1
        return lambda: None

    with pytest.raises(CacheSerializationError, match="return value"):
        load()
    with pytest.raises(CacheSerializationError, match="return value"):
        load()
    assert calls == 2


def test_cache_lock_prevents_duplicate_concurrent_computation() -> None:
    calls = 0
    started = threading.Event()
    release = threading.Event()

    @cache_resource
    def load() -> object:
        nonlocal calls
        calls += 1
        started.set()
        release.wait(timeout=2)
        return object()

    with ThreadPoolExecutor(max_workers=2) as executor:
        first_future = executor.submit(load)
        assert started.wait(timeout=2)
        second_future = executor.submit(load)
        release.set()
        first = first_future.result(timeout=2)
        second = second_future.result(timeout=2)

    assert first is second
    assert calls == 1


def test_same_thread_reentrant_fill_fails_fast() -> None:
    outcome: list[BaseException] = []

    @cache_data
    def load(value: int) -> int:
        return load(value)

    def invoke() -> None:
        try:
            load(1)
        except BaseException as exc:
            outcome.append(exc)

    worker = threading.Thread(target=invoke, daemon=True)
    worker.start()
    worker.join(timeout=1)

    assert not worker.is_alive(), "recursive cache fill deadlocked"
    assert len(outcome) == 1
    assert isinstance(outcome[0], RuntimeError)
    assert "recursive cache fill" in str(outcome[0]).lower()


def test_waiter_retries_after_cross_thread_fill_exception() -> None:
    calls = 0
    first_started = threading.Event()
    release_first = threading.Event()

    @cache_data
    def load() -> int:
        nonlocal calls
        calls += 1
        if calls == 1:
            first_started.set()
            assert release_first.wait(timeout=2)
            raise RuntimeError("first fill failed")
        return calls

    with ThreadPoolExecutor(max_workers=2) as executor:
        first_future = executor.submit(load)
        assert first_started.wait(timeout=2)
        second_future = executor.submit(load)
        release_first.set()

        with pytest.raises(RuntimeError, match="first fill failed"):
            first_future.result(timeout=2)
        assert second_future.result(timeout=2) == 2

    assert load() == 2
    assert calls == 2


@pytest.mark.parametrize("clear_scope", ["function", "namespace"])
def test_clear_during_inflight_fill_does_not_restore_stale_entry(
    clear_scope: str,
) -> None:
    calls = 0
    first_started = threading.Event()
    release_first = threading.Event()

    @cache_data
    def load() -> int:
        nonlocal calls
        calls += 1
        current = calls
        if current == 1:
            first_started.set()
            assert release_first.wait(timeout=2)
        return current

    with ThreadPoolExecutor(max_workers=2) as executor:
        first_future = executor.submit(load)
        assert first_started.wait(timeout=2)
        second_future = executor.submit(load)
        if clear_scope == "function":
            load.clear()
        else:
            cache_data.clear()
        release_first.set()

        assert first_future.result(timeout=2) == 1
        assert second_future.result(timeout=2) == 2

    assert load() == 2
    assert calls == 2


def test_nested_cached_worker_call_does_not_deadlock() -> None:
    with ThreadPoolExecutor(max_workers=1) as executor:

        @cache_data
        def inner() -> str:
            return "ready"

        @cache_data
        def outer() -> str:
            return executor.submit(inner).result(timeout=2)

        assert outer() == "ready"
        assert outer() == "ready"


def test_cache_works_in_form_callback_after_state_commit(tmp_path: Path) -> None:
    counter = tmp_path / "calls.txt"
    counter.write_text("0", encoding="utf-8")
    script = tmp_path / "app.py"
    script.write_text(
        f'''
import stui as st
from pathlib import Path
from stui.cache import cache_data

counter = Path({str(counter)!r})

@cache_data
def normalize(value):
    calls = int(counter.read_text()) + 1
    counter.write_text(str(calls))
    return value.strip().upper()

def remember():
    st.session_state["observed"] = normalize(st.session_state["name"])

with st.form("profile"):
    st.text_input("Name", key="name", on_change=remember)
    st.form_submit_button("Save")
''',
        encoding="utf-8",
    )
    runtime = Runtime(script)

    runtime.run_script()
    runtime.set_widget_value("name", " Ada ")
    runtime.run_script()
    assert "name" not in runtime.session_state
    assert "observed" not in runtime.session_state

    runtime.press_button("form_submit_button:profile:Save:0")
    runtime.run_script()

    assert runtime.session_state["name"] == " Ada "
    assert runtime.session_state["observed"] == "ADA"
    assert counter.read_text(encoding="utf-8") == "1"


def test_check_repeat_reuses_cache_within_one_runtime(tmp_path: Path) -> None:
    from stui.cli import _validate_script

    counter = tmp_path / "calls.txt"
    counter.write_text("0", encoding="utf-8")
    script = tmp_path / "app.py"
    script.write_text(
        f'''
import stui as st
from pathlib import Path
from stui.cache import cache_data

counter = Path({str(counter)!r})

@cache_data
def load():
    calls = int(counter.read_text()) + 1
    counter.write_text(str(calls))
    return calls

st.write(load())
''',
        encoding="utf-8",
    )

    payload = _validate_script(script, strict=True, repeat=3)

    assert payload["ok"] is True
    assert payload["summary"]["runs_completed"] == 3
    assert counter.read_text(encoding="utf-8") == "1"

    second_payload = _validate_script(script, strict=True, repeat=2)

    assert second_payload["ok"] is True
    assert second_payload["summary"]["runs_completed"] == 2
    assert counter.read_text(encoding="utf-8") == "2"
