from data_loader import load_rows
from helpers import format_summary

import stui as st

if "runs" not in st.session_state:
    st.session_state.runs = 0

st.title("Watch Project")
st.caption("Edit helpers.py while this app is running with --watch.")

rows = load_rows("sample_data.json")
st.table(rows)
st.write(format_summary(rows))

if st.button("Count run"):
    st.session_state.runs += 1
    st.toast(f"Run {st.session_state.runs}")

st.metric("Interactive runs", st.session_state.runs)
