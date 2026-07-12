import stui as st

st.title("Inputs")
st.caption("Small controls for terminal-first prototypes.")

name = st.text_input("Name", "MarMar")
notes = st.text_area(
    "Notes",
    "Compare the latest run\nagainst the baseline.",
    height=5,
    max_chars=500,
)
batch = st.number_input("Batch size", min_value=1, max_value=128, value=16, step=1)
model = st.selectbox("Model", ["tiny", "base", "large"], index=1)
mode = st.radio("Mode", ["fast", "balanced", "careful"], index=1)
datasets = st.multiselect("Datasets", ["train", "val", "test"], default=["train"])
enabled = st.checkbox("Enable dry run", value=True)
verbose = st.toggle("Verbose logs")
workspace = st.path_input(
    "Workspace",
    ".",
    kind="directory",
    must_exist=True,
    key="workspace",
)

if st.button("Apply"):
    st.toast("Settings applied")
    st.success("Settings applied")

st.write("name =", name)
st.write("notes =", notes)
st.write("batch =", batch)
st.write("model =", model)
st.write("mode =", mode)
st.write("datasets =", datasets)
st.write("dry run =", enabled)
st.write("verbose =", verbose)
st.write("workspace =", workspace)
