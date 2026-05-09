import stui as st

st.title("Inputs")
st.caption("Small controls for terminal-first prototypes.")

name = st.text_input("Name", "MarMar")
batch = st.number_input("Batch size", min_value=1, max_value=128, value=16, step=1)
model = st.selectbox("Model", ["tiny", "base", "large"], index=1)
mode = st.radio("Mode", ["fast", "balanced", "careful"], index=1)
enabled = st.checkbox("Enable dry run", value=True)

if st.button("Apply"):
    st.success("Settings applied")

st.write("name =", name)
st.write("batch =", batch)
st.write("model =", model)
st.write("mode =", mode)
st.write("dry run =", enabled)
