import stui as st

st.title("Counter")

if "count" not in st.session_state:
    st.session_state.count = 0

step = st.slider("step", 1, 10, 1)

if st.button("Increment"):
    st.session_state.count += step

if st.button("Decrement"):
    st.session_state.count -= step

if st.button("Reset"):
    st.session_state.count = 0

st.write("step =", step)
st.write("count =", st.session_state.count)
