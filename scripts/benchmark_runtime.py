from __future__ import annotations

import argparse
import statistics
import tempfile
import time
from collections.abc import Sequence
from pathlib import Path

from stui.runtime import Runtime

SCENARIOS = {
    "many-writes": """
import stui as st

for index in range(300):
    st.write("row", index)
""",
    "dashboard": """
import stui as st

st.title("Benchmark dashboard")
st.metric("Runs", 12, "+2")
st.table([
    {"name": f"item-{index}", "score": index / 10, "status": "ok"}
    for index in range(50)
], max_rows=10, max_cols=3)
st.bar_chart({"alpha": 12, "beta": -3, "gamma": 8})
st.line_chart([1, 3, 2, 5, 4, 8])
with st.container():
    st.status("Ready", state="complete")
    st.help("Small benchmark scenario")
""",
}


def _time_runtime(script: Path, repeats: int) -> tuple[int, list[float]]:
    runtime = Runtime(script)
    durations = []
    element_count = 0
    for _ in range(repeats):
        start = time.perf_counter()
        elements = runtime.run_script()
        durations.append((time.perf_counter() - start) * 1000)
        element_count = len(elements)
    return element_count, durations


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run advisory stui runtime timing probes."
    )
    parser.add_argument(
        "--repeat",
        type=int,
        default=20,
        help="Number of runtime passes per scenario.",
    )
    args = parser.parse_args(argv)
    if args.repeat < 1:
        parser.error("--repeat must be at least 1")

    with tempfile.TemporaryDirectory(prefix="stui-benchmark-") as tmp:
        tmp_path = Path(tmp)
        for name, source in SCENARIOS.items():
            script = tmp_path / f"{name}.py"
            script.write_text(source, encoding="utf-8")
            element_count, durations = _time_runtime(script, args.repeat)
            print(
                f"{name}: elements={element_count} "
                f"median_ms={statistics.median(durations):.3f} "
                f"max_ms={max(durations):.3f} repeat={args.repeat}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
