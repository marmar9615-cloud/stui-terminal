import stui as st


@st.cache_data
def benchmark_rows():
    """Synthetic, repeatable data. No models or network calls."""
    return [
        {
            "run": f"{model}-b{batch}",
            "quality": round(78 + model_index * 2.7 - batch * 0.08, 2),
            "latency_ms": 8 + model_index * 11 + batch * 2,
            "tokens/s": round(960 / (model_index + 2) + batch * 3, 1),
            "status": "review" if (model_index + batch) % 3 == 0 else "ready",
            "notes": (
                f"{model} at batch {batch}. Synthetic local benchmark. "
                "Compare quality and latency before choosing a run; "
                "the explorer shows this entire note without cell truncation."
            ),
        }
        for model_index, model in enumerate(
            ["atlas-mini", "atlas-base", "cedar", "ember", "nova", "orbit"]
        )
        for batch in [1, 4, 8, 16]
    ]


rows = benchmark_rows()
st.title("Run lab")
st.caption("24 synthetic benchmarks. Focus the table and press F4 to explore.")

quality, latency, ready = st.columns(3)
with quality:
    st.metric("Best quality", max(row["quality"] for row in rows))
with latency:
    st.metric("Fastest run", f"{min(row['latency_ms'] for row in rows)} ms")
with ready:
    st.metric("Ready for review", sum(row["status"] == "ready" for row in rows))

runs, trends = st.tabs(["Runs", "Trends"], key="lab-tabs")
with runs:
    selected = st.data_table(
        rows,
        selection_mode="single",
        key="selected-run",
        height=9,
        show_index=True,
    )
    if selected is None:
        st.caption("F4 explores · Ctrl+F searches · F6 sorts · Enter selects")
    else:
        row = rows[selected]
        st.success(f"Selected {row['run']} · source row {selected}")
        with st.expander("Full selected record", expanded=True):
            st.json(row)

with trends:
    st.subheader("Quality across all runs")
    st.line_chart([row["quality"] for row in rows])
    st.subheader("Latency by run")
    st.bar_chart({row["run"]: row["latency_ms"] for row in rows[:8]})
    st.caption("These numbers are generated for this demo, not measured results.")
