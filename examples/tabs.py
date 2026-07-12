import stui as st

st.title("Tabbed workspace")

overview, details, settings = st.tabs(
    ["Overview", "Details", "Settings"],
    key="main-tabs",
)

with overview:
    st.metric("Runs", 12, "+2")
    st.success("Workspace ready")

with details:
    summary, raw = st.tabs(["Summary", "Raw"], key="detail-tabs")
    with summary:
        st.write("Every tab block executes; only the active pane is mounted.")
    with raw:
        st.json({"status": "ready", "runs": 12})

with settings:
    st.toggle("High confidence", value=True, key="confidence")

st.caption("Left and Right switch the focused tab. Ctrl+P opens commands.")
