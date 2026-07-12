import stui as st


@st.cache_data
def load_rows() -> list[dict[str, object]]:
    return [
        {"name": "alpha", "score": 91, "status": "ready"},
        {"name": "beta", "score": 87, "status": "review"},
        {"name": "gamma", "score": 82, "status": "ready"},
    ]


st.title("Local workspace")
st.caption("Run `stui inspect examples/workspace.py` for structural diagnostics.")

overview, data, files = st.tabs(
    ["Overview", "Data", "Files"],
    key="workspace-tabs",
)

with overview:
    st.metric("Rows", len(load_rows()), "+3")
    st.text_area("Notes", "Review the local run.", key="workspace-notes")
    st.multiselect(
        "Visible states",
        ["ready", "review", "blocked"],
        default=["ready", "review"],
        key="visible-states",
    )

with data:
    selected = st.data_table(
        load_rows(),
        selection_mode="single",
        key="selected-row",
        show_index=True,
    )
    if selected is not None:
        st.info(f"Selected source row {selected}")

with files:
    path = st.path_input(
        "Workspace path",
        ".",
        kind="directory",
        must_exist=True,
        key="workspace-path",
    )
    st.caption(path)
    if st.button("Confirm path", key="confirm-path"):
        st.toast("Path selection committed")
