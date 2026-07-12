import stui as st

ROWS = [
    {"run": "alpha", "score": 0.91, "status": "ready"},
    {"run": "beta", "score": 0.87, "status": "review"},
    {"run": "gamma", "score": 0.82, "status": "ready"},
]

st.title("Data explorer")
st.metric("Local rows", len(ROWS))

selected = st.data_table(
    ROWS,
    selection_mode="single",
    key="selected-run",
    show_index=True,
    max_cols=3,
)

if selected is None:
    st.info("Choose a row with Enter, Space, or the mouse.")
else:
    st.subheader("Selected record")
    st.json(ROWS[selected])

with st.expander("Static comparison"):
    st.table(ROWS, max_rows=3, max_cols=3)
