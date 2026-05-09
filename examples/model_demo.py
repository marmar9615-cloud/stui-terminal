import stui as st

st.title("Model demo")
st.info("Local deterministic demo. No model calls are made.")

if "runs" not in st.session_state:
    st.session_state.runs = 0

prompt = st.text_input("prompt", value="Summarize the deploy log")
streaming = st.checkbox("streaming", value=True)
temperature = st.slider("temperature", 0.0, 2.0, 0.7, 0.1)
context = st.slider("context tokens", 256, 4096, 1024, 256)
top_k = st.slider("top k", 1, 100, 40)

if st.button("Run sample"):
    st.session_state.runs += 1

st.divider()
st.header("Run settings")

st.write("runs =", st.session_state.runs)
st.write("prompt =", prompt)
st.write("streaming =", streaming)
st.write("temperature =", temperature)
st.write("context tokens =", context)
st.write("top k =", top_k)

creativity = round((temperature / 2.0) * 100)
budget = round((context / 4096) * 100)
focus = max(0, 100 - top_k)
stream_bonus = 5 if streaming else 0
score = min(100, round((creativity + budget + focus) / 3) + stream_bonus)

st.header("Deterministic score")
st.write("creativity score =", creativity)
st.write("context budget score =", budget)
st.write("focus score =", focus)
st.write("overall demo score =", score)

if score >= 70:
    st.success("Configuration looks balanced for the demo.")
else:
    st.warning("Try more context or a narrower top k for this demo.")
