# Caching

`stui` v2.2.0 added process-local caching for expensive pure computations and
reusable local resources. The decorators graduate to stable in v2.3.0. The
cache is terminal-native and deliberately small:
it does not write to disk, start workers, use the network, or survive the app
process.

`stui inspect APP.py --json` reports aggregate function, entry, and in-flight
counts for the inspected runtime. It never reports keys, arguments,
fingerprints, return values, or arbitrary representations. Ctrl+P in a running
app exposes fixed commands to clear that app's data or resource cache.

## Choose A Cache

Use `st.cache_data` for values that callers should be able to mutate without
changing the cached copy:

```python
import stui as st


@st.cache_data(ttl=60, max_entries=128)
def load_rows(path: str) -> list[dict[str, object]]:
    ...


rows = load_rows("runs.json")
```

Use `st.cache_resource` for one process-local object whose identity should be
reused, such as a model wrapper, database client, or parsed configuration:

```python
@st.cache_resource
def load_model() -> object:
    ...


model = load_model()
```

`cache_data` isolates supported return values from caller mutation.
`cache_resource` deliberately returns the same object, so callers share any
mutations and must make that object safe for their own access pattern.

## Decorator Forms

Both APIs support bare and configured decorator forms:

```python
@st.cache_data
def defaults():
    return {"ready": True}


@st.cache_data(ttl=30, max_entries=64)
def recent_rows(limit: int):
    return list(range(limit))


@st.cache_resource
def resource():
    return object()
```

`ttl=None` means entries do not expire before process exit or explicit
clearing. A numeric TTL must be positive. `max_entries=None` leaves the cache
unbounded; a numeric limit must be a positive integer. When a limit is set,
least-recently-used entries are evicted deterministically.

## Keys And Invalidation

A cache key includes:

- the current app script;
- the decorated function identity and code fingerprint;
- normalized positional and keyword arguments.

Equivalent keyword arguments have the same key regardless of keyword order.
Changing an argument creates another entry. The fingerprint includes the
decorated function's code, defaults, closure values, configuration, and source
module contents. Recreating the decorator after a source change invalidates
entries made by an older fingerprint. Separate app scripts do not share cached
entries even when they define functions with the same name.

Watch mode evicts imported local modules before rerunning changed source. Any
watched source change clears all `cache_data` and `cache_resource` entries owned
by that app's `Runtime` before the next script pass. This conservative rule
avoids stale results when an unchanged cached function depends indirectly on a
changed helper or module-level value. Other app runtimes remain isolated and
are not cleared. The app process remains alive and `st.session_state` survives
the reload.

## Clearing

Clear one decorated function with its `clear()` method:

```python
load_rows.clear()
```

Clear every entry in a cache namespace for the current process:

```python
st.cache_data.clear()
st.cache_resource.clear()
```

Clearing `cache_data` does not clear `cache_resource`, and vice versa.

## Errors And Unsupported Values

- Exceptions are never cached. A later call executes the function again.
- Arguments must be deterministically keyable by the cache implementation.
- `cache_data` return values must support the documented copy/serialization
  path. Unsupported values raise a readable error instead of silently sharing
  a mutable object.
- `cache_resource` may return objects that cannot be serialized because it
  keeps the live object in memory.
- Cache keys and user-facing errors avoid printing complete argument values;
  do not rely on cache diagnostics as a secret store.

## Edge-Case Contract

| Case | Result |
| --- | --- |
| Same call after a normal rerun | Cache hit in the same app process. |
| Same keyword arguments in a different order | Same key after signature binding. |
| Same function name in another app script | Different app scope; no shared entry. |
| Decorated function/module source changes | New fingerprint replaces stale entries when the function is recreated. |
| Any source tracked by watch mode changes | All data and resource entries for that app runtime are cleared before rerun. |
| Function raises | Exception propagates and no entry is stored. |
| Function recursively requests its own unfinished key | A readable `RuntimeError` is raised; the call does not deadlock or cache an exception. |
| Two threads request the same unfinished key | One thread fills it; the waiter receives the completed cached value or retries after a failed fill. |
| Script-defined cached function runs in an ordinary worker | The weak decoration-time runtime owns the entry, even if the worker finishes later. |
| Shared decorator has no runtime context while another app is active | A readable `RuntimeError` is raised instead of guessing an app scope. |
| Separately loaded same-source functions run outside a stui runtime | Each decorated function instance has its own fallback cache identity. |
| `cache_data` return is mutated by the caller | A later hit restores an isolated value from cached bytes. |
| `cache_resource` return is mutated | Later hits see the same object and mutation by design. |
| TTL expires | The next call recomputes and replaces the entry. |
| `max_entries` is exceeded | The least-recently-used entry is evicted. |
| Argument cannot be serialized | A readable cache-key error is raised without printing the full argument. |
| `cache_data` result cannot be serialized | A readable result error is raised; the result is not cached. |
| Process exits | All entries disappear. |
| External file/service changes without an argument/source change | No automatic invalidation; pass an explicit freshness value or clear. |

## Interaction With Reruns And Forms

Normal widget reruns reuse cache entries in the same app process. Form
interactions still follow form rules: pending widget values commit on submit,
and the cache only sees the arguments passed by the script on each run.

`stui check --repeat N` runs the script repeatedly in one runtime for
validation. Cache entries are intentionally process-local, so repeat checks can
observe the same cache registry. Do not treat `stui check` timings as a
performance benchmark; its job is to catch authoring and repeated-run errors.

## Limits

- In-memory only; closing the process clears everything.
- No disk persistence, distributed coordination, background refresh, or
  network cache.
- No automatic invalidation for files or services read inside a cached
  function. Include a content fingerprint, modification timestamp, or version
  argument when external input freshness matters.
- Outside watch mode, changing an external module-level value, file, or service
  is not inferred as a dependency. Pass a freshness value as an argument or
  clear the function explicitly.
- Unpickleable closure values receive a conservative instance-specific
  fingerprint. This prevents cross-function cache collisions but may turn a
  recreated decorator into a cache miss on the next rerun.
- `cache_resource` identity sharing is intentional and can expose unsafe
  mutation if the resource is not designed for reuse.
- Cached functions defined while an app script executes can be called from
  ordinary workers because the wrapper keeps a weak owner reference. A shared
  decorator created outside a runtime cannot be assigned safely to a
  contextless worker while an app is active; propagate the context explicitly,
  define the wrapper in the app, or call it outside the active script pass.

## Proof Commands

The release gate exercises cache semantics directly and again through an
external multi-file project:

```bash
python3.11 -m pytest tests/test_cache.py tests/test_watch_mode.py
python3.11 scripts/verify_v220_project.py --wheel dist/stui_terminal-2.2.0-py3-none-any.whl
```

The external project must prove cache hits, mutation isolation, resource
identity, clearing, TTL/eviction, helper reload, error recovery, and no
cross-app leakage before v2.2.0 is published. These commands are proof gates,
not performance claims.

v2.2.0 does not publish a cache speedup percentage. Cache effectiveness depends
on the wrapped function, value size, pickle cost, hit rate, and terminal app.
Correctness evidence is required; advisory timings may be recorded separately
but are not a release pass/fail threshold.

See [Watch Mode](watch-mode.md) for source reload behavior and
[`examples/caching.py`](../examples/caching.py) for a small offline example.
