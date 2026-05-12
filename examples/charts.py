import stui as st

series = [3, 7, 5, 11, 8, 13]
rows = [
    {"step": index + 1, "score": score}
    for index, score in enumerate(series)
]

st.title("Charts")
st.caption("Small terminal-native summaries without plotting dependencies.")

st.metric("Latest score", series[-1], delta="+2")

st.subheader("Series")
st.bar_chart(series, width=24)

st.subheader("Named metrics")
st.bar_chart({"baseline": 3, "candidate": 7, "shipping": 13}, width=24)

st.subheader("Source rows")
st.table(rows)
st.progress(series[-1] / max(series), text="latest score")
st.code(
    """st.metric("Latest score", 13, delta="+2")
st.bar_chart([3, 7, 5, 11, 8, 13])
""",
    language="python",
)

st.markdown("Charts should be readable in a terminal and remain useful without color.")
