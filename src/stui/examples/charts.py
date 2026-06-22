import stui as st

series = [3, 7, 5, 11, 8, 13]
signed = [("baseline", -3), ("candidate", 7), ("zero", 0)]
column_data = {
    "step": [1, 2, 3, 4],
    "loss": [0.42, 0.31, 0.24, 0.18],
    "accuracy": [0.61, 0.68, 0.74, 0.8],
}
rows = [
    {"step": index + 1, "score": score}
    for index, score in enumerate(series)
]

st.title("Charts")
st.caption("Small terminal-native summaries without plotting dependencies.")

st.metric("Latest score", series[-1], delta="+2")

st.subheader("Series")
st.bar_chart(series, width=24)
st.line_chart(series, width=24)

st.subheader("Named metrics")
st.bar_chart({"baseline": 3, "candidate": 7, "shipping": 13}, width=24)

st.subheader("Signed compatibility shape")
st.bar_chart(signed, width=24)

st.subheader("Multiple lines")
st.line_chart(
    {
        "baseline": [2, 3, 4, 4, 5],
        "candidate": [3, 5, 6, 8, 13],
    },
    width=24,
)

st.subheader("Column-shaped data")
st.line_chart(column_data, width=24)

st.subheader("Source rows")
st.table(rows)
st.progress(series[-1] / max(series), text="latest score")
st.code(
    """st.metric("Latest score", 13, delta="+2")
st.bar_chart([3, 7, 5, 11, 8, 13])
st.bar_chart([("baseline", -3), ("candidate", 7), ("zero", 0)])
st.line_chart({"baseline": [2, 3, 4], "candidate": [3, 5, 8]})
st.line_chart({"step": [1, 2, 3], "loss": [0.42, 0.31, 0.24]})
""",
    language="python",
)

st.markdown("Charts should be readable in a terminal and remain useful without color.")
