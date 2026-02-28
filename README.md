## sv2 — Sembrando para el futuro

Educational accessibility app built with **Python + Pygame**.

## Requirements

- **Python 3.9**
- **Poetry** (1.5+ recommended)

## Install

Install dependencies with Poetry from the project root:

```bash
poetry install
```

This will create a virtualenv and install the runtime and dev dependencies declared in `pyproject.toml`.

## Run

Run the game using Poetry, from the project root (the script itself lives under `src/`):

```bash
poetry run python src/inicio.py
```

## Notes

- At runtime the code expects to find assets using paths relative to `src/` (for example `./iconos/...`).  
  Using `poetry run python src/inicio.py` from the project root keeps this behavior working as expected.
