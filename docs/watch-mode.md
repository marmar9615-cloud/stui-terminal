# Watch Mode

Use watch mode while editing a local app:

```bash
stui run app.py --watch
```

v2.2.0 hardens the development loop for multi-file projects. After a
successful run, `stui` tracks the app script and imported local Python modules
under the project directory. Saving one of those files reruns the app without
discarding `st.session_state`.

## What Is Watched

- the entry script passed to `stui run`;
- local Python modules imported by the app after a successful run;
- nested local packages imported from the app/project directory.

The watcher ignores virtual environments, `.git`, `__pycache__`, build and
distribution directories, cache directories, and unrelated files. Source
signatures include content and file identity, so atomic replacement is visible
even when a tool preserves timestamps. Multiple writes between polling passes
are coalesced into one reload.

## Reload Semantics

When a relevant file changes, `stui` evicts affected local modules before the
next script pass. Third-party modules stay loaded. This lets an edit to
`helpers.py` appear on the next render instead of reusing the old module from
`sys.modules`.

The runtime and process remain alive:

- `st.session_state` survives a successful reload;
- focused-widget restoration remains best effort;
- every `cache_data` and `cache_resource` entry owned by that app runtime is
  cleared before the rerun, including entries whose decorated function did not
  change directly;
- other app runtimes remain isolated and are not cleared;
- external side effects performed by the script are still the app author's
  responsibility.

## Error Recovery

A temporary syntax, import, or runtime error is rendered as an app error while
the watcher stays alive. Fixing and saving the file triggers another run. This
is especially useful with editors that briefly expose an incomplete file while
saving.

If a local module is deleted and recreated, watch mode keeps polling the
project and reloads it when the source is available again. Rapid save bursts
are coalesced so one edit does not cause a reload storm.

## Limits

- Watch mode is a development helper, not a deployment supervisor.
- Dynamic imports outside the app/project directory may not be tracked.
- Only Python modules imported by a completed script pass are discovered.
  A module imported only on a later conditional path becomes watchable after
  that path runs.
- Non-Python inputs are not inferred automatically. Pass their version,
  content hash, or modification time into cached functions when freshness
  matters.
- Changes inside the active virtual environment or third-party packages are
  intentionally ignored.
- Module-level side effects run again after a reload. Keep them idempotent or
  move reusable setup behind `st.cache_resource`.

The repo-only [`examples/watch_project`](../examples/watch_project/README.md)
example shows an app with local helpers and data loading. It is not a bundled
single-file demo because preserving the multi-file shape is the point of the
example.

## Proof Commands

Run the focused deterministic checks first:

```bash
python3.11 -m pytest tests/test_watch_mode.py
```

Then run the external-project validator against the built wheel:

```bash
python3.11 scripts/verify_v220_project.py --wheel dist/stui_terminal-2.2.0-py3-none-any.whl
```

The validator is expected to edit an imported helper, observe the new render,
preserve session state, reject stale cached output, survive a temporary syntax
error, and recover after the helper is fixed. The full release gate records the
actual pass/fail result; this page does not substitute a claim for that run.
