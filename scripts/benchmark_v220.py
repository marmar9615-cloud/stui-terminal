#!/usr/bin/env python3
"""Run advisory v2.2 cache-hit and watch-poll timing probes."""

from __future__ import annotations

import json
import statistics
import tempfile
import time
from pathlib import Path

from stui.runtime import Runtime


def _median_ms(samples: list[float]) -> float:
    return round(statistics.median(samples) * 1000, 4)


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="stui-v220-benchmark-") as tmp:
        root = Path(tmp)
        helper = root / "helper.py"
        helper.write_text("VALUE = 42\n", encoding="utf-8")
        app = root / "app.py"
        app.write_text(
            "import stui as st\n"
            "from helper import VALUE\n"
            "st.session_state.calls = st.session_state.get('calls', 0)\n"
            "@st.cache_data\n"
            "def compute(value):\n"
            "    st.session_state.calls += 1\n"
            "    return list(range(value))\n"
            "st.write(VALUE, len(compute(5000)))\n",
            encoding="utf-8",
        )
        runtime = Runtime(app)

        cold_start = time.perf_counter()
        runtime.run_script()
        cold_seconds = time.perf_counter() - cold_start
        assert runtime.session_state.calls == 1

        rerun_samples = []
        for _ in range(50):
            started = time.perf_counter()
            runtime.run_script()
            rerun_samples.append(time.perf_counter() - started)
        assert runtime.session_state.calls == 1

        poll_samples = []
        for _ in range(500):
            started = time.perf_counter()
            assert runtime.poll_source_changes() == ()
            poll_samples.append(time.perf_counter() - started)

        result = {
            "schema_version": "stui.v220-benchmark.v1",
            "cache": {
                "cold_ms": round(cold_seconds * 1000, 4),
                "hit_rerun_median_ms": _median_ms(rerun_samples),
                "executions_after_51_runs": runtime.session_state.calls,
            },
            "watch": {
                "tracked_files": len(runtime.watched_source_paths),
                "unchanged_poll_median_ms": _median_ms(poll_samples),
                "poll_samples": len(poll_samples),
            },
        }
        print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
