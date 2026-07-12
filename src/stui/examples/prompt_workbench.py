import stui as st


@st.cache_data(max_entries=32)
def compile_prompt(instructions: str, tags: tuple[str, ...], concise: bool) -> str:
    style = "Answer concisely." if concise else "Explain the reasoning clearly."
    tag_line = ", ".join(tags) if tags else "none"
    return f"{instructions.strip()}\n\n{style}\nTags: {tag_line}"


@st.cache_resource
def local_model_profile() -> dict[str, str]:
    return {"model": "offline-demo", "runtime": "local"}


st.title("Prompt Workbench")
st.caption("Draft and inspect a local prompt without a browser or network call.")

instructions = st.text_area(
    "Instructions",
    value="Summarize the selected run and call out the largest regression.",
    height=7,
    key="instructions",
    placeholder="Write a multiline prompt...",
    max_chars=2000,
)
tags = st.multiselect(
    "Context",
    ["metrics", "logs", "errors", "latency"],
    default=["metrics", "errors"],
    key="context-tags",
)
concise = st.toggle("Concise response", value=True, key="concise")

compiled = compile_prompt(instructions, tags, concise)

if st.button("Prepare prompt"):
    st.toast("Prompt prepared locally")

preview, runtime = st.tabs(["Preview", "Runtime"], key="prompt-tabs")
with preview:
    st.code(compiled, language="text")
with runtime:
    st.json(local_model_profile())
st.caption("Ctrl+Enter commits the text area. Enter inserts a newline.")
