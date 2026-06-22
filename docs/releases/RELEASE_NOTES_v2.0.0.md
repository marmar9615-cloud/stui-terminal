# stui v2.0.0

`stui` v2.0.0 is the first v2 stable release. It is intentionally a contract,
documentation, packaging, and release-proof milestone rather than a risky
feature wave.

Install it from PyPI:

```bash
python -m pip install --upgrade stui-terminal==2.0.0
```

The package/import/CLI contract remains unchanged:

- PyPI distribution: `stui-terminal`
- Python import: `import stui as st`
- Console command: `stui`

## What Changed

- Finalized the v2 stable API contract from the v1.9.0 candidate.
- Kept the stable Python and CLI surface backward-compatible with v1.9.0.
- Kept `st.status`, `st.spinner`, and `st.help` public but experimental.
- Updated README, API docs, roadmap, release checklist, and readiness docs for
  the v2.0.0 release state.
- Release proof for this release includes local checks, clean wheel install,
  custom external project validation, GitHub CI, PyPI publish, GitHub Release,
  and fresh exact-version PyPI install.

## Stable API

The v2.0.0 stable API is the current documented `v1-stable` surface:

- Text: `st.title`, `st.header`, `st.subheader`, `st.caption`, `st.text`,
  `st.markdown`, `st.write`, `st.divider`, `st.code`
- Status outputs: `st.info`, `st.success`, `st.warning`, `st.error`,
  `st.exception`
- Display: `st.json`, `st.progress`, `st.table`, `st.dataframe`, `st.metric`,
  `st.bar_chart`, `st.line_chart`
- Inputs: `st.button`, `st.slider`, `st.text_input`, `st.checkbox`,
  `st.number_input`, `st.selectbox`, `st.radio`
- Forms and grouping: `st.form`, `st.form_submit_button`, `st.container`,
  `st.expander`, `st.columns`
- State and flow: `st.session_state`, `st.rerun`, `st.stop`
- Package metadata: `st.__version__`
- CLI: `stui run`, `stui check`, `stui demo`, `stui examples`,
  `stui example`, `stui init`, `stui doctor`, `stui selftest`,
  and `stui --version`

## Experimental APIs

These APIs remain public but experimental after v2.0.0:

- `st.status`
- `st.spinner`
- `st.help`

They are tested and documented, but their terminal formatting and grouping
semantics need more real use before they are frozen as stable.

## Deferred

The following remain outside the stable v2 surface: `st.empty`, `st.tabs`,
sidebar, file upload, caching, browser/server runtime, editable dataframes,
custom component embedding, heavy charting, and plotting-library parity.

## Upgrade Notes

No migration is required for apps using the v1.9.0 stable candidate API.
Apps using `st.status`, `st.spinner`, or `st.help` should continue to treat
those APIs as experimental.
