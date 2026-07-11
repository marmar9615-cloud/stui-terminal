import stui as st


def mark_changed(name: str) -> None:
    st.session_state.last_change = name


st.title("Kitchen Sink")
st.caption("One small app covering stable APIs plus terminal primitives.")

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
notes = st.text_area(
    "Run notes",
    value="Compare the candidate\nwith the baseline.",
    height=5,
    key="run-notes",
    max_chars=1000,
    on_change=mark_changed,
    args=("run notes",),
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
datasets = st.multiselect(
    "Datasets",
    ["train", "val", "test"],
    default=["train"],
    key="datasets",
)
verbose = st.toggle("Verbose logs", key="verbose")

if st.button("Record run", key="record"):
    st.session_state.runs += 1
    st.toast(f"Recorded run {st.session_state.runs}")
    st.success(f"Recorded run {st.session_state.runs}")

if st.button("Refresh", key="refresh"):
    st.rerun()

st.divider()
st.subheader("Current Values")
st.write("project =", project)
st.write("notes =", notes)
st.text(f"preview = {enabled}")
st.write("datasets =", datasets)
st.text(f"verbose = {verbose}")
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

st.divider()
st.subheader("Terminal primitives")

with st.form("kitchen-form"):
    st.text_area("Form note", "batched\nupdate", height=4)
    form_submitted = st.form_submit_button("Submit form")
if form_submitted:
    st.success("Form submitted")

with st.container():
    st.metric("Runs", st.session_state.runs, delta="+1" if form_submitted else None)
    st.bar_chart([1, 3, 2, 5], width=20)

st.status("Validation complete", state="complete")
with st.status("Visible grouped status", state="running", expanded=True):
    st.text("Status children render when expanded=True.")

with st.spinner("Static spinner block"):
    st.text("Spinner children are grouped under the spinner panel.")

st.help(st.progress)

with st.expander("Primitive snippets", expanded=True):
    st.code(
        """with st.form("settings"):
    name = st.text_input("Name")
    submitted = st.form_submit_button("Apply")

with st.container():
    st.metric("Runs", 3)
    st.bar_chart([1, 3, 2, 5])

with st.status("Visible details", expanded=True):
    st.write("Children render when expanded=True")

with st.spinner("Working"):
    st.write("Static progress grouping")
""",
        language="python",
    )
