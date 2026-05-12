import stui as st

st.title("Layouts")
st.caption("Terminal-native grouping with containers and static expanders.")

if "runs" not in st.session_state:
    st.session_state.runs = 2

mode = st.radio("Mode", ["fast", "balanced", "careful"], index=1)
priority = st.slider("Priority", 1, 5, 3)

with st.container():
    st.subheader("Overview")
    st.write("runs =", st.session_state.runs)
    st.progress(65, text="health")

with st.expander("Settings", expanded=True):
    st.write("mode =", mode)
    st.write("priority =", priority)

st.divider()
st.code(
    """with st.container():
    st.subheader("Overview")

with st.expander("Settings", expanded=True):
    st.write("mode =", mode)
""",
    language="python",
)
st.info("Expanders are static in v0.3.0; interactive toggling is deferred.")
