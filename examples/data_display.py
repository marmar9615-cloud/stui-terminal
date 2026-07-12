import stui as st

st.title("Data Display")
st.caption("Static terminal tables without a pandas dependency.")

st.subheader("Runs")
st.table(
    [
        {"name": "baseline", "accuracy": 0.81, "latency_ms": 42},
        {"name": "quantized", "accuracy": 0.79, "latency_ms": 24},
        {"name": "distilled", "accuracy": 0.77, "latency_ms": 18},
    ]
)

st.subheader("Interactive Rows")
selected = st.data_table(
    [
        {"name": "baseline", "accuracy": 0.81, "latency_ms": 42},
        {"name": "quantized", "accuracy": 0.79, "latency_ms": 24},
        {"name": "distilled", "accuracy": 0.77, "latency_ms": 18},
    ],
    selection_mode="single",
    key="selected-run",
    show_index=True,
)
if selected is not None:
    st.info(f"Selected source row {selected}")

st.subheader("Column Data")
st.dataframe(
    {
        "stage": ["queued", "running", "review", "done"],
        "jobs": [4, 2, 1, 8],
        "owner": ["cli", "model", "human", "release"],
    },
    max_rows=3,
    max_cols=2,
)

st.subheader("Object Rows")


class Run:
    def __init__(self, name, status, note):
        self.name = name
        self.status = status
        self.note = note


st.table(
    [
        Run("local", "ok", "line one\nline two"),
        Run("wheel", "ok", "fresh install"),
    ],
)

st.subheader("Config")
st.json({"device": "mps", "batch_size": 16, "features": ["cache", "compile"]})

st.subheader("Snippet")
st.code(
    """st.table([{"name": "baseline", "accuracy": 0.81}])
st.dataframe({"stage": ["queued", "done"], "jobs": [4, 8]}, max_rows=2)
""",
    language="python",
)

st.info("Static tables and selectable rows work without a dataframe dependency.")
