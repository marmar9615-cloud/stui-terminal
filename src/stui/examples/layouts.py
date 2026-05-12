import stui as st

st.title("Layouts")
st.caption(
    "Terminal-native columns, containers, and keyboard-toggleable expanders."
)

if "runs" not in st.session_state:
    st.session_state.runs = 2

mode = st.radio("Mode", ["fast", "balanced", "careful"], index=1)
priority = st.slider("Priority", 1, 5, 3)

left, right = st.columns(2)
with left:
    st.subheader("Run")
    st.metric("Runs", st.session_state.runs, "+1")
    st.write("Mode:", mode)
with right:
    st.subheader("Queue")
    st.metric("Priority", priority)
    st.progress(priority / 5, text="priority")

with st.container():
    st.subheader("Overview")
    st.write("runs =", st.session_state.runs)
    st.progress(65, text="health")

with st.expander("Settings", expanded=True):
    st.write("mode =", mode)
    st.write("priority =", priority)

st.divider()
st.code(
    """left, right = st.columns(2)
with left:
    st.metric("Runs", 2)
with right:
    st.progress(0.6, text="health")

with st.container():
    st.subheader("Overview")

with st.expander("Settings", expanded=True):
    st.write("mode =", mode)
""",
    language="python",
)
st.info("Focus the expander and press Enter or Space to toggle it.")
