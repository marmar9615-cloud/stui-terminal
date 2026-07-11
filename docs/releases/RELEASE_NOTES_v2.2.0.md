# stui v2.2.0

`stui` v2.2.0 is the fast-reruns-and-richer-authoring release. It keeps the
stable v2 API intact while adding process-local caching, multiline terminal
input, and a multi-file watch loop that reloads imported local helpers.

`stui` remains terminal-native and Streamlit-inspired. It is not official
Streamlit, is not affiliated with Streamlit, and is not a Streamlit
compatibility layer. It does not add a browser, server, websocket, network
cache, or Streamlit runtime dependency.

## Install

```bash
python -m pip install --upgrade stui-terminal==2.2.0
stui --version
stui doctor --json
stui selftest --strict --repeat 2
```

The distribution is `stui-terminal`; Python code still uses
`import stui as st`, and apps still run with `stui run app.py`.

## Highlights

### Process-Local Caching

- Added post-v2 experimental `st.cache_data` for pickle-compatible values that
  should be isolated from caller mutation.
- Added post-v2 experimental `st.cache_resource` for reusable objects whose
  identity should be shared in the app process.
- Both decorators support bare/configured forms, normalized argument keys,
  positive TTLs, deterministic LRU entry limits, per-function `.clear()`, and
  namespace-level clearing.
- Cache entries are isolated by app script and function identity/fingerprint,
  survive normal reruns in the same process, and disappear when the process
  exits.
- Exceptions and unsupported `cache_data` return values are never cached.
- There is no disk cache, network cache, hidden worker, background refresh, or
  distributed coordination.

See [Caching](../caching.md) for the complete contract and limitations.

### Multi-File Watch Mode

- `stui run app.py --watch` now tracks the entry script plus imported local
  Python modules under the app directory.
- Changed local modules are evicted before rerun so `helper.py` edits appear in
  the rendered app instead of reusing stale `sys.modules` objects.
- Content-aware signatures detect in-place writes and atomic file replacement.
- `st.session_state` survives successful reloads.
- Any tracked source change clears all data/resource cache entries owned by the
  affected app runtime before rerun; other app runtimes remain isolated.
- Temporary syntax/import/runtime errors render without killing the watcher;
  fixing and saving source recovers in the same process.
- Third-party packages, virtual environments, `.git`, `__pycache__`, build,
  distribution, and unrelated files remain outside the watch set.

See [Watch Mode](../watch-mode.md) and the repo-only
[`examples/watch_project`](../../examples/watch_project/README.md).

### Multiline Authoring

- Added post-v2 experimental `st.text_area`.
- Enter inserts a newline; Ctrl+Enter applies the value and reruns.
- Supports explicit/generated keys, placeholder text, disabled state,
  positive `max_chars`, callbacks, form-pending state, soft wrapping, and
  best-effort cursor/scroll restoration.
- Renders unsafe C0/C1 terminal controls as visible `\\xNN` escapes for initial,
  restored, typed, and pasted text before each frame, while preserving
  newlines, tabs, and printable Unicode.
- Added a deterministic offline prompt-workbench example combining multiline
  input, caching, multi-select, toggle, and toast behavior.

### Security and isolation hardening

- Script-defined cached functions retain a weak reference to their owning app
  runtime for ordinary worker-thread calls. Ambiguous shared decorators without
  a runtime context fail clearly instead of guessing from another active app.
- Runtime-owned cache registries no longer keep disposed runtimes alive when a
  cached resource contains a backreference to its owner.
- Nested apps check both their script directory and marked project root for
  conflicting local modules before execution.
- Every public display/widget sink, watch filename, toast, and duplicate-key
  diagnostic applies the same visible terminal-control policy as multiline
  input before rendering.
- `text_area(max_chars=...)` normalizes before truncation, keeping the committed
  value idempotent across ordinary reruns even when input contains controls.
