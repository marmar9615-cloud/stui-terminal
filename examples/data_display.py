import stui as st

st.title("Data Display")
st.caption("Tables do not require pandas, but pandas-like objects are supported.")

st.subheader("Runs")
st.table(
    [
        {"name": "baseline", "accuracy": 0.81, "latency_ms": 42},
        {"name": "quantized", "accuracy": 0.79, "latency_ms": 24},
        {"name": "distilled", "accuracy": 0.77, "latency_ms": 18},
    ]
)

st.subheader("Config")
st.json({"device": "mps", "batch_size": 16, "features": ["cache", "compile"]})

st.subheader("Snippet")
st.code(
    """for run in runs:
    evaluate(run)
""",
    language="python",
)
