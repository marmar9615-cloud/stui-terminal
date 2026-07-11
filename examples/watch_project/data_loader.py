import json
from pathlib import Path

import stui as st


@st.cache_data(max_entries=8)
def load_rows(path: str) -> list[dict[str, object]]:
    source = Path(__file__).with_name(path)
    return json.loads(source.read_text(encoding="utf-8"))
