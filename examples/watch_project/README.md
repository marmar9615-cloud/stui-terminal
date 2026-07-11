# Multi-File Watch Example

This repo-only example demonstrates local helper-module reloads. Run it from
the repository root:

```bash
stui run examples/watch_project/app.py --watch
```

While it is running:

1. Change the prefix returned by `format_summary` in `helpers.py`.
2. Save the file and confirm the rendered summary changes.
3. Interact with the app and confirm the run counter survives the reload.
4. Introduce a temporary syntax error, save, then fix and save it again. The
   watcher should render the error and recover without restarting the process.

The example stays repo-only because it depends on a multi-file directory. The
bundled demo command is intentionally optimized for single-file examples that
can be copied from an installed wheel.