- Release proof uses exclusive private temporary directories, TestPyPI
  verification avoids mixed resolver indexes, and the package audit requires
  every new v2.2 runtime and bundled example file.
- PEP 420 namespace packages are included in cross-app module eviction so a
  later runtime cannot reuse a previous app's same-named local module.
- Process-global import changes are serialized when embedding code runs
  multiple runtimes concurrently.
- Watch discovery records only modules introduced or replaced by the app, so it
  does not evict a host-preloaded project module that the app never owned.
- Source-reload eviction shares the script-execution lock, preventing one run
  from observing old and new identities of the same helper module.
- Recursive same-key cache fills fail clearly instead of deadlocking, and
  separately decorated fallback functions remain isolated outside an active
  runtime.
- Multiple immutable pre-release snapshots were checked through Codex Security;
  every reproduced security or defense-in-depth defect was fixed before the
  final release snapshot and publication gates.

## API Status

The stable v2 surface is unchanged.

Post-v1 experimental APIs remain:

- `st.status`
- `st.spinner`
- `st.help`

Post-v2 experimental APIs are:

- `st.multiselect`
- `st.toggle`
- `st.toast`
- `st.cache_data`
- `st.cache_resource`
- `st.text_area`

`st.tabs` was evaluated and deferred. The current element model does not yet
have a sufficiently small, proven contract for inactive-content execution,
widget keys, nested forms/containers, focus restoration, and narrow-terminal
navigation. v2.2.0 prioritizes cache, watch, and text-area correctness instead.

## Examples

From an installed package:

```bash
stui demo caching
stui demo prompt_workbench
stui example copy caching ./caching.py
stui example copy prompt_workbench ./prompt_workbench.py
stui run ./caching.py
stui run ./prompt_workbench.py
```

From a repository checkout:

```bash
stui run examples/caching.py
stui run examples/prompt_workbench.py
stui run examples/watch_project/app.py --watch
```

## Compatibility

- Existing v2.1.0 stable API calls continue to work.
- The Textual runtime floor is now 8.2.5 so every valid v2.2.0 installation has
  the multiline widget constructor and behavior exercised by the release
  suite. Pip upgrades older Textual installations during normal resolution.
- `st.multiselect`, `st.toggle`, and `st.toast` remain available and
  experimental; v2.2.0 does not silently promote them.
- Watch mode remains opt-in. `stui run app.py` without `--watch` keeps the
  existing one-run-at-a-time app behavior.
- Non-Python data files are not automatically watched. Pass a version, content
  fingerprint, or modification time as a cache argument when external input
  freshness matters.

## Release Proof

The release is considered complete only after all of these pass against the
same commit and artifacts:

- Ruff and the complete Python 3.11 test suite;
- build, Twine, release-version, wheel/sdist content, and repo-hygiene checks;
- deterministic cache and watch regression tests;
- Textual harness checks for multiline input and v2.1 widget behavior;
- clean wheel install plus strict CLI/selftest/example validation;
- a clean external multi-file project proving cache hits, mutation isolation,
  resource identity, clear/TTL/LRU behavior, helper reload, state survival,
  stale-cache invalidation, syntax-error survival, and recovery;
- security/static-policy checks and Trusted Publishing/OIDC review;
- GitHub main/tag/publish workflows;
- PyPI JSON/Simple API and a fresh exact-version `--no-cache-dir` install;
- GitHub Release and a clean final working tree.

No social or GitHub Discussion launch copy is part of this release.

## Known Limits

- Cache values are process-local only. Closing the app clears them.
- `st.cache_data` arguments and results must be pickle-compatible.
- `st.cache_resource` deliberately shares mutable object identity.
- Watch mode discovers Python modules after a script pass imports them; it is
  not a deployment supervisor or general filesystem watcher.
- `st.text_area` keyboard handling is terminal/Textual based; unusual terminal
  key mappings should be reported with `stui doctor --compat` output.
- Tabs, sidebars, file upload, persistent/distributed caching, editable
  dataframes, and heavier plotting remain outside this release.
