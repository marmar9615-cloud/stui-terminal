# stui v0.2.2

`stui` v0.2.2 is a documentation and package-page polish patch.

## What changed

- Replaced the generated preview SVG with a real PNG screenshot captured from
  the terminal while running `examples/model_demo.py`.
- Updated the README preview image to use a versioned raw GitHub URL so the
  image renders correctly on PyPI.
- Included the PNG preview asset in the source distribution.

## What did not change

- No public API changes.
- No runtime behavior changes.
- No browser, server, websocket, or port-forwarding runtime code.
- No Streamlit dependency.
- No `textual-slider` dependency.

## Install

```bash
python -m pip install stui-terminal==0.2.2
```

## Quick check

```bash
python -c "import stui; print(stui.__version__)"
stui --version
```

