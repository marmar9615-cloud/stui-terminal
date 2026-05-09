import stui as st

st.title("Training Dashboard")
st.caption("A compact terminal-native control panel.")

if "runs" not in st.session_state:
    st.session_state.runs = 0

model = st.selectbox("Model", ["resnet-mini", "transformer-lite", "mlp-debug"])
epochs = st.slider("Epochs", 1, 50, 8)
lr = st.number_input("Learning rate x1000", min_value=1, max_value=100, value=10)
augment = st.checkbox("Augmentation", value=True)

progress = min(st.session_state.runs * 20, 100)
st.progress(progress, text="latest run progress")

if st.button("Run training"):
    st.session_state.runs += 1
    st.success(f"Queued run {st.session_state.runs}")

st.subheader("Current settings")
st.table(
    {
        "setting": ["model", "epochs", "lr", "augment"],
        "value": [model, epochs, lr / 1000, augment],
    }
)

st.info("Use Tab to move focus, Enter to activate, q to quit.")
