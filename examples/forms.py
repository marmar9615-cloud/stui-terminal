import stui as st

st.title("Forms")
st.caption("Group related inputs and apply them with one submit button.")

if "submitted_runs" not in st.session_state:
    st.session_state.submitted_runs = 0

with st.form("run-settings"):
    project = st.text_input("Project", "stui")
    batch_size = st.number_input("Batch size", min_value=1, max_value=128, value=16)
    dry_run = st.checkbox("Dry run", value=True)
    submitted = st.form_submit_button("Apply settings")

if submitted:
    st.session_state.submitted_runs += 1
    st.success(f"Applied settings for {project}")

st.write("project =", project)
st.write("batch size =", batch_size)
st.write("dry run =", dry_run)
st.progress(min(st.session_state.submitted_runs * 25, 100), text="submitted runs")
st.info("MVP note: widgets still update session_state before submit.")
