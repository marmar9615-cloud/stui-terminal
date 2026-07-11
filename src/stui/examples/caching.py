import stui as st


@st.cache_data(ttl=60, max_entries=16)
def load_rows(dataset: str) -> list[dict[str, object]]:
    return [
        {"dataset": dataset, "run": "baseline", "score": 0.82},
        {"dataset": dataset, "run": "tuned", "score": 0.91},
    ]


@st.cache_resource
def load_model() -> dict[str, str]:
    return {"name": "local-demo", "device": "cpu"}


st.title("Caching")
st.caption("Process-local data copies and reusable resource identity.")

dataset = st.selectbox("Dataset", ["validation", "test"])
rows = load_rows(dataset)
model = load_model()

# Each cache_data hit restores an independent value. Mutating this probe does
# not poison the value returned to the app below.
probe = load_rows(dataset)
probe[0]["score"] = -1
fresh_rows = load_rows(dataset)

st.table(rows)
st.json(model)
st.write("data copy isolated =", fresh_rows[0]["score"] == rows[0]["score"])
st.write("resource identity reused =", load_model() is model)

if st.button("Clear data cache"):
    load_rows.clear()
    st.toast("Data cache cleared")

if st.button("Clear resource cache"):
    load_model.clear()
    st.toast("Resource cache cleared")

st.info("Cached entries live only for this app process.")
