import stui as st


def mark_changed(name: str) -> None:
    st.session_state.last_change = name


st.title("Kitchen Sink")
st.caption("One small app covering the stable stui 0.2 API surface.")

if "runs" not in st.session_state:
    st.session_state.runs = 0
if "last_change" not in st.session_state:
    st.session_state.last_change = "none"

st.header("Inputs")
project = st.text_input(
    "Project",
    value="stui",
    placeholder="Project name",
    key="project",
    on_change=mark_changed,
    args=("project",),
)
enabled = st.checkbox(
    "Enable preview",
    value=True,
    key="preview",
    on_change=mark_changed,
    args=("preview",),
)
batch = st.number_input(
    "Batch size",
    min_value=1,
    max_value=64,
    value=8,
    step=1,
    key="batch",
)
threshold = st.slider(
    "Confidence",
    min_value=0,
    max_value=100,
    value=70,
    step=5,
    key="confidence",
    help="Percent threshold for the summary.",
)
model = st.selectbox("Model", ["tiny", "base", "large"], index=1, key="model")
mode = st.radio("Mode", ["fast", "balanced", "careful"], index=1, key="mode")

if st.button("Record run", key="record"):
    st.session_state.runs += 1
    st.success(f"Recorded run {st.session_state.runs}")

if st.button("Refresh", key="refresh"):
    st.rerun()

st.divider()
st.subheader("Current Values")
st.write("project =", project)
st.text(f"preview = {enabled}")
st.markdown(f"**model**: {model} / **mode**: {mode}")
st.progress(threshold, text="confidence")

st.table(
    [
        {"metric": "batch", "value": batch},
        {"metric": "confidence", "value": f"{threshold}%"},
        {"metric": "runs", "value": st.session_state.runs},
    ]
)
st.dataframe(
    {
        "setting": ["project", "preview", "last change"],
        "value": [project, enabled, st.session_state.last_change],
    }
)
st.json(
    {
        "project": project,
        "preview": enabled,
        "batch": batch,
        "confidence": threshold,
        "model": model,
        "mode": mode,
    }
)
st.code(
    """if st.button("Record run"):
    st.session_state.runs += 1
""",
    language="python",
)

st.info("Use Tab to move between controls.")
st.success("Kitchen sink rendered successfully.")
st.warning("This example keeps all work local and deterministic.")
st.error("Example error message.")

try:
    raise ValueError("example exception")
except ValueError as exc:
    st.exception(exc)
