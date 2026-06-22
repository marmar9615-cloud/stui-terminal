import stui as st

st.title("Layouts")
st.caption(
    "Terminal-native columns, containers, and keyboard-toggleable expanders."
)

if "runs" not in st.session_state:
    st.session_state.runs = 2

mode = st.radio("Mode", ["fast", "balanced", "careful"], index=1)
priority = st.slider("Priority", 1, 5, 3)

left, middle, right = st.columns(3)
with left:
    st.subheader("Run")
    st.metric("Runs", st.session_state.runs, "+1")
    st.write("Mode:", mode)
with middle:
    st.subheader("Health")
    st.metric("Ready", "3/4", "+1")
    st.progress(65, text="health")
with right:
    st.subheader("Queue")
    st.metric("Priority", priority)
    st.progress(priority / 5, text="priority")

with st.container():
    st.subheader("Overview")
    st.write("runs =", st.session_state.runs)
    st.table(
        [
            {"stage": "queued", "count": 4},
            {"stage": "running", "count": 2},
            {"stage": "done", "count": st.session_state.runs},
        ],
        max_rows=3,
    )

with st.expander("Settings", expanded=True, key="layout-settings"):
    st.write("mode =", mode)
    st.write("priority =", priority)
    st.dataframe(
        {
            "setting": ["mode", "priority", "window"],
            "value": [mode, priority, "auto-stack"],
        },
        max_rows=3,
        max_cols=2,
    )

st.divider()
st.code(
    """left, middle, right = st.columns(3)
with left:
    st.metric("Runs", 2)
with middle:
    st.progress(0.65, text="health")
with right:
    st.progress(0.6, text="health")

with st.container():
    st.subheader("Overview")
    st.table([{"stage": "queued", "count": 4}])

with st.expander("Settings", expanded=True, key="layout-settings"):
    st.write("mode =", mode)
""",
    language="python",
)
st.info(
    "Columns stack in narrow terminals, including nested columns inside a "
    "parent column. Focus the expander and press Enter or Space to toggle it."
)
