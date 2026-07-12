import stui as st


@st.cache_data
def load_summary() -> dict[str, object]:
    return {"source": "local", "rows": 3, "status": "ready"}


st.title("Diagnostics-ready app")
st.write("This app is deterministic, offline, and safe to inspect.")
st.json(load_summary())
st.code("stui inspect examples/diagnostics.py --json")
st.code("stui check examples/diagnostics.py --strict --repeat 3")
st.caption("Ctrl+P opens the safe built-in command palette while the TUI runs.")
