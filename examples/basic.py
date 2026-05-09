import stui as st

st.title("stui demo")

if "count" not in st.session_state:
    st.session_state.count = 0

x = st.slider("x", 0, 100, 10)

if st.button("Increment"):
    st.session_state.count += 1

st.write("x =", x)
st.write("count =", st.session_state.count)
